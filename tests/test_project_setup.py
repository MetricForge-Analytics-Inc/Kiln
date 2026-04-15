"""Tests for ProjectInitializer."""

import pytest
from pathlib import Path
from unittest.mock import patch

from metricforge.utils.project_setup import ProjectInitializer


class TestProjectInitializer:

    def test_scaffold_creates_directories(self, tmp_path, fake_crucible):
        proj = tmp_path / "myproj"
        init = ProjectInitializer(proj, fake_crucible)
        config = {
            "project_name": "myproj",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "pipelines": {},
        }
        init.scaffold(config)

        assert (proj / "db").exists()
        assert (proj / "Orchestration" / "logs").exists()
        assert (proj / "metricforge.yaml").exists()

    def test_scaffold_copies_crucible_files(self, tmp_path, fake_crucible):
        proj = tmp_path / "myproj"
        init = ProjectInitializer(proj, fake_crucible)
        config = {
            "project_name": "myproj",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "pipelines": {},
        }
        init.scaffold(config)

        assert (proj / "Orchestration" / "Main.py").exists()
        assert (proj / "Visualization" / "Dockerfile").exists()

    def test_git_init(self, tmp_path, fake_crucible):
        proj = tmp_path / "gitproj"
        init = ProjectInitializer(proj, fake_crucible)
        config = {
            "project_name": "gitproj",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "pipelines": {},
        }
        init.scaffold(config)
        init.git_init()
        assert (proj / ".git").exists()
