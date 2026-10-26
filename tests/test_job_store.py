"""Persistence and conservative recovery for Studio jobs."""

from purffle_shorts.job_store import JobStore
from purffle_shorts.studio import Job


def test_job_snapshots_survive_reopen(tmp_path):
    path = tmp_path / "jobs.db"
    store = JobStore(path)
    first = store.create("draft", {"offline": True}, "Draft")
    second = store.create("clip", {"source": "sample.mp4"}, "Clip")
    job = Job(first["id"], "draft", {"offline": True}, label="Draft", created=first["created"])
    job.status = "done"
    job.pct = 100
    job.result = {"script": {"title": "Hello"}}
    job.finished = 123.0
    store.save(job)

    reopened = JobStore(path)
    rows = reopened.recent()
    assert [row["id"] for row in rows] == [second["id"], first["id"]]
    assert rows[1]["status"] == "done"
    assert rows[1]["result"] == {"script": {"title": "Hello"}}
    assert rows[1]["params"] == {"offline": True}
    assert rows[1]["finished"] == 123.0
    assert reopened.create("plan", {}, "Plan")["id"] > second["id"]


def test_recovery_never_replays_interrupted_jobs(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    queued = store.create("upload", {"id": 42}, "Upload")
    running = store.create("make", {"topic": "test"}, "Make")
    completed = store.create("draft", {}, "Draft")
    active = Job(running["id"], "make", {"topic": "test"})
    active.status = "running"
    store.save(active)
    finished = Job(completed["id"], "draft", {})
    finished.status = "done"
    store.save(finished)

    store.recover()
    rows = {row["id"]: row for row in JobStore(tmp_path / "jobs.db").recent()}
    assert rows[queued["id"]]["status"] == "failed"
    assert rows[running["id"]]["status"] == "failed"
    assert rows[queued["id"]]["finished"] is not None
    assert "restart" in rows[running["id"]]["message"]
    assert rows[completed["id"]]["status"] == "done"


def test_recovery_is_idempotent(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    created = store.create("upload", {"id": 1}, "Upload")
    store.recover()
    first = store.recent()[0]
    store.recover()
    second = store.recent()[0]
    assert first["finished"] == second["finished"]
    assert second["id"] == created["id"]
