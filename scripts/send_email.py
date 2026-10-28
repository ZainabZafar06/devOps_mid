import json
import os
import smtplib
import sys
from email.message import EmailMessage


def main():
       user = os.environ.get("EMAIL_USER")
       password = os.environ.get("EMAIL_PASSWORD")
       to = os.environ.get("EMAIL_TO")
       if not (user and password and to):
           print("EMAIL_USER / EMAIL_PASSWORD / EMAIL_TO secrets are not set.")
           sys.exit(1)

       host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
       port = int(os.environ.get("SMTP_PORT", "465"))

       with open("report.json", encoding="utf-8") as f:
           report = json.load(f)
       s = report["summary"]

       lines = [
           f"Repository : {report['repository']}",
           f"Branch     : {report['branch']}",
           f"Commit     : {report['commit_sha']}",
           f"Run ID     : {report['run_id']}",
           f"Time       : {report['timestamp']}",
           f"Overall    : {s['status'].upper()}",
           f"Total: {s['total']}  Passed: {s['passed']}  Failed: {s['failed']}",
           "",
           "Individual results:",
       ]
       for t in report["tests"]:
           line = f" - {t['name']}: {t['result']}"
           if t["failure_message"]:
               line += f"  ({t['failure_message']})"
           lines.append(line)

       msg = EmailMessage()
       msg["Subject"] = f"[{s['status'].upper()}] {report['repository']} @ {report['commit_sha'][:7]}"
       msg["From"] = user
       msg["To"] = to
       msg.set_content("\n".join(lines))
       msg.add_attachment(json.dumps(report, indent=2).encode(),
                          maintype="application", subtype="json",
                          filename="test-report.json")

       with smtplib.SMTP_SSL(host, port) as server:
           server.login(user, password)
           server.send_message(msg)
       print("Email sent to", to)


if __name__ == "__main__":
       main()