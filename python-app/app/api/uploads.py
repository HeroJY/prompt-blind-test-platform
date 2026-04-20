# -*- coding: utf-8 -*-

from fastapi import APIRouter, File, UploadFile

from app.config import ALLOW_ZIP_UPLOAD, API_PREFIX
from app.core.response import error_response, success_response
from app.services.excel_parser import (
    parse_item_excel,
    parse_prompt_excel,
    parse_test_data_excel,
    validate_excel_filename,
)


router = APIRouter(prefix=API_PREFIX, tags=["upload"])


@router.post("/upload/prompt_excel")
async def upload_prompt_excel(file=File(...)):  # type: (UploadFile) -> dict
    error = validate_excel_filename(file.filename)
    if error:
        return error_response(4002, error)

    file_bytes = await file.read()

    try:
        result = parse_prompt_excel(file_bytes)
    except ValueError as exc:
        return error_response(4002, str(exc))

    result["file_name"] = file.filename
    return success_response(result)


@router.post("/upload/item_excel")
async def upload_item_excel(file=File(...)):  # type: (UploadFile) -> dict
    error = validate_excel_filename(file.filename)
    if error:
        return error_response(4002, error)

    file_bytes = await file.read()

    try:
        result = parse_item_excel(file_bytes)
    except ValueError as exc:
        return error_response(4002, str(exc))

    result["file_name"] = file.filename
    return success_response(result)


@router.post("/upload/test_data_excel")
async def upload_test_data_excel(file=File(...)):  # type: (UploadFile) -> dict
    error = validate_excel_filename(file.filename)
    if error:
        return error_response(4002, error)

    file_bytes = await file.read()

    try:
        result = parse_test_data_excel(file_bytes)
    except ValueError as exc:
        return error_response(4002, str(exc))

    result["file_name"] = file.filename
    return success_response(result)


@router.post("/upload/task_zip")
def upload_task_zip():
    if not ALLOW_ZIP_UPLOAD:
        return error_response(4003, "zip upload is not enabled yet", status_code=403)

    return success_response({"enabled": True})
