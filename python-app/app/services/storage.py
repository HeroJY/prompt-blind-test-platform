# -*- coding: utf-8 -*-

import copy
import json
import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
SESSIONS_FILE = os.path.join(BASE_DIR, "sessions.json")


def _ensure_base_dir():
    if not os.path.isdir(BASE_DIR):
        os.makedirs(BASE_DIR)


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
