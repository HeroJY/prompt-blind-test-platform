# -*- coding: utf-8 -*-

from fastapi.responses import JSONResponse


def success_response(data=None, message="ok"):
    return {
        "code": 0,
        "message": message,
        "data": {} if data is None else data,
    }


def error_response(code, message, data=None, status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data,
        },
    )
