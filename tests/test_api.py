"""Tests for the FastAPI provisioning API."""

import json
import os
import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient


@pytest.fixture
def api_client(tmp_path, fake_crucible, monkeypatch):
    """Create a test client with CRUCIBLE_PATH and OUTPUT_ROOT configured."""
    monkeypatch.setenv("CRUCIBLE_PATH", str(fake_crucible))

    import metricforge.api as api_mod
    api_mod.CRUCIBLE_PATH = fake_crucible
    api_mod.OUTPUT_ROOT = tmp_path / "output"
    (tmp_path / "output").mkdir()

    client = TestClient(api_mod.app)
    yield client, tmp_path / "output"


# ── Health ────────────────────────────────────────────────────────


class TestHealthEndpoint:

    def test_health_ok(self, api_client):
        client, _ = api_client
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["crucible_available"] is True
        assert "version" in data


# ── Create Project ────────────────────────────────────────────────


class TestCreateProject:

    def test_create_project(self, api_client):
        client, output = api_client
        resp = client.post("/projects", json={
            "project_name": "api-test",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["status"] == "created"
        assert data["project_name"] == "api-test"
        assert (output / "api-test" / "metricforge.yaml").exists()

    def test_create_project_with_pipelines(self, api_client):
        client, output = api_client
        resp = client.post("/projects", json={
            "project_name": "pipe-api",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
            "support_software": "zendesk",
        })
        assert resp.status_code == 201
        assert (output / "pipe-api" / "Pipeline-Casts" / "Support" / "zendesk").exists()

    def test_create_duplicate_project(self, api_client):
        client, _ = api_client
        client.post("/projects", json={
            "project_name": "dup-test",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        resp = client.post("/projects", json={
            "project_name": "dup-test",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        assert resp.status_code == 409

    def test_create_invalid_name(self, api_client):
        client, _ = api_client
        resp = client.post("/projects", json={
            "project_name": "../escape",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        assert resp.status_code == 422  # pydantic validation


# ── Get Project Status ────────────────────────────────────────────


class TestGetProjectStatus:

    def test_existing_project(self, api_client):
        client, _ = api_client
        client.post("/projects", json={
            "project_name": "status-test",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        resp = client.get("/projects/status-test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["exists"] is True
        assert data["has_metricforge_yaml"] is True

    def test_nonexistent_project(self, api_client):
        client, _ = api_client
        resp = client.get("/projects/nope")
        assert resp.status_code == 200
        data = resp.json()
        assert data["exists"] is False


# ── Add Pipeline ──────────────────────────────────────────────────


class TestAddPipelineAPI:

    def test_add_pipeline(self, api_client):
        client, output = api_client
        client.post("/projects", json={
            "project_name": "addp-test",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        resp = client.post("/projects/addp-test/pipelines", json={
            "area": "support",
            "software": "zendesk",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "added"

    def test_add_duplicate_pipeline(self, api_client):
        client, _ = api_client
        client.post("/projects", json={
            "project_name": "dupap",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        client.post("/projects/dupap/pipelines", json={
            "area": "support", "software": "zendesk",
        })
        resp = client.post("/projects/dupap/pipelines", json={
            "area": "support", "software": "zendesk",
        })
        assert resp.status_code == 409

    def test_add_pipeline_to_missing_project(self, api_client):
        client, _ = api_client
        resp = client.post("/projects/ghost/pipelines", json={
            "area": "support", "software": "zendesk",
        })
        assert resp.status_code == 404

    def test_add_pipeline_invalid_area(self, api_client):
        client, _ = api_client
        resp = client.post("/projects/x/pipelines", json={
            "area": "marketing", "software": "zendesk",
        })
        assert resp.status_code == 422


# ── Upgrade ───────────────────────────────────────────────────────


class TestUpgradeAPI:

    def test_upgrade_project(self, api_client):
        client, output = api_client
        client.post("/projects", json={
            "project_name": "upg-api",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
        })
        resp = client.post("/projects/upg-api/upgrade")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "upgraded"

    def test_upgrade_missing_project(self, api_client):
        client, _ = api_client
        resp = client.post("/projects/nope/upgrade")
        assert resp.status_code == 404


# ── Delete ────────────────────────────────────────────────────────


class TestDeleteAPI:

    def test_delete_project(self, api_client):
        client, output = api_client
        client.post("/projects", json={
            "project_name": "del-test",
            "data_warehouse": "duckdb",
            "semantic_layer": "cube",
            "include_git": False,
        })
        resp = client.delete("/projects/del-test")
        assert resp.status_code == 200
        assert not (output / "del-test").exists()

    def test_delete_missing_project(self, api_client):
        client, _ = api_client
        resp = client.delete("/projects/nope")
        assert resp.status_code == 404


# ── Path Traversal Protection ─────────────────────────────────────


class TestPathTraversal:

    def test_safe_project_path_rejects_traversal(self, api_client):
        client, _ = api_client
        # Name with path-encoded dots — FastAPI may return 404 (route mismatch)
        # or 400/422 (validation). Any non-200 that doesn't leak data is fine.
        resp = client.get("/projects/..%2F..%2Fetc")
        assert resp.status_code in (200, 400, 404, 422)
        if resp.status_code == 200:
            assert resp.json()["exists"] is False
