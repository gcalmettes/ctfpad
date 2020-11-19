import pathlib
import magic
import requests
from uuid import uuid4

from ctftools.settings import (
    HEDGEDOC_URL,
    CTFTIME_API_EVENTS_URL,
)


def register_new_hedgedoc_user(username: str, password: str) -> bool:
    """Register the member in hedgedoc. If fail, the member will be
    seen as anonymous.

    Args:
        username (str): member HedgeDoc username
        password (str): member HedgeDoc password

    Returns:
        bool: if the register action succeeded, returns True; False in any other cases
    """
    res = requests.post(
        f'{HEDGEDOC_URL}/register',
        data={'email': username, 'password': password},
        allow_redirects = False
    )

    if res.status_code != requests.codes.found:
        return False

    return True


def create_new_note() -> str:
    """"Returns a unique note ID so that the note will be automatically created when accessed for the first time

    Returns:
        str: the string ID of the new note
    """
    return f"/{uuid4()}"


def check_note_id(id: str) -> bool:
    """"Checks if a specific note exists from its ID.

    Args:
        id (str): the identifier to check

    Returns:
        bool: returns True if it exists
    """
    res = requests.head( f"{HEDGEDOC_URL}/{id}" )
    return res.status_code == requests.codes.found



def get_file_magic(fpath: pathlib.Path) -> str:
    """Returns the file description from its magic number (ex. 'PE32+ executable (console) x86-64, for MS Windows' )

    Args:
        fpath (pathlib.Path): path object to the file

    Returns:
        str: the file description, or "" if the file doesn't exist on FS
    """
    abspath = str(fpath.absolute())
    return magic.from_file(abspath) if fpath.exists() else "Data"



def get_file_mime(fpath: pathlib.Path) -> str:
    """Returns the mime type associated to the file (ex. 'appication/pdf')

    Args:
        fpath (pathlib.Path): path object to the file

    Returns:
        str: the file mime type, or "application/octet-stream" if the file doesn't exist on FS
    """
    abspath = str(fpath.absolute())
    return magic.from_file(abspath, mime=True) if fpath.exists() else "application/octet-stream"



def ctftime_fetch_next_ctf_data() -> list:
    """Retrieve the next CTFs from CTFTime API

    Returns:
        list: JSON output of the upcoming CTFs of the output from CTFTime
    """
    try:
        res = requests.get(CTFTIME_API_EVENTS_URL, headers={"user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"})
        if res.status_code != requests.codes.ok:
            raise RuntimeError(f"CTFTime service returned HTTP code {res.status_code} (expected {requests.codes.ok}): {res.reason}")
        result = res.json()
    except Exception:
        result = []
    return result
