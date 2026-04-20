# -*- coding: utf-8 -*-

from typing import Any, Dict

from fastapi import APIRouter, Body

from app.config import API_PREFIX
from app.core.response import error_response, success_response
from app.services.session_service import (
    delete_history_question,
    finish_session,
    generate_question,
    judge_question,
    session_detail as get_session_detail,
    start_session,
    task_history,
    vote_question,
)


router = APIRouter(prefix=API_PREFIX, tags=["session"])


@router.post("/session/start")
def session_start(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    session = start_session(
        payload.get("operator", {}),
        payload.get("taskId"),
        payload.get("questionLimit", 49),
    )
    if not session:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"session": session})


@router.post("/session/detail")
def session_detail(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    session = get_session_detail(payload.get("sessionId"))
    if not session:
        return error_response(4006, "session not found", status_code=404)
    return success_response({"session": session})


@router.post("/session/generate")
def session_generate(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    result = generate_question(
        payload.get("sessionId"),
        payload.get("slotIndex"),
        payload.get("originalQuestion", ""),
        payload.get("testData", ""),
    )
    if not result:
        return error_response(4006, "session or question not found", status_code=404)
    return success_response(result)


@router.post("/session/vote")
def session_vote(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    result = vote_question(
        payload.get("sessionId"),
        payload.get("questionRecordId"),
        payload.get("selectedOption"),
    )
    if not result:
        return error_response(4006, "session or question not found", status_code=404)
    return success_response(result, message="saved")


@router.post("/session/judge")
def session_judge(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    result = judge_question(payload.get("sessionId"), payload.get("questionRecordId"))
    if not result:
        return error_response(4006, "session or question not found", status_code=404)
    return success_response(result)


@router.post("/session/finish")
def session_finish(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    session = finish_session(payload.get("sessionId"), "finished")
    if not session:
        return error_response(4006, "session not found", status_code=404)
    return success_response({"session": session})


@router.post("/session/quit")
def session_quit(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    session = finish_session(payload.get("sessionId"), "quit")
    if not session:
        return error_response(4006, "session not found", status_code=404)
    return success_response({"session": session})


@router.post("/history/task_list")
def history_task_list(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    task = task_history(payload.get("taskId"))
    if not task:
        return error_response(4004, "task not found", status_code=404)
    return success_response({"task": task})


@router.post("/history/session_detail")
def history_session_detail(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    session = get_session_detail(payload.get("sessionId"))
    if not session:
        return error_response(4006, "session not found", status_code=404)
    return success_response({"session": session})


@router.post("/history/question/delete")
def history_question_delete(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    session = delete_history_question(payload.get("sessionId"), payload.get("questionId"))
    if not session:
        return error_response(4006, "session not found", status_code=404)
    return success_response({"session": session})
