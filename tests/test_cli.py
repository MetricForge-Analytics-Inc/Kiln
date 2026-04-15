"""Tests for CLI commands: init, add-pipeline, build, upgrade, status."""

import json
import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from metricforge.cli import cli
from metricforge.cli.initialize import _find_crucible


# ── _find_crucible ────────────────────────────────────────────────


class TestFindCrucible:

    def test_explicit_hint(self, tmp_path):
        d = tmp_path / "my-crucible"
        d.mkdir()
        assert _find_crucible(str(d)) == d

    def test_explicit_hint_missing(self, tmp_path):
        import click
        with pytest.raises(click.BadParameter, match="does not exist"):
            _find_crucible(str(tmp_path / "nope"))

    def test_env_var(self, tmp_path, monkeypatch):
        d = tmp_path / "env-crucible"
        d.mkdir()
        monkeypatch.setenv("CRUCIBLE_PATH", str(d))
        assert _find_crucible(None) == d

    def test_env_var_bad_path(self, monkeypatch, tmp_path):
        import click
        import metricforge.cli.initialize as init_mod
        monkeypatch.setenv("CRUCIBLE_PATH", "/nonexistent/path")
        # Point __file__ somewhere without a sibling Crucible folder
        monkeypatch.setattr(init_mod, "__file__", str(tmp_path / "a" / "b" / "c" / "d" / "init.py"))
        with pytest.raises(click.UsageError, match="Cannot locate"):
            _find_crucible(None)


# ── init command ──────────────────────────────────────────────────


