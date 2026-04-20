# -*- coding: utf-8 -*-

from typing import Any, Dict

from fastapi import APIRouter, Body

from app.config import API_PREFIX
from app.core.response import error_response, success_response
from app.services.task_service import (
    create_task,
    create_task_item,
    delete_task,
    delete_task_item,
    get_task_detail,
    import_task_items,
    list_tasks_for_operator,
    publish_task,
    update_task,
)


router = APIRouter(prefix=API_PREFIX, tags=["task"])


@router.post("/task/list")
def task_list(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    tasks = list_tasks_for_operator(payload.get("operator", {}))
    return success_response({"tasks": tasks})


@router.post("/task/create")
def task_create(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = create_task(payload.get("operator", {}), payload.get("task", {}))
    return success_response({"task": task})


@router.post("/task/detail")
def task_detail(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = get_task_detail(payload.get("taskId"))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"task": task})


@router.post("/task/update")
def task_update(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = update_task(payload.get("taskId"), payload.get("task", {}))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"task": task})


@router.post("/task/delete")
def task_delete(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    deleted = delete_task(payload.get("taskId"))
    if not deleted:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"deleted": True})


@router.post("/task/publish")
def task_publish(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = publish_task(payload.get("taskId"))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"task": task})


@router.post("/task/item/list")
def task_item_list(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = get_task_detail(payload.get("taskId"))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"items": task.get("items", [])})


@router.post("/task/item/create")
def task_item_create(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = create_task_item(payload.get("taskId"), payload.get("item", {}))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"task": task})


@router.post("/task/item/update")
def task_item_update(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    return error_response(4005, "task item update is not implemented yet", status_code=501)


@router.post("/task/item/delete")
def task_item_delete(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = delete_task_item(payload.get("taskId"), payload.get("itemId"))
    if not task:
        return error_response(4004, "task or item not found", status_code=404)
    return success_response({"task": task})


@router.post("/task/item/import_excel")
def task_item_import_excel(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = import_task_items(payload.get("taskId"), payload.get("items", []))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"task": task})
