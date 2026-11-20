"""Shared test fixtures. pytest loads this file automatically."""

import pytest

import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point db.py at a fresh, empty database file for one test."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
