# Copyright 2023 Luma AI, Inc
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import shutil
from typing import Optional, List, Dict
import uuid
import urllib.parse
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import time
import json
import requests

import fire
import platformdirs


CACHE_DIR = platformdirs.user_config_dir("luma")
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


class LumaClient:
    """
    Luma API Python Client.
    Currently limited to basic video/zip/folder uploads
    and status checking.

    Library usage: :code:`from lumaapi import LumaClient`

    CLI usage:

    To submit a video
    :code:`luma submit <video> <title>`
    This outputs a slug.

    To check status of the capture
    :code:`luma status <slug>`

    To search user's captures
    :code:`luma get <title>`

    To manually authenticate
    (the CLI automatically prompts for api-key when running anything else)
    :code:`luma auth`

    To check for credits
    :code:`luma credits`
    """
    def __init__(self, api_key: Optional[str] = None):
        if api_key is not None:
            self.auth(api_key)


    def credits(self) -> LumaCreditInfo:
        """
        :code:`luma credits`
        Get number of credits remaining for the user.

        :return: LumaCreditInfo
        """
        auth_headers = self.auth()
        response = requests.get(f"{API_BASE_URL}capture/credits", headers=auth_headers)
        response.raise_for_status()
        data = response.json()
        return LumaCreditInfo(**data)


    def auth(self, api_key: Optional[str] = None):
        """
        :code:`luma auth`, :code:`luma auth <api-key>`
        Update the api_key to the provided api_key.
        Alternatively, if api_key is not given, load the cached API key,
        or ask the user to enter it
        If api_key is updated, runs client.credits() to check its validity.

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

            print("Verifying api-key...")
            # Check it by getting credits
            try:
                self.credits()
            except Exception as ex:
                print("401 invalid API key, please obtain one from https://captures.lumalabs.ai/dashboard")
                os.remove(AUTH_FILE)
                raise ex

        return result


    def clear_auth(self):
        """
        :code:`luma clear_auth`
        Remove cached authorization (client.auth()) if present
        """
        if os.path.isfile(AUTH_FILE):
            os.remove(AUTH_FILE)


    def submit(self,
               path: str,
               title: str,
               cam_model: CameraType = CameraType.NORMAL,
               silent: bool = False,
           ) -> str:
        """
        :code:`luma submit <path> <title>`
        Submit a video, zip, or directory (at path) to Luma for processing, with given title.
        User might be prompted for API key, if not already authenticated (call auth).
        Returns the slug. After submissing, use status(slug) to check the status
        and output artifacts.

        :param path: str, path to video, zip of images, zip of multiple videos, or directory (with images) to submit
        :param title: str, a descriptive title for the capture
        :param cam_model: CameraType, camera model
        :param silent: bool, if True, do not print progress

        :return: str, the slug identifier for checking the status etc
        """
        tmp_path = None
        if os.path.isdir(path):
            path = path.rstrip("/").rstrip("\\")
            tmp_path = os.path.join(os.path.dirname(path),
                                    uuid.uuid4().hex)
            if not silent:
                print("Compressing directory", path, "to", tmp_path + ".zip")
            path = shutil.make_archive(tmp_path, 'zip', path)
            if not silent:
                print("Compressed to", path)

        with open(path, "rb") as f:
            payload = f.read()
        result = self.submit_binary(payload, title,
                           cam_model=cam_model,
                           silent=silent)
        if tmp_path is not None and os.path.isfile(tmp_path):
            os.remove(tmp_path)
        return result

    def submit_binary(self,
               payload: bytes,
               title: str,
               cam_model: CameraType = CameraType.NORMAL,
               silent: bool = False,
           ) -> str:
        """
        (Python only)
        Submit a video or zip (as binary blob) to Luma for processing, with given title.
        User might be prompted for API key, if not already authenticated (call auth).
        Returns the slug. After submissing, use status(slug) to check the status
        and output artifacts.

        :param payload: bytes,
        :param title: str, a descriptive title for the capture
        :param cam_model: CameraType, camera model

        :return: str, the slug identifier for checking the status etc
        """
        auth_headers = self.auth()

        # 1. Create capture
        capture_data = {
            'title': title,
            'camModel': cam_model.value,
        }
        if not silent:
            print("Capture data", capture_data)
        response = requests.post(f"{API_BASE_URL}capture",
                                 headers=auth_headers, data=capture_data)
        response.raise_for_status()
        capture_data = response.json()
        upload_url = capture_data['signedUrls']['source']
        slug = capture_data['capture']['slug']
        if not silent:
            print("Created capture", slug)
            print("Uploading")

        # 2. Upload video or zip
        response = requests.put(upload_url, headers={'Content-Type': 'text/plain'}, data=payload)
        response.raise_for_status()

        time.sleep(0.5)
        if not silent:
            print("Triggering")

        # 3. Trigger processing
        response = requests.post(f"{API_BASE_URL}capture/{slug}", headers=auth_headers)
        response.raise_for_status()

        if not silent:
            print("Submitted", slug)
        return slug


    def status(self, slug: str) -> LumaCaptureInfo:
        """
        :code:`luma status <slug>`
        Check the status of a submitted capture

        :param slug: str, slug of capture to check (from submit())

        :return: LumaCaptureInfo dataclass
        """
        auth_headers = self.auth()
        response = requests.get(f"{API_BASE_URL}capture/{slug}", headers=auth_headers)
        response.raise_for_status()
        data = response.json()
        return LumaCaptureInfo.from_dict(data)


    def get(self,
            query: str="",
            skip : int=0,
            take : int=50,
            desc : bool = True) -> List[LumaCaptureInfo]:
        """
        :code:`luma get <query>`
        Find captures from all of the user's API captures

        :param query: str, query string to filter captures by (title)
        :param skip: int, starting capture index
        :param take: int, number of captures to take
        :param desc: bool, whether to sort in descending order

        :return: list of LumaCaptureInfo dataclass
        """
        auth_headers = self.auth()
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
    fire.Fire(LumaClient)
