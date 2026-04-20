# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from app.services.storage import load_sessions, load_tasks, next_item_id, next_task_id, save_tasks


def now_iso():
    return datetime.now().isoformat()


def _session_matches_task(session, task_id):
    return session.get("taskId") == task_id


def _build_task_stats(task, task_sessions):
    total_selections = 0
    prompt_a_selections = 0
    prompt_b_selections = 0

    for item in task.get("items", []):
        item["promptASelections"] = 0
        item["promptBSelections"] = 0

    item_map = {}
    for item in task.get("items", []):
        item_map[item.get("id")] = item

    for session in task_sessions:
        for answer in session.get("answers", []):
            total_selections += 1
            selected_prompt = answer.get("selectedPrompt")
            if selected_prompt == "prompt_a":
                prompt_a_selections += 1
                if answer.get("itemId") in item_map:
                    item_map[answer.get("itemId")]["promptASelections"] += 1
            elif selected_prompt == "prompt_b":
                prompt_b_selections += 1
                if answer.get("itemId") in item_map:
                    item_map[answer.get("itemId")]["promptBSelections"] += 1

    task["sessions"] = copy.deepcopy(task_sessions)
    task["totalSelections"] = total_selections
    task["promptASelections"] = prompt_a_selections
    task["promptBSelections"] = prompt_b_selections
    task["promptAPercentage"] = int(round((prompt_a_selections * 100.0 / total_selections))) if total_selections else 0
    task["promptBPercentage"] = int(round((prompt_b_selections * 100.0 / total_selections))) if total_selections else 0
    task["itemCount"] = len(task.get("items", []))
    task["sessionCount"] = len(task_sessions)
    return task


def list_tasks_for_operator(operator):
    tasks = load_tasks()
    sessions = load_sessions()
    role = operator.get("role")
    username = operator.get("username")
    result = []

    for task in tasks:
        if role != "admin":
            is_published = task.get("status") == "published"
            is_private_owner = task.get("visibility") == "private" and task.get("createdBy") == username
            if not (is_published or is_private_owner):
                continue

        task_sessions = [session for session in sessions if _session_matches_task(session, task.get("id"))]
        result.append(_build_task_stats(copy.deepcopy(task), task_sessions))

    return result


def get_task_detail(task_id):
    tasks = load_tasks()
    sessions = load_sessions()
    for task in tasks:
        if task.get("id") == task_id:
            task_sessions = [session for session in sessions if _session_matches_task(session, task_id)]
            return _build_task_stats(copy.deepcopy(task), task_sessions)
    return None


def create_task(operator, task_payload):
    tasks = load_tasks()
    task_id = next_task_id(tasks)
    new_task = {
        "id": task_id,
        "name": task_payload.get("name", ""),
        "description": task_payload.get("description", ""),
        "promptA": task_payload.get("promptA", ""),
        "promptB": task_payload.get("promptB", ""),
        "promptAImages": copy.deepcopy(task_payload.get("promptAImages", [])),
        "promptBImages": copy.deepcopy(task_payload.get("promptBImages", [])),
        "testData": task_payload.get("testData", ""),
        "status": task_payload.get("status", "draft"),
        "visibility": task_payload.get("visibility", "private" if operator.get("role") != "admin" else "public"),
        "questionLimit": task_payload.get("questionLimit", 49),
        "createdBy": operator.get("username", ""),
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
        "items": copy.deepcopy(task_payload.get("items", [])),
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return get_task_detail(task_id)


def update_task(task_id, task_payload):
    tasks = load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task["name"] = task_payload.get("name", task.get("name", ""))
            task["description"] = task_payload.get("description", task.get("description", ""))
            task["promptA"] = task_payload.get("promptA", task.get("promptA", ""))
            task["promptB"] = task_payload.get("promptB", task.get("promptB", ""))
            task["promptAImages"] = copy.deepcopy(task_payload.get("promptAImages", task.get("promptAImages", [])))
            task["promptBImages"] = copy.deepcopy(task_payload.get("promptBImages", task.get("promptBImages", [])))
            task["testData"] = task_payload.get("testData", task.get("testData", ""))
            task["status"] = task_payload.get("status", task.get("status", "draft"))
            task["visibility"] = task_payload.get("visibility", task.get("visibility", "private"))
            task["questionLimit"] = task_payload.get("questionLimit", task.get("questionLimit", 49))
            if "items" in task_payload and isinstance(task_payload.get("items"), list):
                task["items"] = copy.deepcopy(task_payload.get("items"))
            task["updatedAt"] = now_iso()
            save_tasks(tasks)
            return get_task_detail(task_id)
    return None


def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task.get("id") != task_id]
    deleted = len(new_tasks) != len(tasks)
    if deleted:
        save_tasks(new_tasks)
    return deleted


def publish_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "published"
            task["updatedAt"] = now_iso()
            save_tasks(tasks)
            return get_task_detail(task_id)
    return None


def create_task_item(task_id, item_payload):
    tasks = load_tasks()
    new_item_id = next_item_id(tasks)
    for task in tasks:
        if task.get("id") == task_id:
            task.setdefault("items", [])
            task["items"].append(
                {
                    "id": new_item_id,
                    "code": item_payload.get("code", ""),
                    "sourceType": item_payload.get("sourceType", "text"),
                    "sortOrder": item_payload.get("sortOrder", len(task.get("items", [])) + 1),
                    "sourceText": item_payload.get("sourceText", ""),
                    "images": item_payload.get("images", []),
                }
            )
            task["updatedAt"] = now_iso()
            save_tasks(tasks)
            return get_task_detail(task_id)
    return None


def delete_task_item(task_id, item_id):
    tasks = load_tasks()
    updated = False
    for task in tasks:
        if task.get("id") == task_id:
            old_count = len(task.get("items", []))
            task["items"] = [item for item in task.get("items", []) if item.get("id") != item_id]
            updated = len(task.get("items", [])) != old_count
            if updated:
                task["updatedAt"] = now_iso()
                save_tasks(tasks)
                return get_task_detail(task_id)
    return None


def import_task_items(task_id, items):
    tasks = load_tasks()
    new_item_id = next_item_id(tasks)
    for task in tasks:
        if task.get("id") == task_id:
            task.setdefault("items", [])
            for index, item in enumerate(items):
                task["items"].append(
                    {
                        "id": new_item_id + index,
                        "code": item.get("code", ""),
                        "sourceType": item.get("source_type", item.get("sourceType", "text")),
                        "sortOrder": item.get("sort_order", item.get("sortOrder", len(task["items"]) + index + 1)),
                        "sourceText": item.get("source_text", item.get("sourceText", "")),
                        "images": item.get("images", []),
                    }
                )
            task["updatedAt"] = now_iso()
            save_tasks(tasks)
            return get_task_detail(task_id)
    return None