class TestInitCommand:

    def test_init_creates_project(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        result = runner.invoke(cli, [
            "init",
            "--name", "test-proj",
            "--dw", "duckdb",
            "--sl", "cube",
            "--path", str(out_dir),
            "--crucible", str(fake_crucible),
            "--no-git",
        ])
        assert result.exit_code == 0, result.output
        proj = out_dir / "test-proj"
        assert (proj / "metricforge.yaml").exists()
        assert (proj / "docker-compose.yml").exists()

    def test_init_with_support_pipeline(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        result = runner.invoke(cli, [
            "init",
            "--name", "pipe-proj",
            "--dw", "duckdb",
            "--sl", "cube",
            "--path", str(out_dir),
            "--crucible", str(fake_crucible),
            "--support-software", "zendesk",
            "--no-git",
        ])
        assert result.exit_code == 0, result.output
        proj = out_dir / "pipe-proj"
        assert (proj / "Pipeline-Casts" / "Support" / "zendesk").exists()

    def test_init_with_git(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        result = runner.invoke(cli, [
            "init",
            "--name", "git-proj",
            "--dw", "duckdb",
            "--sl", "cube",
            "--path", str(out_dir),
            "--crucible", str(fake_crucible),
            "--git",
        ])
        assert result.exit_code == 0, result.output
        assert (out_dir / "git-proj" / ".git").exists()


# ── add-pipeline command ──────────────────────────────────────────


class TestAddPipelineCommand:

    def _init_project(self, runner, out_dir, fake_crucible):
        """Helper to create a project first."""
        runner.invoke(cli, [
            "init",
            "--name", "ap-proj",
            "--dw", "duckdb",
            "--sl", "cube",
            "--path", str(out_dir),
            "--crucible", str(fake_crucible),
            "--no-git",
        ])
        return out_dir / "ap-proj"

    def test_add_pipeline(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        proj = self._init_project(runner, out_dir, fake_crucible)

        result = runner.invoke(cli, [
            "add-pipeline",
            "--area", "sales",
            "--software", "salesforce",
            "--path", str(proj),
            "--crucible", str(fake_crucible),
        ])
        assert result.exit_code == 0, result.output
        assert "Added sales pipeline" in result.output

        # Config should be updated
        cfg = yaml.safe_load((proj / "metricforge.yaml").read_text(encoding="utf-8"))
        assert "sales" in cfg.get("pipelines", {})

    def test_add_duplicate_pipeline(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        proj = self._init_project(runner, out_dir, fake_crucible)

        # Add support/zendesk pipeline first
        runner.invoke(cli, [
            "add-pipeline", "--area", "support", "--software", "zendesk",
            "--path", str(proj), "--crucible", str(fake_crucible),
        ])
        # Try to add the same one again
        result = runner.invoke(cli, [
            "add-pipeline", "--area", "support", "--software", "zendesk",
            "--path", str(proj), "--crucible", str(fake_crucible),
        ])
        assert result.exit_code == 0
        assert "already exists" in result.output

    def test_add_pipeline_no_config(self, tmp_path, fake_crucible):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "add-pipeline", "--area", "support", "--software", "zendesk",
            "--path", str(tmp_path), "--crucible", str(fake_crucible),
        ])
        assert result.exit_code != 0


# ── build command ─────────────────────────────────────────────────


class TestBuildCommand:

    def test_build_no_compose_file(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "build", "--path", str(tmp_path),
        ])
        assert result.exit_code != 0

    @patch("subprocess.run")
    def test_build_all(self, mock_run, tmp_path):
        (tmp_path / "docker-compose.yml").write_text("version: '3'", encoding="utf-8")
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        result = runner.invoke(cli, [
            "build", "--path", str(tmp_path), "--service", "all",
        ])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        assert "docker" in mock_run.call_args[0][0][0]

    @patch("subprocess.run")
    def test_build_single_service(self, mock_run, tmp_path):
        (tmp_path / "docker-compose.yml").write_text("version: '3'", encoding="utf-8")
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        result = runner.invoke(cli, [
            "build", "--path", str(tmp_path), "--service", "orchestration",
        ])
        assert result.exit_code == 0
        assert "orchestration" in mock_run.call_args[0][0]

    @patch("subprocess.run")
    def test_build_failure(self, mock_run, tmp_path):
        (tmp_path / "docker-compose.yml").write_text("version: '3'", encoding="utf-8")
        mock_run.return_value = MagicMock(returncode=1)
        runner = CliRunner()
        result = runner.invoke(cli, [
            "build", "--path", str(tmp_path),
        ])
        assert result.exit_code != 0


# ── status command ────────────────────────────────────────────────


class TestStatusCommand:

    def test_status_no_config(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "status", "--path", str(tmp_path),
        ])
        assert result.exit_code != 0

    def test_status_basic(self, tmp_path, fake_crucible):
        # Create a project first
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        runner.invoke(cli, [
            "init", "--name", "stat-proj", "--dw", "duckdb", "--sl", "cube",
            "--path", str(out_dir), "--crucible", str(fake_crucible), "--no-git",
        ])
        proj = out_dir / "stat-proj"

        result = runner.invoke(cli, ["status", "--path", str(proj)])
        assert result.exit_code == 0
        assert "stat-proj" in result.output

    def test_status_json_output(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        runner.invoke(cli, [
            "init", "--name", "json-proj", "--dw", "duckdb", "--sl", "cube",
            "--path", str(out_dir), "--crucible", str(fake_crucible), "--no-git",
        ])
        proj = out_dir / "json-proj"

        result = runner.invoke(cli, ["status", "--path", str(proj), "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["project_name"] == "json-proj"
        assert "checks" in data

    def test_status_checks_main_py(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        runner.invoke(cli, [
            "init", "--name", "chk-proj", "--dw", "duckdb", "--sl", "cube",
            "--path", str(out_dir), "--crucible", str(fake_crucible), "--no-git",
        ])
        proj = out_dir / "chk-proj"

        result = runner.invoke(cli, ["status", "--path", str(proj), "--json-output"])
        data = json.loads(result.output)
        # Orchestration/Main.py should exist (copied from Crucible)
        assert data["checks"]["orchestration"] is True


# ── upgrade command ───────────────────────────────────────────────


class TestUpgradeCommand:

    def test_upgrade_no_config(self, tmp_path, fake_crucible):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "upgrade", "--path", str(tmp_path), "--crucible", str(fake_crucible),
        ])
        assert result.exit_code != 0

    def test_upgrade_preserves_config(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        runner.invoke(cli, [
            "init", "--name", "upg-proj", "--dw", "duckdb", "--sl", "cube",
            "--path", str(out_dir), "--crucible", str(fake_crucible), "--no-git",
        ])
        proj = out_dir / "upg-proj"

        # Write a custom .env
        (proj / ".env").write_text("MY_SECRET=keepme", encoding="utf-8")

        result = runner.invoke(cli, [
            "upgrade", "--path", str(proj), "--crucible", str(fake_crucible),
        ])
        assert result.exit_code == 0
        assert "upgraded" in result.output.lower() or "Upgraded" in result.output

        # .env should be preserved
        assert (proj / ".env").read_text(encoding="utf-8") == "MY_SECRET=keepme"

    def test_upgrade_dry_run(self, tmp_path, fake_crucible):
        runner = CliRunner()
        out_dir = tmp_path / "projects"
        out_dir.mkdir()
        runner.invoke(cli, [
            "init", "--name", "dry-proj", "--dw", "duckdb", "--sl", "cube",
            "--path", str(out_dir), "--crucible", str(fake_crucible), "--no-git",
        ])
        proj = out_dir / "dry-proj"

        result = runner.invoke(cli, [
            "upgrade", "--path", str(proj), "--crucible", str(fake_crucible), "--dry-run",
        ])
        assert result.exit_code == 0
        assert "dry-run" in result.output.lower()
