import os
import sys
import tempfile
import subprocess
import uuid
import pytest
from api.db import Base, get_engine
from api.models import User

def run_cli(args, db_url):
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url
    cmd = [sys.executable, "-m", "cli.admin"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result

@pytest.fixture
def sqlite_db_url(tmp_path):
    db_file = tmp_path / f"test_{uuid.uuid4().hex}.db"
    url = f"sqlite:///{db_file}"
    engine = get_engine(url)
    Base.metadata.create_all(engine)
    yield url
    engine.dispose()

def test_user_add_list_del(sqlite_db_url):
    # Add user
    result = run_cli(["user", "add", "-u", "Test User", "test@example.com"], sqlite_db_url)
    assert "User added" in result.stdout
    # List users
    result = run_cli(["user", "list"], sqlite_db_url)
    assert "test@example.com" in result.stdout
    assert "Test User" in result.stdout
    # Delete user
    result = run_cli(["user", "del", "test@example.com"], sqlite_db_url)
    assert "User deleted" in result.stdout
    # List again
    result = run_cli(["user", "list"], sqlite_db_url)
    assert "No users found" in result.stdout

def test_user_add_duplicate_force(sqlite_db_url):
    # Add user
    run_cli(["user", "add", "-u", "Test User", "test@example.com"], sqlite_db_url)
    # Add again without -f (should error)
    result = run_cli(["user", "add", "-u", "Test User", "test@example.com"], sqlite_db_url)
    assert "already exists" in result.stdout
    # Add again with -f (should succeed)
    result = run_cli(["-f", "user", "add", "-u", "Test User", "test@example.com"], sqlite_db_url)
    assert "User added" in result.stdout

def test_user_del_not_found(sqlite_db_url):
    result = run_cli(["user", "del", "notfound@example.com"], sqlite_db_url)
    assert "not found" in result.stdout

def test_user_add_dry_run(sqlite_db_url):
    result = run_cli(["-n", "user", "add", "-u", "Dry Run", "dry@example.com"], sqlite_db_url)
    assert "[DRY RUN]" in result.stdout
    # Should not actually add
    result = run_cli(["user", "list"], sqlite_db_url)
    assert "No users found" in result.stdout

def test_user_del_dry_run(sqlite_db_url):
    run_cli(["user", "add", "-u", "Dry Run", "dry@example.com"], sqlite_db_url)
    result = run_cli(["-n", "user", "del", "dry@example.com"], sqlite_db_url)
    assert "[DRY RUN]" in result.stdout
    # Should not actually delete
    result = run_cli(["user", "list"], sqlite_db_url)
    assert "dry@example.com" in result.stdout 