import pytest
from app import create_app, load_submissions


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "submissions.json"))
    app.config["TESTING"] = True
    return app.test_client()


def data(**changes):
    d = {"name": "Ali Khan", "reg_no": "FA22-BCS-001",
         "title": "Lab 1", "url": "https://github.com/ali/lab1"}
    d.update(changes)
    return d


def saved(client):
    return load_submissions(client.application.config["DATA_FILE"])


def test_valid_submission_is_saved_and_listed(client):
    r = client.post("/", data=data())
    assert r.status_code == 200
    assert len(saved(client)) == 1
    assert b"FA22-BCS-001" in r.data
    assert b"https://github.com/ali/lab1" in client.get("/").data


def test_missing_registration_number_is_rejected(client):
    r = client.post("/", data=data(reg_no=""))
    assert r.status_code == 400
    assert b"Registration number is required" in r.data
    assert saved(client) == []


def test_invalid_url_is_rejected_and_not_saved(client):
    r = client.post("/", data=data(url="not-a-valid-url"))
    assert r.status_code == 400
    assert b"Submission URL is invalid" in r.data
    assert saved(client) == []