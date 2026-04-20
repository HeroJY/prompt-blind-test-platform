# -*- coding: utf-8 -*-

import copy
import random
from datetime import datetime

from app.services.storage import load_sessions, load_tasks, save_sessions
from app.services.task_service import get_task_detail


def now_iso():
    return datetime.now().isoformat()


def _find_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def _find_session(session_id):
    sessions = load_sessions()
    for session in sessions:
        if session.get("id") == session_id:
            return session
    return None


def _save_session(updated_session):
    sessions = load_sessions()
    for index, session in enumerate(sessions):
        if session.get("id") == updated_session.get("id"):
            sessions[index] = updated_session
            save_sessions(sessions)
            return
    sessions.append(updated_session)
    save_sessions(sessions)


def _build_blank_question(slot_index):
    question_number = slot_index + 1
    return {
        "id": int("9{0:03d}".format(question_number)),
        "code": "Q{0:03d}".format(question_number),
        "sourceType": "text",
        "sortOrder": question_number,
        "sourceText": "",
        "images": [],
        "answerA": "",
        "answerB": "",
        "questionRecordId": "",
        "isImported": False,
        "promptMapping": None,
        "modelJudge": None,
        "testData": "",
    }


def start_session(operator, task_id, question_limit):
    task = _find_task(task_id)
    if not task:
        return None

    items = task.get("items", [])
    limit = question_limit or task.get("questionLimit", 49)
    questions = []

    for index in range(limit):
        if index < len(items):
            item = copy.deepcopy(items[index])
            item["answerA"] = ""
            item["answerB"] = ""
            item["questionRecordId"] = ""
            item["isImported"] = True
            item["promptMapping"] = None
            item["modelJudge"] = None
            item["testData"] = ""
            questions.append(item)
        else:
            questions.append(_build_blank_question(index))

    session = {
        "id": "s_{0}".format(int(datetime.now().timestamp() * 1000)),
        "taskId": task_id,
        "userId": operator.get("username", ""),
        "status": "in_progress",
        "answeredCount": 0,
        "answers": [],
        "userInputs": {},
        "testDataByQuestion": {},
        "questions": questions,
        "startTime": now_iso(),
        "endTime": None,
    }

    _save_session(session)
    return session


def session_detail(session_id):
    return _find_session(session_id)


def _make_answer(prompt_key, question_text, test_data, prompt_text):
    base_text = question_text or "请生成回复"
    test_hint = ("测试数据：{0}。".format(test_data)) if test_data else ""
    if prompt_key == "prompt_a":
        return "候选回答 A/B 来源之一：基于提示词生成。\n问题：{0}\n{1}\n风格：{2}".format(
            base_text,
            test_hint,
            prompt_text[:60]
        )
    return "候选回答 A/B 来源之一：偏强调行动路径与表达自然度。\n问题：{0}\n{1}\n风格：{2}".format(
        base_text,
        test_hint,
        prompt_text[:60]
    )


def _prompt_text_with_image_fallback(task, prompt_field, image_field):
    prompt_text = task.get(prompt_field, "") or ""
    if prompt_text:
        return prompt_text

    image_count = len(task.get(image_field, []) or [])
    if image_count:
        return "图像提示词，共 {0} 张".format(image_count)
    return ""


def generate_question(session_id, slot_index, original_question, test_data):
    session = _find_session(session_id)
    if not session:
        return None

    task = _find_task(session.get("taskId"))
    if not task:
        return None

    if slot_index < 0 or slot_index >= len(session.get("questions", [])):
        return None

    question = session["questions"][slot_index]
    question["sourceText"] = original_question or question.get("sourceText", "")
    question["testData"] = test_data or ""
    session["userInputs"][str(question.get("id"))] = original_question or ""
    session["testDataByQuestion"][str(question.get("id"))] = test_data or ""

    prompt_a_first = random.choice([True, False])
    prompt_mapping = {
        "a": "prompt_a" if prompt_a_first else "prompt_b",
        "b": "prompt_b" if prompt_a_first else "prompt_a",
    }

    prompt_text_a = _prompt_text_with_image_fallback(task, "promptA", "promptAImages")
    prompt_text_b = _prompt_text_with_image_fallback(task, "promptB", "promptBImages")
    actual_prompt_a = prompt_text_a if prompt_mapping["a"] == "prompt_a" else prompt_text_b
    actual_prompt_b = prompt_text_b if prompt_mapping["b"] == "prompt_b" else prompt_text_a

    question_record_id = question.get("questionRecordId") or "sq_{0}_{1}".format(session_id, slot_index + 1)
    question["questionRecordId"] = question_record_id
    question["promptMapping"] = prompt_mapping
    question["answerA"] = _make_answer(prompt_mapping["a"], original_question, test_data, actual_prompt_a)
    question["answerB"] = _make_answer(prompt_mapping["b"], original_question, test_data, actual_prompt_b)

    _save_session(session)
    return {
        "questionRecordId": question_record_id,
        "candidateA": question["answerA"],
        "candidateB": question["answerB"],
    }


def vote_question(session_id, question_record_id, selected_option):
    session = _find_session(session_id)
    if not session:
        return None

    target_question = None
    for question in session.get("questions", []):
        if question.get("questionRecordId") == question_record_id:
            target_question = question
            break

    if not target_question:
        return None

    prompt_mapping = target_question.get("promptMapping") or {"a": "prompt_a", "b": "prompt_b"}
    actual_selected_prompt = prompt_mapping["a"] if selected_option == "A" else prompt_mapping["b"]

    updated = False
    for answer in session.get("answers", []):
        if answer.get("itemId") == target_question.get("id"):
            answer["selectedOption"] = selected_option
            answer["selectedPrompt"] = actual_selected_prompt
            updated = True
            break

    if not updated:
        session.setdefault("answers", []).append(
            {
                "itemId": target_question.get("id"),
                "selectedOption": selected_option,
                "selectedPrompt": actual_selected_prompt,
            }
        )

    session["answeredCount"] = len(session.get("answers", []))
    _save_session(session)
    return {
        "answeredCount": session.get("answeredCount", 0),
        "selectedOption": selected_option,
        "selectedPrompt": actual_selected_prompt,
    }


def judge_question(session_id, question_record_id):
    session = _find_session(session_id)
    if not session:
        return None

    for question in session.get("questions", []):
        if question.get("questionRecordId") == question_record_id:
            recommended = random.choice(["A", "B"])
            result = {
                "recommended": recommended,
                "reason": "裁判认为候选回答 {0} 在结构完整度、语气自然度和可执行性上表现更均衡。".format(recommended),
            }
            question["modelJudge"] = result
            _save_session(session)
            return result
    return None


def finish_session(session_id, status):
    session = _find_session(session_id)
    if not session:
        return None

    session["status"] = status
    session["endTime"] = now_iso()
    session["answeredCount"] = len(session.get("answers", []))
    _save_session(session)
    return session


def task_history(task_id):
    return get_task_detail(task_id)


def delete_history_question(session_id, question_id):
    session = _find_session(session_id)
    if not session:
        return None

    session["questions"] = [question for question in session.get("questions", []) if question.get("id") != question_id]
    session["answers"] = [answer for answer in session.get("answers", []) if answer.get("itemId") != question_id]
    if str(question_id) in session.get("userInputs", {}):
        del session["userInputs"][str(question_id)]
    if str(question_id) in session.get("testDataByQuestion", {}):
        del session["testDataByQuestion"][str(question_id)]
    session["answeredCount"] = len(session.get("answers", []))
    _save_session(session)
    return session
