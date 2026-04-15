"""Tests for the template engine: build_context, render_template, scaffold_project,
context_from_project_config, _replace_foundry_refs, _parameterize_dlt_destination."""

import pytest
from pathlib import Path
from unittest.mock import patch

from metricforge.utils.template_engine import (
    build_context,
    context_from_project_config,
    render_template,
    scaffold_project,
    _replace_foundry_refs,
    _parameterize_dlt_destination,
    _get_kiln_version,
    DW_TYPE_MAP,
    SL_TYPE_MAP,
    _CRUCIBLE_STATIC,
    _CRUCIBLE_PIPELINES,
    TEMPLATES_DIR,
)


# ── build_context ─────────────────────────────────────────────────


class TestBuildContext:

    def test_defaults(self):
        ctx = build_context({})
        assert ctx["project_name"] == "metricforge-project"
        assert ctx["project_slug"] == "metricforge_project"
        assert ctx["dw_type"] == "duckdb_local"
        assert ctx["sl_type"] == "cube_oss"
        assert isinstance(ctx["cube_api_secret"], str)
        assert len(ctx["cube_api_secret"]) > 10

    def test_project_slug_generated(self):
        ctx = build_context({"project_name": "My Cool Project"})
        assert ctx["project_slug"] == "my_cool_project"

    def test_explicit_slug(self):
        ctx = build_context({"project_name": "X", "project_slug": "custom_slug"})
        assert ctx["project_slug"] == "custom_slug"

    def test_areas_populated_from_pipelines(self, sample_build_config):
        ctx = build_context(sample_build_config)
        assert ctx["has_support"] is True
        assert ctx["has_sales"] is False
        assert len(ctx["areas"]) == 1
        assert ctx["areas"][0]["name"] == "support"
        assert ctx["areas"][0]["software"] == "zendesk"

    def test_both_areas(self):
        cfg = {
            "pipelines": {
                "support": {"software": "zendesk"},
                "sales": {"software": "salesforce"},
            },
        }
        ctx = build_context(cfg)
        assert ctx["has_support"] is True
        assert ctx["has_sales"] is True
        assert len(ctx["areas"]) == 2

    def test_no_pipelines(self):
        ctx = build_context({"pipelines": {}})
        assert ctx["areas"] == []
        assert ctx["has_support"] is False
        assert ctx["has_sales"] is False

    def test_include_flags(self):
        ctx = build_context({"include_docker": False, "include_tests": False, "include_cicd": False})
        assert ctx["include_docker"] is False
        assert ctx["include_tests"] is False
        assert ctx["include_cicd"] is False

    def test_kiln_version_present(self):
        ctx = build_context({})
        assert "kiln_version" in ctx


# ── context_from_project_config ───────────────────────────────────


class TestContextFromProjectConfig:

    def test_translates_nested_config(self, sample_config_dict):
        ctx = context_from_project_config(sample_config_dict)
        assert ctx["project_name"] == "test-project"
        assert ctx["dw_type"] == "duckdb_local"
        assert ctx["sl_type"] == "cube_oss"
        assert ctx["has_support"] is True

    def test_defaults_for_empty_config(self):
        ctx = context_from_project_config({})
        assert ctx["project_name"] == "metricforge-project"
        assert ctx["dw_type"] == "duckdb_local"
        assert ctx["sl_type"] == "cube_oss"


# ── render_template ───────────────────────────────────────────────


class TestRenderTemplate:

    def test_render_metricforge_yaml(self):
        ctx = build_context({
            "project_name": "render-test",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
        })
        content = render_template("metricforge.yaml.j2", ctx)
        assert "render-test" in content or "render_test" in content

    def test_render_raises_on_missing_template(self):
        from jinja2 import TemplateNotFound
        with pytest.raises(TemplateNotFound):
            render_template("nonexistent.j2", {})


# ── _replace_foundry_refs ─────────────────────────────────────────


class TestReplaceFoundryRefs:

    def test_replaces_in_sql_files(self, tmp_path):
        d = tmp_path / "Pipeline-Casts"
        d.mkdir()
        f = d / "model.sql"
        f.write_text("SELECT * FROM Foundry.schema.table", encoding="utf-8")
        _replace_foundry_refs(tmp_path, "acme")
        assert f.read_text(encoding="utf-8") == "SELECT * FROM acme.schema.table"

    def test_replaces_in_python_files(self, tmp_path):
        d = tmp_path / "Semantic-Cubes"
        d.mkdir()
        f = d / "cube.py"
        f.write_text("db = 'Foundry.main'", encoding="utf-8")
        _replace_foundry_refs(tmp_path, "client_x")
        assert "client_x.main" in f.read_text(encoding="utf-8")

    def test_replaces_in_yaml_files(self, tmp_path):
        d = tmp_path / "Pipeline-Casts"
        d.mkdir()
        f = d / "config.yaml"
        f.write_text("source: Foundry.raw", encoding="utf-8")
        _replace_foundry_refs(tmp_path, "myproj")
        assert "myproj.raw" in f.read_text(encoding="utf-8")

    def test_skips_nonmatching_extensions(self, tmp_path):
        d = tmp_path / "Pipeline-Casts"
        d.mkdir()
        f = d / "readme.md"
        f.write_text("Foundry.data", encoding="utf-8")
        _replace_foundry_refs(tmp_path, "x")
        assert f.read_text(encoding="utf-8") == "Foundry.data"

    def test_noop_when_no_target_dirs(self, tmp_path):
        _replace_foundry_refs(tmp_path, "x")  # should not raise


