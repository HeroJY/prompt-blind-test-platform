# -*- coding: utf-8 -*-

from typing import Any, Dict

from fastapi import APIRouter, Body

from app.config import API_PREFIX
from app.core.response import success_response


router = APIRouter(prefix=API_PREFIX, tags=["ai"])


@router.post("/ai/prompt_generate")
def ai_prompt_generate(payload=Body(...)):  # type: (Dict[str, Any]) -> Dict[str, Any]
    requirement = payload.get("requirement", "")
    generated_prompt = (
        "你是一名资深业务助手，请围绕以下需求生成高质量输出：\n"
        "1. 先理解用户目标\n"
        "2. 给出结构清晰、语气自然的回答\n"
        "3. 必要时提供可执行建议\n\n"
        "需求：{0}".format(requirement)
    )
    return success_response(
        {
            "prompt_text": generated_prompt,
            "action": "ai_prompt_generate",
        }
    )
