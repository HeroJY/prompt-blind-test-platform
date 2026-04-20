# -*- coding: utf-8 -*-

from fastapi import APIRouter

from app.config import API_PREFIX, APP_NAME, APP_VERSION
from app.core.response import success_response


router = APIRouter(prefix=API_PREFIX, tags=["system"])


@router.post("/system/ping")
def system_ping():
    return success_response(
        {
            "service": APP_NAME,
            "version": APP_VERSION,
            "status": "ok",
        }
    )
