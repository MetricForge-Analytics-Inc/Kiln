"""Tests for MetricForgeConfig and create_default_config."""

import json
import pytest
import yaml

from metricforge.utils.config import MetricForgeConfig, create_default_config


class TestMetricForgeConfig:
    """Tests for MetricForgeConfig class."""

    def test_load_yaml(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        assert cfg.config["project_name"] == "test-project"
        assert cfg.config["data_warehouse"]["type"] == "duckdb_local"

    def test_load_json(self, tmp_path, sample_config_dict):
        p = tmp_path / "config.json"
        p.write_text(json.dumps(sample_config_dict), encoding="utf-8")
        cfg = MetricForgeConfig(str(p))
        assert cfg.config["project_name"] == "test-project"

    def test_load_unsupported_format(self, tmp_path):
        p = tmp_path / "config.toml"
        p.write_text("x = 1", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported config file format"):
            MetricForgeConfig(str(p))

    def test_nonexistent_file_gives_empty_config(self, tmp_path):
        cfg = MetricForgeConfig(str(tmp_path / "missing.yaml"))
        assert cfg.config == {}

    def test_to_dict(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert d["project_name"] == "test-project"

    def test_to_yaml(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        text = cfg.to_yaml()
        parsed = yaml.safe_load(text)
        assert parsed["project_name"] == "test-project"

    def test_to_json(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        text = cfg.to_json()
        parsed = json.loads(text)
        assert parsed["project_name"] == "test-project"

    def test_save_yaml(self, config_yaml_file, tmp_path):
        cfg = MetricForgeConfig(str(config_yaml_file))
        out = tmp_path / "saved.yaml"
        cfg.save(str(out), format="yaml")
        loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert loaded["project_name"] == "test-project"

    def test_save_json(self, config_yaml_file, tmp_path):
        cfg = MetricForgeConfig(str(config_yaml_file))
        out = tmp_path / "saved.json"
        cfg.save(str(out), format="json")
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert loaded["project_name"] == "test-project"

    def test_save_unsupported_format(self, config_yaml_file, tmp_path):
        cfg = MetricForgeConfig(str(config_yaml_file))
        with pytest.raises(ValueError, match="Unsupported format"):
            cfg.save(str(tmp_path / "out.txt"), format="csv")

    def test_save_default_path(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        cfg.config["project_name"] = "modified"
        cfg.save()
        reloaded = MetricForgeConfig(str(config_yaml_file))
        assert reloaded.config["project_name"] == "modified"

    def test_validate_config_missing_keys(self, tmp_path):
        p = tmp_path / "empty.yaml"
        p.write_text(yaml.dump({"project_name": "x"}), encoding="utf-8")
        cfg = MetricForgeConfig(str(p))
        with pytest.raises(ValueError, match="Missing required config keys"):
            cfg._validate_config()

    def test_validate_config_passes(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        cfg._validate_config()  # should not raise

    def test_get_pipelines(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        pipes = cfg.get_pipelines()
        assert "support" in pipes
        assert pipes["support"]["software"] == "zendesk"

    def test_get_pipelines_empty(self, tmp_path):
        p = tmp_path / "no_pipes.yaml"
        p.write_text(yaml.dump({"project_name": "x"}), encoding="utf-8")
        cfg = MetricForgeConfig(str(p))
        assert cfg.get_pipelines() == {}

    def test_add_pipeline(self, config_yaml_file):
        cfg = MetricForgeConfig(str(config_yaml_file))
        cfg.add_pipeline("sales", "salesforce")
        assert cfg.config["pipelines"]["sales"] == {"software": "salesforce"}

    def test_add_pipeline_creates_section(self, tmp_path):
        p = tmp_path / "no_pipes.yaml"
        p.write_text(yaml.dump({"project_name": "x"}), encoding="utf-8")
        cfg = MetricForgeConfig(str(p))
        cfg.add_pipeline("support", "zendesk")
        assert cfg.config["pipelines"]["support"] == {"software": "zendesk"}


class TestCreateDefaultConfig:
    """Tests for the create_default_config factory."""

    def test_basic_creation(self):
        cfg = create_default_config("my-project", "duckdb_local", "cube_oss")
        assert cfg.config["project_name"] == "my-project"
        assert cfg.config["data_warehouse"]["type"] == "duckdb_local"
        assert cfg.config["semantic_layer"]["type"] == "cube_oss"

    def test_custom_dw_config(self):
        dw_cfg = {"database_path": "/custom/path.duckdb"}
        cfg = create_default_config("p", "duckdb_local", "cube_oss", dw_config=dw_cfg)
        assert cfg.config["data_warehouse"]["config"]["database_path"] == "/custom/path.duckdb"

    def test_custom_sl_config(self):
        sl_cfg = {"port": 9999}
        cfg = create_default_config("p", "duckdb_local", "cube_oss", sl_config=sl_cfg)
        assert cfg.config["semantic_layer"]["config"]["port"] == 9999

    def test_default_dw_configs(self):
        for dw_type in ["duckdb_local", "motherduck", "snowflake", "bigquery"]:
            cfg = create_default_config("p", dw_type, "cube_oss")
            assert isinstance(cfg.config["data_warehouse"]["config"], dict)

    def test_default_sl_configs(self):
        for sl_type in ["cube_oss", "cube_cloud", "metabase", "superset"]:
            cfg = create_default_config("p", "duckdb_local", sl_type)
            assert isinstance(cfg.config["semantic_layer"]["config"], dict)

    def test_organization_kwarg(self):
        cfg = create_default_config("p", "duckdb_local", "cube_oss", organization="Acme")
        assert cfg.config["organization"] == "Acme"

    def test_pipelines_kwarg(self):
        pipes = {"support": {"software": "zendesk"}}
        cfg = create_default_config("p", "duckdb_local", "cube_oss", pipelines=pipes)
        assert cfg.config["pipelines"] == pipes

    def test_unknown_dw_type_gives_empty_defaults(self):
        cfg = create_default_config("p", "unknown_dw", "cube_oss")
        assert cfg.config["data_warehouse"]["config"] == {}
