# Luma API
# Copyright 2022 Luma AI

import os
from typing import Optional, List, Dict
import urllib.parse
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import time
import json
import requests
import fire


CACHE_DIR = os.path.join(os.path.expanduser("~"), ".lumaapi")
AUTH_FILE = os.path.join(CACHE_DIR, "auth.json")
API_BASE_URL = "https://webapp.engineeringlumalabs.com/api/v2/"


@dataclass
class LumaCreditInfo:
    """
    Response of credits query
    """
    remaining: int
    """ Number of remaining credits """

    used: int
    """ Number of used credits """

    total: int
    """ Number of remaining+used credits """

class CaptureType(Enum):
    """
    Capture types.
    Current API version always has RECONSTRUCTION type
    (generation API not yet available for public)
    """
    RECONSTRUCTION = 0
    GENERATION = 1

    @classmethod
    def parse(cls, name: str) -> "CaptureType":
        return getattr(cls, name.upper(), None)

class CameraType(Enum):
    """
    Camera types
    """
    NORMAL = "normal"
    """ Perspective camera """
    FISHEYE = "fisheye"
    """ Fisheye camera """
    EQUIRECTANGULAR = "equirectangular"
    """ Equirectangular 360 camera """

    @classmethod
    def parse(cls, name: str) -> "CameraType":
        return getattr(cls, name.upper(), None)


class PrivacyLevel(Enum):
    """
    Privacy levels for capture
    """
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"
    OPEN = "open"

    @classmethod
    def parse(cls, name: str) -> "PrivacyLevel":
        return getattr(cls, name.upper(), None)

class CaptureStatus(Enum):
    """
    Run status
    """
    NEW = 0
    UPLOADING = 0
    COMPLETE = 1

    @classmethod
    def parse(cls, name: str) -> "CaptureStatus":
        return getattr(cls, name.upper(), None)

@dataclass
class CaptureLocation:
    latitude: float = 0.0
    longitude: float = 0.0
    name: str = ""
    is_visible: bool = True

    @classmethod
    def from_dict(cls, data: Dict) -> "CaptureLocation":
        return cls(
                latitude=data.get("latitude", 0.0),
                longitude=data.get("longitude", 0.0),
                name=data.get("name", ""),
                is_visible=data.get("is_visible", True))

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "name": self.name,
            "isVisible": self.is_visible
        }


class RunStatus(Enum):
    """
    Run status
    """
    NEW = 0
    DISPATCHED = 1
    FAILED = 2
    FINISHED = 3

    @classmethod
    def parse(cls, name: str) -> "RunStatus":
        return getattr(cls, name.upper(), None)


@dataclass
class LumaRunInfo:
    status: RunStatus

    progress: int
    """ Percentage progress (0-100) """

    current_stage: str
    """ Current stage of reconstruction for information. Examples are sfm and nerf """

    artifacts: List[Dict[str, str]]

@dataclass
class LumaCaptureInfo:
    title: str
    """ Capture title """
    type: CaptureType
    """ Capture type. This will currently be reconstruction """
    location: Optional[CaptureLocation]
    """ Location of capture. For API captures, this will be None """
    privacy: PrivacyLevel
    """ Capture privacy level """
    date: datetime
    """ Capture creation time """
    username: str
    """ Username of submitting user """
    status: CaptureStatus
    """ Capture upload status """
    latest_run: Optional[LumaRunInfo]

    @classmethod
    def from_dict(cls, data: Dict) -> "LumaCaptureInfo":
        lrun = data.get("latestRun", None)
        return LumaCaptureInfo(
            title=data["title"],
            type=CaptureType.parse(data["type"]),
            location=CaptureLocation.from_dict(data["location"]) if data["location"] is not None else None,
            privacy=PrivacyLevel.parse(data["privacy"]),
            date=datetime.fromisoformat(data["date"][:-1] + '+00:00'),
            username=data["username"],
            status=CaptureStatus.parse(data["status"]),
            latest_run=LumaRunInfo(
                    status=RunStatus.parse(lrun["status"]),
                    progress=lrun["progress"],
                    current_stage=lrun["currentStage"],
                    artifacts=lrun["artifacts"],
                ) if lrun is not None else None
        )


def get_credits() -> LumaCreditInfo:
    """
    Get number of credits remaining for the user.

    :return: LumaCreditInfo
    """
    auth_headers = auth()
    response = requests.get(f"{API_BASE_URL}capture/credits", headers=auth_headers)
    response.raise_for_status()
    data = response.json()
    return LumaCreditInfo(**data)


