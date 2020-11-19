import uuid
import os
import hashlib
from datetime import datetime
from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property

from model_utils.fields import MonitorField, StatusField
from model_utils import Choices, FieldTracker


from ctftools.settings import (
    HEDGEDOC_URL,
    CTF_CHALLENGE_FILE_PATH,
    CTF_CHALLENGE_FILE_ROOT,
    USERS_FILE_PATH,
)
from ctfpad.validators import challenge_file_max_size_validator
from ctfpad.helpers import register_new_hedgedoc_user, create_new_note, get_file_magic, get_file_mime


# Create your models here.

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    creation_time = models.DateTimeField(auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(TimeStampedModel):
    """
    CTF team model
    """
    name = models.CharField(max_length=64)
    email = models.EmailField(max_length=256, unique=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    blog_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=128)
    avatar = models.ImageField(blank=True, upload_to=USERS_FILE_PATH)

    def save(self):
        if not self.api_key:
            self.api_key = get_random_string(128)
        super(Team, self).save()
        return


class Member(TimeStampedModel):
    """
    CTF team member model
    """
    COUNTRIES = Choices("", "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","The Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo, Republic of the","Congo, Democratic Republic of the","Costa Rica","Cote d'Ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","East Timor (Timor-Leste)","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Fiji","Finland","France","Gabon","The Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Korea, North","Korea, South","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia, Federated States of","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar (Burma)","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Palau","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States of America","Uruguay","Uzbekistan","Vanuatu","Vatican City (Holy See)","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe")
    TIMEZONES = Choices("UTC", "UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1", "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10", "UTC+11", "UTC+12")

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    avatar = models.ImageField(blank=True, upload_to=USERS_FILE_PATH)
    description = models.TextField(blank=True)
    country = StatusField(choices_name='COUNTRIES')
    timezone = StatusField(choices_name='TIMEZONES')
    last_scored = models.DateTimeField(null=True)
    show_pending_notifications = models.BooleanField(default=False)
    last_active_notification = models.DateTimeField(null=True)
    hedgedoc_password = models.CharField(max_length=64, null=True)

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def has_superpowers(self):
        return self.user.id == 1 # todo: when perm added, use self.user.is_superuser

    def __str__(self):
        return self.username


    @cached_property
    def best_category(self) -> str:
        best_categories_by_point = Challenge.objects.filter(
            solver = self,
        ).values("category").annotate(
            dcount=Sum("points")
        ).order_by(
            "-points"
        )
        print(best_categories_by_point)
        if best_categories_by_point.count() == 0:
            return ""
        best_category_id = best_categories_by_point.first()["category"]
        return ChallengeCategory.objects.get(pk=best_category_id)


    @property
    def total_points_scored(self):
        challenges = Challenge.objects.filter(
            solver = self,
        )
        return challenges.aggregate(Sum("points"))["points__sum"] or 0


    @property
    def last_logged_in(self):
        return self.user.last_login

    @property
    def hedgedoc_username(self):
        return f"{self.username}@ctfpad"

    def save(self):
        if not self.hedgedoc_password:
            # create the hedgedoc user
            self.hedgedoc_password = get_random_string(64)
            if not register_new_hedgedoc_user(self.hedgedoc_username, self.hedgedoc_password):
                # password empty == anonymous mode under HedgeMd
                self.hedgedoc_password = ""

        super(Member, self).save()
        return


class Ctf(TimeStampedModel):
    """
    CTF model class
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    flag_prefix = models.CharField(max_length=64, blank=True)
    team_login = models.CharField(max_length=128, blank=True)
    team_password = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def is_permanent(self) -> bool:
        return self.start_date is None and self.end_date is None

    @property
    def challenges(self):
        return self.challenge_set.all()

    @property
    def solved_challenges(self):
        return self.challenge_set.filter(status = "solved")

    @property
    def unsolved_challenges(self):
        return self.challenge_set.filter(status = "unsolved")

    @property
    def solved_challenges_as_percent(self):
        l = self.challenges.count()
        if l == 0: return 0
        return int(float(self.solved_challenges.count() / l) * 100)

    @property
    def total_points(self):
        return self.challenges.aggregate(Sum("points"))["points__sum"] or 0

    @property
    def scored_points(self):
        return self.solved_challenges.aggregate(Sum("points"))["points__sum"] or 0

    @property
    def scored_points_as_percent(self):
        if self.total_points == 0: return 0
        return int(float(self.scored_points / self.total_points) * 100)

    @property
    def duration(self):
        if self.is_permanent: return 0
        return self.end_date - self.start_date

    @property
    def is_running(self):
        now = datetime.now()
        return self.start_date <= now < self.end_date



class ChallengeCategory(TimeStampedModel):
    """
    CTF challenge category model

    The category for a specific challenge. This approach is better than using choices because
    we can't predict all existing categories for CTFs.
    """
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Challenge(TimeStampedModel):
    """
    CTF challenge model
    """
    STATUS = Choices('unsolved', 'solved', )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    points = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ChallengeCategory, on_delete=models.DO_NOTHING, null=True)
    note_id = models.CharField(max_length=80, blank=True)
    ctf = models.ForeignKey(Ctf, on_delete=models.CASCADE)
    last_update_by = models.ForeignKey(Member, on_delete=models.DO_NOTHING, null=True, related_name='last_updater')
    flag = models.CharField(max_length=128, blank=True)
    flag_tracker = FieldTracker(fields=['flag',])
    status = StatusField()
    solver = models.ForeignKey(Member, on_delete=models.DO_NOTHING, null=True, related_name='solver')
    solved_time = MonitorField(monitor='status', when=['solved',])

    @property
    def solved(self) -> bool:
        return self.status == "solved"

    @property
    def note_url(self) -> str:
        note_id = self.note_id or "/"
        return f"{HEDGEDOC_URL}{note_id}"

    def save(self):
        if not self.note_id:
            self.note_id = create_new_note()

        if self.flag_tracker.has_changed("flag"):
            self.status = "solved"
            self.solver = self.last_update_by
            self.solved_time = datetime.now()

        super(Challenge, self).save()
        return



class ChallengeFile(TimeStampedModel):
    """
    CTF file model, for a file associated with a challenge
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(null=True, upload_to=CTF_CHALLENGE_FILE_PATH, validators=[challenge_file_max_size_validator,])
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    mime = models.CharField(max_length=128)
    type = models.CharField(max_length=512)
    hash = models.CharField(max_length=64) # sha256 -> 32*2

    @property
    def name(self):
        return os.path.basename(self.file.name)

    @property
    def size(self):
        return self.file.size

    def save(self):
        # save() to commit files to proper location
        super(ChallengeFile, self).save()

        # update missing properties
        p = Path(CTF_CHALLENGE_FILE_ROOT) / self.name
        if p.exists():
            abs_path = str(p.absolute())
            if not self.mime: self.mime = get_file_mime(p)
            if not self.type: self.type = get_file_magic(p)
            if not self.hash: self.hash = hashlib.sha256( open(abs_path, "rb").read() ).hexdigest()
            super(ChallengeFile, self).save()

        return



class ChallengeWriteup(TimeStampedModel):
    """
    CTF challenge write-up model
    """
    url = models.CharField(max_length=2048)
    added_by = models.ForeignKey(Member, on_delete=models.PROTECT)
    challenge = models.ForeignKey(Challenge, on_delete=models.PROTECT)


class Notification(TimeStampedModel):
    """
    Internal notification system
    """
    sender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_sender")
    recipient = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_recipient", blank=True) # if blank -> broadcast
    description = models.TextField()
    challenge = models.ForeignKey(Challenge, on_delete=models.DO_NOTHING, blank=True)


class CtfStats:
    """
    Statistic collection class
    """
    pass