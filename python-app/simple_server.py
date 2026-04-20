# -*- coding: utf-8 -*-

import cgi
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.services.excel_parser import (
    parse_item_excel,
    parse_prompt_excel,
    parse_test_data_excel,
    validate_excel_filename,
)
from app.services.session_service import (
    delete_history_question,
    finish_session,
    generate_question,
    judge_question,
    session_detail,
    start_session,
    task_history,
    vote_question,
)
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
from app.services.storage import uploads_root


HOST = "127.0.0.1"
PORT = 8000


def success_response(data=None, message="ok"):
    return {"code": 0, "message": message, "data": {} if data is None else data}


def error_response(code, message, status=400, data=None):
    return status, {"code": code, "message": message, "data": data}


def ai_prompt_generate(payload):
    requirement = payload.get("requirement", "")
    generated_prompt = (
        "你是一名资深业务助手，请围绕以下需求生成高质量输出：\n"
        "1. 先理解用户目标\n"
        "2. 给出结构清晰、语气自然的回答\n"
        "3. 必要时提供可执行建议\n\n"
        "需求：{0}".format(requirement)
    )
    return success_response({"prompt_text": generated_prompt})


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "PromptBlindTestServer/0.1"

    def _set_headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)
        self.wfile.write(b"")

    def do_GET(self):
        if self.path.startswith("/uploads/"):
            self.serve_upload_file()
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"code": 4040, "message": "route not found", "data": None}).encode("utf-8"))

    def do_POST(self):
        try:
            status, result = self.route_request()
        except Exception as exc:
            status, result = 500, {"code": 5000, "message": str(exc), "data": None}
        self._set_headers(status)
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def serve_upload_file(self):
        uploads_dir = uploads_root()
        relative_path = self.path[len("/uploads/"):]
        local_path = os.path.abspath(os.path.join(uploads_dir, relative_path))

        if not local_path.startswith(os.path.abspath(uploads_dir)):
            self._set_headers(403)
            self.wfile.write(b"forbidden")
            return

        if not os.path.exists(local_path) or not os.path.isfile(local_path):
            self._set_headers(404)
            self.wfile.write(b"not found")
            return

        content_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"
        with open(local_path, "rb") as file_obj:
            file_bytes = file_obj.read()

        self._set_headers(200, content_type=content_type)
        self.wfile.write(file_bytes)

    def route_request(self):
        path = self.path
        if path == "/api/v1/system/ping":
            return 200, success_response({"service": "simple_server", "status": "ok"})

        if path.startswith("/api/v1/upload/"):
            return self.handle_upload(path)

        payload = self.parse_json_body()

        if path == "/api/v1/task/list":
            return 200, success_response({"tasks": list_tasks_for_operator(payload.get("operator", {}))})
        if path == "/api/v1/task/create":
            return 200, success_response({"task": create_task(payload.get("operator", {}), payload.get("task", {}))})
        if path == "/api/v1/task/detail":
            task = get_task_detail(payload.get("taskId"))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"task": task})
        if path == "/api/v1/task/update":
            task = update_task(payload.get("taskId"), payload.get("task", {}))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"task": task})
        if path == "/api/v1/task/delete":
            deleted = delete_task(payload.get("taskId"))
            if not deleted:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"deleted": True})
        if path == "/api/v1/task/publish":
            task = publish_task(payload.get("taskId"))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"task": task})
        if path == "/api/v1/task/item/list":
            task = get_task_detail(payload.get("taskId"))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"items": task.get("items", [])})
        if path == "/api/v1/task/item/create":
            task = create_task_item(payload.get("taskId"), payload.get("item", {}))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"task": task})
        if path == "/api/v1/task/item/delete":
            task = delete_task_item(payload.get("taskId"), payload.get("itemId"))
            if not task:
                return error_response(4004, "task or item not found", 404)
            return 200, success_response({"task": task})
        if path == "/api/v1/task/item/import_excel":
            task = import_task_items(payload.get("taskId"), payload.get("items", []))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"task": task})

        if path == "/api/v1/session/start":
            session = start_session(payload.get("operator", {}), payload.get("taskId"), payload.get("questionLimit", 49))
            if not session:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"session": session})
        if path == "/api/v1/session/detail":
            session = session_detail(payload.get("sessionId"))
            if not session:
                return error_response(4006, "session not found", 404)
            return 200, success_response({"session": session})
        if path == "/api/v1/session/generate":
            result = generate_question(
                payload.get("sessionId"),
                payload.get("slotIndex"),
                payload.get("originalQuestion", ""),
                payload.get("testData", ""),
            )
            if not result:
                return error_response(4006, "session or question not found", 404)
            return 200, success_response(result)
        if path == "/api/v1/session/vote":
            result = vote_question(payload.get("sessionId"), payload.get("questionRecordId"), payload.get("selectedOption"))
            if not result:
                return error_response(4006, "session or question not found", 404)
            return 200, success_response(result, message="saved")
        if path == "/api/v1/session/judge":
            result = judge_question(payload.get("sessionId"), payload.get("questionRecordId"))
            if not result:
                return error_response(4006, "session or question not found", 404)
            return 200, success_response(result)
        if path == "/api/v1/session/finish":
            session = finish_session(payload.get("sessionId"), "finished")
            if not session:
                return error_response(4006, "session not found", 404)
            return 200, success_response({"session": session})
        if path == "/api/v1/session/quit":
            session = finish_session(payload.get("sessionId"), "quit")
            if not session:
                return error_response(4006, "session not found", 404)
            return 200, success_response({"session": session})

        if path == "/api/v1/history/task_list":
            task = task_history(payload.get("taskId"))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"task": task})
        if path == "/api/v1/history/session_detail":
            session = session_detail(payload.get("sessionId"))
            if not session:
                return error_response(4006, "session not found", 404)
            return 200, success_response({"session": session})
        if path == "/api/v1/history/question/delete":
            session = delete_history_question(payload.get("sessionId"), payload.get("questionId"))
            if not session:
                return error_response(4006, "session not found", 404)
            return 200, success_response({"session": session})

        if path == "/api/v1/stats/task_overview":
            task = get_task_detail(payload.get("taskId"))
            if not task:
                return error_response(4004, "task not found", 404)
            participant_count = len(set([item.get("userId") for item in task.get("sessions", [])]))
            return 200, success_response(
                {
                    "taskId": task.get("id"),
                    "participantCount": participant_count,
                    "sessionCount": task.get("sessionCount", 0),
                    "totalSelections": task.get("totalSelections", 0),
                    "promptASelections": task.get("promptASelections", 0),
                    "promptBSelections": task.get("promptBSelections", 0),
                    "promptAPercentage": task.get("promptAPercentage", 0),
                    "promptBPercentage": task.get("promptBPercentage", 0),
                }
            )
        if path == "/api/v1/stats/task_items":
            task = get_task_detail(payload.get("taskId"))
            if not task:
                return error_response(4004, "task not found", 404)
            return 200, success_response({"items": task.get("items", [])})
        if path == "/api/v1/stats/dashboard_overview":
            tasks = list_tasks_for_operator(payload.get("operator", {}))
            total_items = sum([len(task.get("items", [])) for task in tasks])
            total_sessions = sum([len(task.get("sessions", [])) for task in tasks])
            published_tasks = len([task for task in tasks if task.get("status") == "published"])
            return 200, success_response(
                {
                    "taskCount": len(tasks),
                    "publishedTaskCount": published_tasks,
                    "totalItemCount": total_items,
                    "totalSessionCount": total_sessions,
                }
            )

        if path == "/api/v1/ai/prompt_generate":
            return 200, ai_prompt_generate(payload)

        return error_response(4040, "route not found", 404)

    def parse_json_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        if not raw_body:
            return {}
        return json.loads(raw_body.decode("utf-8"))

    def handle_upload(self, path):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST"})
        upload = form["file"] if "file" in form else None
        if not upload or not getattr(upload, "filename", ""):
            return error_response(4002, "file is required", 400)

        filename = upload.filename
        file_error = validate_excel_filename(filename)
        if file_error:
            return error_response(4002, file_error, 400)

        file_bytes = upload.file.read()
        try:
          if path == "/api/v1/upload/prompt_excel":
              result = parse_prompt_excel(file_bytes)
          elif path == "/api/v1/upload/item_excel":
              result = parse_item_excel(file_bytes)
          elif path == "/api/v1/upload/test_data_excel":
              result = parse_test_data_excel(file_bytes)
          elif path == "/api/v1/upload/task_zip":
              return error_response(4003, "zip upload is not enabled yet", 403)
          else:
              return error_response(4040, "route not found", 404)
        except ValueError as exc:
            return error_response(4002, str(exc), 400)

        result["file_name"] = filename
        return 200, success_response(result)


def run():
    server = HTTPServer((HOST, PORT), RequestHandler)
    print("Serving on http://{0}:{1}".format(HOST, PORT))
    server.serve_forever()


if __name__ == "__main__":
    run()