def auth(api_key: Optional[str] = None):
    """
    Update the api_key to the provided api_key.
    Alternatively, if api_key is not given, load the cached API key,
    or ask the user to enter it
    If api_key is updated, runs get_credits to check its validity.

    :param api_key: str, optional, API key to use instead of prompting user
    :return: dict, headers to use for authenticated requests (:code:`Authorization: luma-pai-key=<api_key>`)
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    if api_key is None and os.path.isfile(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            result = json.load(f)
    else:
        # Prompt user for API key
        if api_key is None:
            api_key = input("Enter your Luma API key (get from https://captures.lumalabs.ai/dashboard): ").strip()
        with open(AUTH_FILE, "w") as f:
            result = {"Authorization": 'luma-api-key=' + api_key}
            json.dump(result, f)

        # Check it by getting credits
        try:
            get_credits()
        except Exception as ex:
            print("401 invalid API key, please obtain one from https://captures.lumalabs.ai/dashboard")
            os.remove(AUTH_FILE)
            raise ex

    return result


def clear_auth():
    """
    Remove cached authorization (auth()) if present
    """
    if os.path.isfile(AUTH_FILE):
        os.remove(AUTH_FILE)


def submit(path: str,
           title: str,
           privacy: PrivacyLevel = PrivacyLevel.PRIVATE,
           location: Optional[CaptureLocation] = None,
           cam_model: CameraType = CameraType.NORMAL,
       ) -> str:
    """
    Submit a video or image to Luma for processing, with given title.
    User might be prompted for API key, if not already authenticated (call auth).
    Returns the slug. After submissing, use status(slug) to check the status
    and output artifacts.

    :param path: str, path to video or zip of images or zip of multiple videos to submit
    :param title: str, a descriptive title for the capture
    :param privacy: PrivacyLevel, privacy level for the capture
    :param location: str, location of capture
    :param cam_model: CameraType, camera model

    :return: str, the slug identifier for checking the status etc
    """

    assert os.path.isfile(path), "File not found: " + path
    auth_headers = auth()

    # 1. Create capture
    capture_data = {
        'title': title,
        'privacy': privacy.value,
        'camModel': cam_model.value,
    }
    if location is not None:
        capture_data['location'] = location.to_dict()
    response = requests.post(f"{API_BASE_URL}capture", headers=auth_headers, data=capture_data)
    response.raise_for_status()
    capture_data = response.json()
    upload_url = capture_data['signedUrls']['source']
    slug = capture_data['capture']['slug']

    with open(path, "rb") as f:
        payload = f.read()

    # 2. Upload video or zip
    response = requests.put(upload_url, headers={'Content-Type': 'text/plain'}, data=payload)
    response.raise_for_status()

    time.sleep(0.5)

    # 3. Trigger processing
    response = requests.post(f"{API_BASE_URL}capture/{slug}", headers=auth_headers)
    response.raise_for_status()
    return slug


def status(slug: str) -> LumaCaptureInfo:
    """
    Check the status of a submitted capture

    :param slug: str, slug of capture to check (from submit())

    :return: LumaCaptureInfo dataclass
    """
    auth_headers = auth()
    response = requests.get(f"{API_BASE_URL}capture/{slug}", headers=auth_headers)
    response.raise_for_status()
    data = response.json()
    return LumaCaptureInfo.from_dict(data)


def get(query: str="",
        skip : int=0,
        take : int=50,
        desc : bool = True) -> List[LumaCaptureInfo]:
    """
    Get a range of captures from all of the user's captures

    :param query: str, query string to filter captures by (title)
    :param skip: int, starting capture index
    :param take: int, number of captures to take
    :param desc: bool, whether to sort in descending order

    :return: list of LumaCaptureInfo dataclass
    """
    auth_headers = auth()
    query = urllib.parse.quote(query)
    skip = int(skip)
    take = int(take)
    order = "DESC" if desc else "ASC"
    url = f"{API_BASE_URL}capture?"
    if query:
        url += f"search={query}&"
    response = requests.get(url + f"skip={skip}&take={take}&order={order}",
                            headers=auth_headers)
    response.raise_for_status()
    data = response.json()
    return [LumaCaptureInfo.from_dict(x) for x in data["captures"]]


if __name__ == '__main__':
    fire.Fire()