# ── _parameterize_dlt_destination ─────────────────────────────────


class TestParameterizeDltDestination:

    def test_replaces_single_quoted(self, tmp_path):
        d = tmp_path / "Pipeline-Casts"
        d.mkdir()
        f = d / "zendesk_pipeline.py"
        f.write_text("dlt.pipeline(destination='motherduck')", encoding="utf-8")
        _parameterize_dlt_destination(tmp_path, "snowflake")
        assert "destination='snowflake'" in f.read_text(encoding="utf-8")

    def test_replaces_double_quoted(self, tmp_path):
        d = tmp_path / "Pipeline-Casts"
        d.mkdir()
        f = d / "salesforce_pipeline.py"
        f.write_text('dlt.pipeline(destination="motherduck")', encoding="utf-8")
        _parameterize_dlt_destination(tmp_path, "bigquery")
        assert 'destination="bigquery"' in f.read_text(encoding="utf-8")

    def test_noop_when_already_correct(self, tmp_path):
        d = tmp_path / "Pipeline-Casts"
        d.mkdir()
        f = d / "test_pipeline.py"
        original = "dlt.pipeline(destination='duckdb')"
        f.write_text(original, encoding="utf-8")
        _parameterize_dlt_destination(tmp_path, "duckdb")
        # motherduck not present, so no replacement
        assert f.read_text(encoding="utf-8") == original

    def test_noop_when_dir_missing(self, tmp_path):
        _parameterize_dlt_destination(tmp_path, "snowflake")  # should not raise


# ── scaffold_project ──────────────────────────────────────────────


class TestScaffoldProject:

    def test_scaffold_creates_files(self, tmp_path, fake_crucible):
        output = tmp_path / "output"
        output.mkdir()
        ctx = build_context({
            "project_name": "scaffold-test",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "pipelines": {"support": {"software": "zendesk"}},
        })
        scaffold_project(output, fake_crucible, ctx)

        # .j2 templates should be rendered (without .j2 extension)
        assert (output / "metricforge.yaml").exists()
        assert (output / "docker-compose.yml").exists()

        # Crucible static files should be copied
        assert (output / "Orchestration" / "Main.py").exists()
        assert (output / "Orchestration" / "Dockerfile").exists()
        assert (output / "Visualization" / "Dockerfile").exists()

        # Pipeline should be copied
        assert (output / "Pipeline-Casts" / "Support" / "zendesk" / "Data-Extract").exists()

    def test_scaffold_replaces_foundry_refs(self, tmp_path, fake_crucible):
        # Put a file with Foundry. refs into the fake crucible pipeline
        stub = fake_crucible / "Pipeline-Casts" / "Support" / "zendesk" / "Data-Extract" / "stub.py"
        stub.write_text("FROM Foundry.raw.tickets", encoding="utf-8")

        output = tmp_path / "output"
        output.mkdir()
        ctx = build_context({
            "project_name": "replace-test",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "pipelines": {"support": {"software": "zendesk"}},
        })
        scaffold_project(output, fake_crucible, ctx)
        copied = output / "Pipeline-Casts" / "Support" / "zendesk" / "Data-Extract" / "stub.py"
        assert "replace_test.raw.tickets" in copied.read_text(encoding="utf-8")

    def test_scaffold_no_pipelines(self, tmp_path, fake_crucible):
        output = tmp_path / "output"
        output.mkdir()
        ctx = build_context({
            "project_name": "no-pipes",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "pipelines": {},
        })
        scaffold_project(output, fake_crucible, ctx)
        # No Pipeline-Casts should exist (none selected)
        assert not (output / "Pipeline-Casts").exists()


# ── Mapping tables ────────────────────────────────────────────────


class TestMappingTables:

    def test_dw_type_map_keys(self):
        expected = {"duckdb", "motherduck", "snowflake", "bigquery"}
        assert set(DW_TYPE_MAP.keys()) == expected

    def test_sl_type_map_keys(self):
        expected = {"cube", "cube-cloud", "looker", "metabase", "superset"}
        assert set(SL_TYPE_MAP.keys()) == expected

    def test_crucible_pipelines_all_combos(self):
        for area in ["support", "sales"]:
            for vendor in ["zendesk", "salesforce"]:
                assert (area, vendor) in _CRUCIBLE_PIPELINES

    def test_crucible_static_has_main_py(self):
        static_dsts = [dst for _, dst in _CRUCIBLE_STATIC]
        assert "Orchestration/Main.py" in static_dsts


# ── _get_kiln_version ─────────────────────────────────────────────


class TestGetKilnVersion:

    def test_returns_version_string(self):
        v = _get_kiln_version()
        assert isinstance(v, str)
        assert v == "0.1.0"
