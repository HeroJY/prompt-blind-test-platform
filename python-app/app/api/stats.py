# -*- coding: utf-8 -*-

from typing import Any, Dict

from fastapi import APIRouter, Body

from app.config import API_PREFIX
from app.core.response import error_response, success_response
from app.services.task_service import get_task_detail, list_tasks_for_operator


router = APIRouter(prefix=API_PREFIX, tags=["stats"])


@router.post("/stats/task_overview")
def stats_task_overview(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = get_task_detail(payload.get("taskId"))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response(
        {
            "taskId": task.get("id"),
            "participantCount": len(set([session.get("userId") for session in task.get("sessions", [])])),
            "sessionCount": task.get("sessionCount", 0),
            "totalSelections": task.get("totalSelections", 0),
            "promptASelections": task.get("promptASelections", 0),
            "promptBSelections": task.get("promptBSelections", 0),
            "promptAPercentage": task.get("promptAPercentage", 0),
            "promptBPercentage": task.get("promptBPercentage", 0),
        }
    )


@router.post("/stats/task_items")
def stats_task_items(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = get_task_detail(payload.get("taskId"))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"items": task.get("items", [])})


@router.post("/stats/dashboard_overview")
def stats_dashboard_overview(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    tasks = list_tasks_for_operator(payload.get("operator", {}))
    total_items = 0
    total_sessions = 0
    published_tasks = 0
    for task in tasks:
        total_items += len(task.get("items", []))
        total_sessions += len(task.get("sessions", []))
        if task.get("status") == "published":
            published_tasks += 1
    return success_response(
        {
            "taskCount": len(tasks),
            "publishedTaskCount": published_tasks,
            "totalItemCount": total_items,
            "totalSessionCount": total_sessions,
        }
    )
