# -*- coding: utf-8 -*-

import base64
import binascii
import copy
import json
import os
import re
import shutil
import uuid


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
SESSIONS_FILE = os.path.join(BASE_DIR, "sessions.json")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
PROMPT_UPLOADS_DIR = os.path.join(UPLOADS_DIR, "prompts")

DATA_URL_PATTERN = re.compile(r"^data:(image/[A-Za-z0-9.+-]+);base64,(.+)$")

EXTENSION_BY_MIME = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _ensure_base_dir():
    if not os.path.isdir(BASE_DIR):
        os.makedirs(BASE_DIR)
    if not os.path.isdir(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    if not os.path.isdir(PROMPT_UPLOADS_DIR):
        os.makedirs(PROMPT_UPLOADS_DIR)


def _read_json(path, default_value):
    _ensure_base_dir()
    if not os.path.exists(path):
        return copy.deepcopy(default_value)
    with open(path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _write_json(path, data):
    _ensure_base_dir()
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(data, file_obj, ensure_ascii=False, indent=2)


def load_tasks():
    return _read_json(TASKS_FILE, [])


def save_tasks(tasks):
    _write_json(TASKS_FILE, tasks)


def load_sessions():
    return _read_json(SESSIONS_FILE, [])


def save_sessions(sessions):
    _write_json(SESSIONS_FILE, sessions)


def next_task_id(tasks):
    max_id = 0
    for task in tasks:
        try:
            max_id = max(max_id, int(task.get("id", 0)))
        except (TypeError, ValueError):
            continue
    return max_id + 1


def next_item_id(tasks):
    max_id = 0
    for task in tasks:
        for item in task.get("items", []):
            try:
                max_id = max(max_id, int(item.get("id", 0)))
            except (TypeError, ValueError):
                continue
    return max_id + 1


def uploads_root():
    _ensure_base_dir()
    return UPLOADS_DIR


def _safe_prompt_dir(task_id, slot_name):
    _ensure_base_dir()
    task_dir = os.path.join(PROMPT_UPLOADS_DIR, "task_{0}".format(task_id), slot_name)
    if not os.path.isdir(task_dir):
        os.makedirs(task_dir)
    return task_dir


def _parse_data_url(data_url):
    if not data_url:
        raise ValueError("image data is required")

    matched = DATA_URL_PATTERN.match(data_url)
    if not matched:
        raise ValueError("invalid image data url")

    mime_type = matched.group(1)
    encoded = matched.group(2)
    extension = EXTENSION_BY_MIME.get(mime_type, ".bin")
    try:
        file_bytes = base64.b64decode(encoded)
    except (TypeError, binascii.Error):
        raise ValueError("invalid image base64 data")
    return mime_type, extension, file_bytes


def _url_to_local_path(url_path):
    if not url_path or not url_path.startswith("/uploads/"):
        return ""
    relative_path = url_path[len("/uploads/"):]
    return os.path.join(UPLOADS_DIR, relative_path)


def _remove_file_if_exists(file_path):
    if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)


def sync_prompt_images(task_id, slot_name, incoming_images, existing_images):
    # type: (int, str, list, list) -> list
    incoming_images = incoming_images or []
    existing_images = existing_images or []

    slot_dir = _safe_prompt_dir(task_id, slot_name)
    result = []
    kept_urls = set()

    for image in incoming_images:
        if not isinstance(image, dict):
            continue

        existing_url = image.get("url", "")
        if existing_url and not image.get("dataUrl"):
            result.append(
                {
                    "name": image.get("name", ""),
                    "type": image.get("type", ""),
                    "url": existing_url,
                }
            )
            kept_urls.add(existing_url)
            continue

        data_url = image.get("dataUrl", "")
        if not data_url:
            continue

        mime_type, extension, file_bytes = _parse_data_url(data_url)
        file_name = "{0}{1}".format(uuid.uuid4().hex, extension)
        file_path = os.path.join(slot_dir, file_name)
        with open(file_path, "wb") as file_obj:
            file_obj.write(file_bytes)

        relative_url = "/uploads/prompts/task_{0}/{1}/{2}".format(task_id, slot_name, file_name)
        result.append(
            {
                "name": image.get("name", file_name),
                "type": image.get("type", mime_type),
                "url": relative_url,
            }
        )
        kept_urls.add(relative_url)

    for image in existing_images:
        if not isinstance(image, dict):
            continue
        existing_url = image.get("url", "")
        if existing_url and existing_url not in kept_urls:
            _remove_file_if_exists(_url_to_local_path(existing_url))

    return result


def delete_prompt_uploads(task_id):
    # type: (int) -> None
    task_dir = os.path.join(PROMPT_UPLOADS_DIR, "task_{0}".format(task_id))
    if os.path.isdir(task_dir):
        shutil.rmtree(task_dir)
