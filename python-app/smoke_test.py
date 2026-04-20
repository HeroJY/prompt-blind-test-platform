# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import time
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000/api/v1"


def post_json(path, payload):
    request = Request(
        BASE_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    response = urlopen(request, timeout=10)
    return json.loads(response.read().decode("utf-8"))


def main():
    server = subprocess.Popen([sys.executable, "simple_server.py"])
    try:
        time.sleep(1.0)

        operator = {"username": "tester01", "role": "tester"}

        ping = post_json("/system/ping", {})
        tasks = post_json("/task/list", {"operator": operator})
        start = post_json("/session/start", {"operator": operator, "taskId": 1, "questionLimit": 3})
        session_id = start["data"]["session"]["id"]
        generate = post_json(
            "/session/generate",
            {
                "operator": operator,
                "sessionId": session_id,
                "slotIndex": 0,
                "originalQuestion": "请生成客服安抚回复",
                "testData": "order_id=9988",
            },
        )
        question_record_id = generate["data"]["questionRecordId"]
        vote = post_json(
            "/session/vote",
            {
                "operator": operator,
                "sessionId": session_id,
                "questionRecordId": question_record_id,
                "selectedOption": "A",
            },
        )
        judge = post_json(
            "/session/judge",
            {
                "operator": operator,
                "sessionId": session_id,
                "questionRecordId": question_record_id,
            },
        )
        finish = post_json("/session/finish", {"operator": operator, "sessionId": session_id})
        stats = post_json("/stats/task_overview", {"operator": operator, "taskId": 1})

        print("ping:", ping["message"])
        print("task_count:", len(tasks["data"]["tasks"]))
        print("session_id:", session_id)
        print("generated:", bool(generate["data"]["candidateA"]))
        print("voted:", vote["data"]["selectedOption"])
        print("judged:", judge["data"]["recommended"])
        print("finished:", finish["data"]["session"]["status"])
        print("stats_total:", stats["data"]["totalSelections"])
    finally:
        server.kill()


if __name__ == "__main__":
    main()
