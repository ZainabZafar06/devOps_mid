import datetime
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

JUNIT = "junit.xml"
RECEIVER_URL = os.environ.get("RECEIVER_URL", "http://127.0.0.1:9000/report")


def parse_tests(path):
    tests = []
    if not os.path.exists(path):
        return tests
    for tc in ET.parse(path).getroot().iter("testcase"):
        result, msg = "passed", None
        failure = tc.find("failure")
        error = tc.find("error")
        skipped = tc.find("skipped")
        if failure is not None:
            result, msg = "failed", failure.get("message")
        elif error is not None:
            result, msg = "failed", error.get("message")
        elif skipped is not None:
            result, msg = "skipped", skipped.get("message")
        tests.append({"name": tc.get("name"), "result": result, "failure_message": msg})
    return tests


def main():
    tests = parse_tests(JUNIT)
    total = len(tests)
    passed = sum(1 for t in tests if t["result"] == "passed")
    failed = sum(1 for t in tests if t["result"] == "failed")
    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local/repo"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "status": "passed" if total > 0 and failed == 0 else "failed",
        },
        "tests": tests,
    }

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    req = urllib.request.Request(
        RECEIVER_URL,
        data=json.dumps(report).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print("Receiver replied:", r.status)
    except Exception as e:
        print("Could not deliver report:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()