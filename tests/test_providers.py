"""Tests for data warehouse and semantic layer providers."""

import os
import pytest
from unittest.mock import patch, MagicMock

from metricforge.providers.base import ConnectionConfig, DataWarehouseProvider, SemanticLayerProvider
from metricforge.providers.data_warehouse import (
    DuckDBLocalProvider,
    MotherDuckProvider,
    SnowflakeProvider,
    BigQueryProvider,
    get_data_warehouse_provider,
    DATA_WAREHOUSE_PROVIDERS,
)
from metricforge.providers.semantic_layer import (
    CubeOSSProvider,
    CubeCloudProvider,
    LookerProvider,
    MetabaseProvider,
    SupersetProvider,
    get_semantic_layer_provider,
    SEMANTIC_LAYER_PROVIDERS,
)


# ── Helpers ───────────────────────────────────────────────────────


def _dw_config(provider_type="duckdb_local", **kwargs):
    return ConnectionConfig(provider_type=provider_type, name="test", config=kwargs)


def _duckdb_provider(**kwargs):
    return DuckDBLocalProvider(_dw_config("duckdb_local", **kwargs))


# ── ConnectionConfig ──────────────────────────────────────────────


class TestConnectionConfig:

    def test_creation(self):
        cc = ConnectionConfig(provider_type="duckdb_local", name="test", config={"key": "val"})
        assert cc.provider_type == "duckdb_local"
        assert cc.name == "test"
        assert cc.config["key"] == "val"


# ── Data Warehouse Providers ──────────────────────────────────────


class TestDuckDBLocalProvider:

    def test_connection_string(self, tmp_path):
        db_path = str(tmp_path / "test.duckdb")
        p = _duckdb_provider(database_path=db_path)
        assert p.get_connection_string() == f"duckdb:///{db_path}"

    def test_environment_vars(self, tmp_path):
        db_path = str(tmp_path / "test.duckdb")
        p = _duckdb_provider(database_path=db_path)
        env = p.get_environment_vars()
        assert env["DUCKDB_DATABASE"] == db_path
        assert env["DUCKDB_PATH"] == db_path

    def test_no_docker_service(self, tmp_path):
        p = _duckdb_provider(database_path=str(tmp_path / "x.duckdb"))
        assert p.get_docker_compose_service() is None

    def test_default_database_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        p = _duckdb_provider()
        assert p.database_path == "./db/metricforge.duckdb"


class TestMotherDuckProvider:

    def test_connection_string(self):
        p = MotherDuckProvider(_dw_config("motherduck", motherduck_token="tok", database="mydb"))
        assert p.get_connection_string() == "motherduck:///mydb"

    def test_environment_vars(self):
        p = MotherDuckProvider(_dw_config("motherduck", motherduck_token="tok", database="mydb"))
        env = p.get_environment_vars()
        assert env["MOTHERDUCK_TOKEN"] == "tok"
        assert "md://mydb" in env["DUCKDB_DATABASE"]

    def test_no_docker_service(self):
        p = MotherDuckProvider(_dw_config("motherduck", motherduck_token="tok"))
        assert p.get_docker_compose_service() is None

    def test_validate_no_token(self, monkeypatch):
        monkeypatch.delenv("MD_TOKEN", raising=False)
        p = MotherDuckProvider(_dw_config("motherduck"))
        assert p.validate_connection() is False

    def test_token_from_env(self, monkeypatch):
        monkeypatch.setenv("MD_TOKEN", "env-token")
        p = MotherDuckProvider(_dw_config("motherduck"))
        assert p.motherduck_token == "env-token"


class TestSnowflakeProvider:

    def test_connection_string(self):
        p = SnowflakeProvider(_dw_config("snowflake",
            account="acct", user="usr", password="pw",
            warehouse="WH", database="DB", schema="SCH"))
        assert p.get_connection_string() == "snowflake://usr:pw@acct/DB/SCH"

    def test_environment_vars(self):
        p = SnowflakeProvider(_dw_config("snowflake",
            account="acct", user="usr", password="pw"))
        env = p.get_environment_vars()
        assert env["SNOWFLAKE_ACCOUNT"] == "acct"
        assert env["SNOWFLAKE_USER"] == "usr"
        assert env["SNOWFLAKE_PASSWORD"] == "pw"

    def test_no_docker_service(self):
        p = SnowflakeProvider(_dw_config("snowflake", account="a", user="u", password="p"))
        assert p.get_docker_compose_service() is None

    def test_validate_missing_creds(self):
        p = SnowflakeProvider(_dw_config("snowflake"))
        assert p.validate_connection() is False

    def test_defaults(self):
        p = SnowflakeProvider(_dw_config("snowflake"))
        assert p.warehouse == "COMPUTE_WH"
        assert p.database == "METRICFORGE"
        assert p.schema == "PUBLIC"


