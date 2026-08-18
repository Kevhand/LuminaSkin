# Requirements: Python >= 3.10 (for f-strings), requests >= 2.20.0
# 1. Starts an async task
# 2. Polls until the task status becomes success or error
import requests
import time
import json
import os
import mimetypes
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_URL = 'https://yce-api-01.makeupar.com/s2s/v2.1/task/skin-analysis'
FILE_UPLOAD_URL = "https://yce-api-01.makeupar.com/s2s/v2.0/file/skin-analysis"
START_METHOD = 'POST'
HEADERS = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {os.getenv('API_KEY')}"
}

def intialize_upload(image_path):
  file_size = os.path.getsize(image_path)
  file_name = os.path.basename(image_path)

  data = {
    "files":[
      {
        "content_type": mimetypes.guess_type(image_path)[0] or "image/jpg",
        "file_name": file_name,
        "file_size": file_size,
      }
    ]
  }

  response = requests.post(FILE_UPLOAD_URL, headers=HEADERS, json=data)

  payload = response.json()

  payload = response.json()

  print(response.status_code)
  print(json.dumps(payload, indent=2))

  file = payload.get("data", {}).get("files", [None])[0]



  return(
    file["file_id"],
    file["requests"][0]["url"],
    file["requests"][0]["headers"]
  )

def upload_image(image_path):
  file_id, upload_url, upload_headers = intialize_upload(image_path)

  with open(image_path, "rb") as file:
    response = requests.put(upload_url, headers=upload_headers, data=file)

  if response.status_code != 200:
    raise RuntimeError(f"Upload failed: {response.status_code} {response.reason}")

  return file_id




def start_task(file_id, skin_concerns):

    actions = list(dict.fromkeys(
        ["skin_type"] + skin_concerns
    ))

    data = {
        "src_file_id": file_id,
        "dst_actions": actions,
        "miniserver_args": {
            "enable_mask_overlay": False
        },
        "format": "json",
        "pf_camera_kit": False
    }

    print("Sending payload:")
    print(json.dumps(data, indent=2))

    resp = requests.request(
        START_METHOD,
        BASE_URL,
        headers=HEADERS,
        json=data
    )

    print("Status:", resp.status_code)
    print("Response:")
    print(resp.text)

    if not resp.ok:
        raise RuntimeError(
            f"Start request failed: {resp.status_code} {resp.reason}"
        )

    payload = resp.json()

    task_id = payload.get("data", {}).get("task_id")

    if not task_id:
        raise RuntimeError(
            f"Task ID not found: {payload}"
        )

    print("Task ID:", task_id)

    return task_id

def poll_task(task_id, interval_s=2, max_attempts=300):

    error_messages = {
        "error_below_min_image_size":
            "The uploaded image is too small. Please upload a higher-resolution image.",

        "error_exceed_max_image_size":
            "The uploaded image is too large. Please upload a smaller image.",

        "error_src_face_too_small":
            "Your face appears too small in the image. Please move closer to the camera so your face takes up more of the image.",

        "error_src_face_out_of_bound":
            "Your face is not fully within the image. Please make sure your entire face is visible and centered.",

        "error_lighting_dark":
            "The image is too dark to analyze properly. Please take the photo in brighter, even lighting.",
    }

    for attempt in range(1, max_attempts + 1):

        poll_url = f"{BASE_URL}/{task_id}"

        resp = requests.get(
            poll_url,
            headers=HEADERS
        )

        if not resp.ok:
            raise RuntimeError(
                f"Unable to check the scan status: "
                f"{resp.status_code} {resp.reason}"
            )

        payload = resp.json() if resp.content else {}

        status = payload.get(
            "data", {}
        ).get(
            "task_status"
        )

        print(
            "[pollTask] Attempt",
            attempt,
            "status =",
            status
        )

        # ==============================
        # SUCCESS
        # ==============================

        if status == "success":

            print(
                "[pollTask] Success results:",
                payload.get("data", {}).get("results")
            )

            return payload

        # ==============================
        # ERROR
        # ==============================

        if status == "error":

            print("========== YOUCAM API ERROR ==========")
            print(json.dumps(payload, indent=2))

            error = (
                payload
                .get("data", {})
                .get("error")
            )

            error_code = None

            if isinstance(error, dict):
                error_code = (
                    error.get("code")
                    or error.get("error_code")
                )

            elif isinstance(error, str):
                error_code = error

            print("YouCam error code:", error_code)

            # Known YouCam error
            if error_code in error_messages:
                raise RuntimeError(
                    error_messages[error_code]
                )

            # Unknown API error
            raise RuntimeError(
                "We couldn't analyze your image. "
                "Please try again with a clear, well-lit photo "
                "of your face."
            )

        time.sleep(interval_s)

    raise RuntimeError(
        "The skin analysis took too long. "
        "Please try again."
    )