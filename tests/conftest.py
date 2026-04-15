"""Shared fixtures for MetricForge tests."""

import os
import pytest
from pathlib import Path


@pytest.fixture
def tmp_project(tmp_path):
    """Return a temporary directory to use as a project root."""
    return tmp_path


@pytest.fixture
def sample_config_dict():
    """Minimal metricforge.yaml config as a dict."""
    return {
        "project_name": "test-project",
        "organization": "TestOrg",
        "data_warehouse": {"type": "duckdb_local", "config": {"database_path": "./db/test.duckdb"}},
        "semantic_layer": {"type": "cube_oss", "config": {"port": 4000}},
        "pipelines": {
            "support": {"software": "zendesk"},
        },
    }


@pytest.fixture
def sample_build_config():
    """Config dict in the flat format expected by build_context()."""
    return {
        "project_name": "test-project",
        "project_slug": "test_project",
        "organization": "TestOrg",
        "data_warehouse_type": "duckdb_local",
        "semantic_layer_type": "cube_oss",
        "include_docker": True,
        "include_tests": True,
        "include_cicd": True,
        "pipelines": {"support": {"software": "zendesk"}},
    }


@pytest.fixture
def config_yaml_file(tmp_path, sample_config_dict):
    """Write a sample metricforge.yaml and return its path."""
    import yaml

    p = tmp_path / "metricforge.yaml"
    p.write_text(yaml.dump(sample_config_dict), encoding="utf-8")
    return p


@pytest.fixture
def fake_crucible(tmp_path):
    """Create a minimal fake Crucible directory structure."""
    crucible = tmp_path / "Crucible"
    # Static files
    for rel in [
        "Orchestration/Dockerfile",
        "Orchestration/entrypoint.sh",
        "Orchestration/requirements.txt",
        "Orchestration/trigger.py",
        "Orchestration/Main.py",
        "Visualization/Dockerfile",
        "Visualization/entrypoint.sh",
        "Visualization/dev.sh",
        "Visualization/degit.json",
        "Visualization/requirements.txt",
        "Visualization/package.json",
        "Visualization/evidence.config.yaml",
        "Semantic-Cubes/model/cube.py",
    ]:
        f = crucible / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"# stub: {rel}\n", encoding="utf-8")

    # Visualization dirs
    for d in ["pages", "sources", "components"]:
        (crucible / "Visualization" / d).mkdir(parents=True, exist_ok=True)
        (crucible / "Visualization" / d / "stub.md").write_text("stub", encoding="utf-8")

    # Cube model files
    for i in range(1, 7):
        f = crucible / f"Semantic-Cubes/model/cubes/{i}_tickets_case_created_time.yaml"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"cube: stub_{i}\n", encoding="utf-8")
    (crucible / "Semantic-Cubes/model/cubes/END_tickets_case_detail.yaml").write_text("cube: end\n", encoding="utf-8")

    # Pipeline casts
    for area, vendor in [("Support", "zendesk"), ("Support", "salesforce"),
                         ("Sales", "zendesk"), ("Sales", "salesforce")]:
        for sub in ["Data-Extract", "Data-Pipeline"]:
            d = crucible / "Pipeline-Casts" / area / vendor / sub
            d.mkdir(parents=True, exist_ok=True)
            (d / "stub.py").write_text("# pipeline stub\n", encoding="utf-8")

    return crucible