class TestBigQueryProvider:

    def test_connection_string(self):
        p = BigQueryProvider(_dw_config("bigquery", project_id="proj", dataset_id="ds"))
        assert p.get_connection_string() == "bigquery://proj/ds"

    def test_environment_vars(self):
        p = BigQueryProvider(_dw_config("bigquery", project_id="proj", dataset_id="ds"))
        env = p.get_environment_vars()
        assert env["GCP_PROJECT_ID"] == "proj"
        assert env["BIGQUERY_DATASET"] == "ds"

    def test_credentials_path_in_env(self):
        p = BigQueryProvider(_dw_config("bigquery", project_id="p", credentials_path="/key.json"))
        env = p.get_environment_vars()
        assert env["GOOGLE_APPLICATION_CREDENTIALS"] == "/key.json"

    def test_no_creds_path_omitted(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
        p = BigQueryProvider(_dw_config("bigquery", project_id="p"))
        env = p.get_environment_vars()
        assert "GOOGLE_APPLICATION_CREDENTIALS" not in env

    def test_no_docker_service(self):
        p = BigQueryProvider(_dw_config("bigquery", project_id="p"))
        assert p.get_docker_compose_service() is None

    def test_validate_no_project(self):
        p = BigQueryProvider(_dw_config("bigquery"))
        assert p.validate_connection() is False


# ── Provider Factory ──────────────────────────────────────────────


class TestDataWarehouseFactory:

    def test_all_registered_types(self):
        expected = {"duckdb_local", "motherduck", "snowflake", "bigquery"}
        assert set(DATA_WAREHOUSE_PROVIDERS.keys()) == expected

    def test_factory_duckdb(self, tmp_path):
        p = get_data_warehouse_provider("duckdb_local",
            _dw_config("duckdb_local", database_path=str(tmp_path / "x.duckdb")))
        assert isinstance(p, DuckDBLocalProvider)

    def test_factory_unknown(self):
        with pytest.raises(ValueError, match="Unknown data warehouse provider"):
            get_data_warehouse_provider("oracle", _dw_config("oracle"))


# ── Semantic Layer Providers ──────────────────────────────────────


def _make_dw():
    """Helper: create a DuckDB provider for SL tests."""
    return DuckDBLocalProvider(ConnectionConfig(
        provider_type="duckdb_local", name="test",
        config={"database_path": "./db/test.duckdb"}
    ))


def _sl_config(sl_type, **kwargs):
    return ConnectionConfig(provider_type=sl_type, name="test", config=kwargs)


class TestCubeOSSProvider:

    def test_defaults(self):
        dw = _make_dw()
        p = CubeOSSProvider(_sl_config("cube_oss"), dw)
        assert p.port == 4000
        assert p.sql_port == 15432

    def test_environment_vars(self):
        dw = _make_dw()
        p = CubeOSSProvider(_sl_config("cube_oss", api_secret="secret123"), dw)
        env = p.get_environment_vars()
        assert env["CUBE_API_SECRET"] == "secret123"
        assert env["CUBE_DB_TYPE"] == "duckdb"

    def test_docker_compose_service(self):
        dw = _make_dw()
        p = CubeOSSProvider(_sl_config("cube_oss", api_secret="s"), dw)
        svc = p.get_docker_compose_service()
        assert "cube" in svc
        assert svc["cube"]["image"].startswith("cubejs/cube")

    def test_ui_endpoints(self):
        dw = _make_dw()
        p = CubeOSSProvider(_sl_config("cube_oss"), dw)
        eps = p.get_ui_endpoints()
        assert "playground" in eps

    def test_api_endpoints(self):
        dw = _make_dw()
        p = CubeOSSProvider(_sl_config("cube_oss"), dw)
        eps = p.get_api_endpoints()
        assert "rest" in eps
        assert "sql" in eps

    def test_cube_db_type_mapping(self):
        for dw_cls, expected in [
            (DuckDBLocalProvider, "duckdb"),
            (MotherDuckProvider, "duckdb"),
            (SnowflakeProvider, "snowflake"),
            (BigQueryProvider, "bigquery"),
        ]:
            if dw_cls == DuckDBLocalProvider:
                dw = _make_dw()
            elif dw_cls == MotherDuckProvider:
                dw = MotherDuckProvider(_dw_config("motherduck", motherduck_token="t"))
            elif dw_cls == SnowflakeProvider:
                dw = SnowflakeProvider(_dw_config("snowflake", account="a", user="u", password="p"))
            else:
                dw = BigQueryProvider(_dw_config("bigquery", project_id="p"))
            p = CubeOSSProvider(_sl_config("cube_oss"), dw)
            assert p._get_cube_db_type() == expected


class TestCubeCloudProvider:

    def test_defaults(self):
        dw = _make_dw()
        p = CubeCloudProvider(_sl_config("cube_cloud"), dw)
        assert p.api_endpoint == "https://api.cubecloudapp.com"

    def test_environment_vars(self):
        dw = _make_dw()
        p = CubeCloudProvider(_sl_config("cube_cloud", api_token="tk", deploy_id="d1"), dw)
        env = p.get_environment_vars()
        assert env["CUBE_CLOUD_API_TOKEN"] == "tk"
        assert env["CUBE_CLOUD_DEPLOY_ID"] == "d1"

    def test_no_docker_service(self):
        dw = _make_dw()
        p = CubeCloudProvider(_sl_config("cube_cloud"), dw)
        assert p.get_docker_compose_service() is None

    def test_validate_no_token(self, monkeypatch):
        monkeypatch.delenv("CUBE_CLOUD_TOKEN", raising=False)
        dw = _make_dw()
        p = CubeCloudProvider(_sl_config("cube_cloud"), dw)
        assert p.validate_connection() is False

    def test_ui_endpoints(self):
        dw = _make_dw()
        p = CubeCloudProvider(_sl_config("cube_cloud", deploy_id="d1"), dw)
        eps = p.get_ui_endpoints()
        assert "d1" in eps["dashboard"]


class TestLookerProvider:

    def test_environment_vars(self):
        dw = _make_dw()
        p = LookerProvider(_sl_config("looker",
            instance_url="https://looker.example.com",
            client_id="cid", client_secret="csec"), dw)
        env = p.get_environment_vars()
        assert env["LOOKER_INSTANCE_URL"] == "https://looker.example.com"
        assert env["LOOKER_CLIENT_ID"] == "cid"
        assert env["LOOKER_API_VERSION"] == "4.0"

    def test_no_docker_service(self):
        dw = _make_dw()
        p = LookerProvider(_sl_config("looker"), dw)
        assert p.get_docker_compose_service() is None

    def test_validate_missing_creds(self):
        dw = _make_dw()
        p = LookerProvider(_sl_config("looker"), dw)
        assert p.validate_connection() is False

    def test_api_endpoints(self):
        dw = _make_dw()
        p = LookerProvider(_sl_config("looker", instance_url="https://l.co"), dw)
        eps = p.get_api_endpoints()
        assert "4.0" in eps["api"]


class TestMetabaseProvider:

    def test_defaults(self):
        dw = _make_dw()
        p = MetabaseProvider(_sl_config("metabase"), dw)
        assert p.port == 3000
        assert p.admin_email == "admin@metricforge.local"

    def test_environment_vars(self):
        dw = _make_dw()
        p = MetabaseProvider(_sl_config("metabase", admin_password="pw"), dw)
        env = p.get_environment_vars()
        assert env["MB_DB_TYPE"] == "postgres"
        assert env["MB_ADMIN_PASSWORD"] == "pw"

    def test_docker_compose_service(self):
        dw = _make_dw()
        p = MetabaseProvider(_sl_config("metabase"), dw)
        svc = p.get_docker_compose_service()
        assert "metabase" in svc
        assert "postgres" in svc

    def test_ui_endpoints(self):
        dw = _make_dw()
        p = MetabaseProvider(_sl_config("metabase"), dw)
        eps = p.get_ui_endpoints()
        assert "3000" in eps["ui"]


class TestSupersetProvider:

    def test_defaults(self):
        dw = _make_dw()
        p = SupersetProvider(_sl_config("superset"), dw)
        assert p.port == 8088
        assert p.admin_username == "admin"

    def test_environment_vars(self, monkeypatch):
        monkeypatch.delenv("SUPERSET_ADMIN_PASSWORD", raising=False)
        monkeypatch.delenv("SUPERSET_SECRET_KEY", raising=False)
        dw = _make_dw()
        p = SupersetProvider(_sl_config("superset", admin_password="pw", secret_key="sk"), dw)
        env = p.get_environment_vars()
        assert env["SUPERSET_ADMIN_PASSWORD"] == "pw"
        assert env["SECRET_KEY"] == "sk"

    def test_docker_compose_service(self):
        dw = _make_dw()
        p = SupersetProvider(_sl_config("superset"), dw)
        svc = p.get_docker_compose_service()
        assert "superset" in svc
        assert "8088" in svc["superset"]["ports"][0]

    def test_ui_endpoints(self):
        dw = _make_dw()
        p = SupersetProvider(_sl_config("superset"), dw)
        eps = p.get_ui_endpoints()
        assert "8088" in eps["ui"]


# ── Semantic Layer Factory ────────────────────────────────────────


class TestSemanticLayerFactory:

    def test_all_registered_types(self):
        expected = {"cube_oss", "cube_cloud", "looker", "metabase", "superset"}
        assert set(SEMANTIC_LAYER_PROVIDERS.keys()) == expected

    def test_factory_cube_oss(self):
        dw = _make_dw()
        p = get_semantic_layer_provider("cube_oss", _sl_config("cube_oss"), dw)
        assert isinstance(p, CubeOSSProvider)

    def test_factory_unknown(self):
        dw = _make_dw()
        with pytest.raises(ValueError, match="Unknown semantic layer provider"):
            get_semantic_layer_provider("tableau", _sl_config("tableau"), dw)
