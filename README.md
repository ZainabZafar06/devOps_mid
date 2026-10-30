# Assignment Submission Portal

Flask app where students submit assignment links, with CI testing and local report delivery.

## Run the application
```
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Run the tests
```
python -m pytest -v
```

## Start the local report receiver
```
python receiver/receiver.py
```
It listens on http://127.0.0.1:9000/report and saves the report to `receiver/test-report.json`.

## CI pipeline
- `.github/workflows/ci.yml` runs on every push using a **self-hosted runner** on my computer.
- Tests run, then `scripts/send_report.py` POSTs the JSON report to the receiver (pass or fail).
- `scripts/send_email.py` emails the report (needs secrets EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO).
- On `main`, if tests pass, `docs/` is deployed to GitHub Pages.

## Self-hosted runner setup
Repo Settings → Actions → Runners → New self-hosted runner, then run `config` and `run`.

Pages URL: https://zainabzafar06.github.io/devOps_mid/
