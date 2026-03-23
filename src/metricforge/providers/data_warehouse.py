"""Data warehouse provider implementations."""

from typing import Any, Dict, Optional
import os

from .base import DataWarehouseProvider, ConnectionConfig


class DuckDBLocalProvider(DataWarehouseProvider):
    """
    Local DuckDB file-based data warehouse.
    
    Configuration:
        database_path: Path to .duckdb file (default: ./db/metricforge.duckdb)
    """
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.database_path = config.config.get('database_path', './db/metricforge.duckdb')
        os.makedirs(os.path.dirname(self.database_path) or '.', exist_ok=True)
    
    def validate_connection(self) -> bool:
        """Validate DuckDB file is accessible."""
        try:
            import duckdb
            conn = duckdb.connect(self.database_path, read_only=False)
            conn.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"DuckDB connection failed: {e}")
            return False
    
    def get_connection_string(self) -> str:
        """Return DuckDB connection string."""
        return f"duckdb:///{self.database_path}"
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Return DuckDB environment variables for DLT and other tools."""
        return {
            "DUCKDB_DATABASE": self.database_path,
            "DUCKDB_PATH": self.database_path,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Local DuckDB doesn't need a Docker service."""
        return None


class MotherDuckProvider(DataWarehouseProvider):
    """
    MotherDuck cloud data warehouse.
    
    Configuration:
        motherduck_token: Authentication token (can use MD_TOKEN env var)
        database: Database name (default: 'metricforge')
    """
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.motherduck_token = config.config.get(
            'motherduck_token',
            os.getenv('MD_TOKEN', '')
        )
        self.database = config.config.get('database', 'metricforge')
    
    def validate_connection(self) -> bool:
        """Validate MotherDuck connection."""
        if not self.motherduck_token:
            print("MotherDuck token not provided. Set MD_TOKEN env var or provide motherduck_token in config.")
            return False
        
        try:
            import duckdb
            conn_str = f"md://{self.database}"
            conn = duckdb.connect(conn_str, motherduck_token=self.motherduck_token)
            conn.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"MotherDuck connection failed: {e}")
            return False
    
    def get_connection_string(self) -> str:
        """Return MotherDuck connection string."""
        return f"motherduck:///{self.database}"
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Return MotherDuck environment variables."""
        return {
            "MOTHERDUCK_TOKEN": self.motherduck_token,
            "DUCKDB_DATABASE": f"md://{self.database}",
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """MotherDuck is cloud-based, no Docker service needed."""
        return None


class SnowflakeProvider(DataWarehouseProvider):
    """
    Snowflake enterprise cloud data warehouse.
    
    Configuration:
        account: Snowflake account identifier
        user: Snowflake username
        password: Snowflake password (or use SNOWFLAKE_PASSWORD env var)
        warehouse: Warehouse name
        database: Database name
        schema: Schema name
    """
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.account = config.config.get('account')
        self.user = config.config.get('user')
        self.password = config.config.get('password', os.getenv('SNOWFLAKE_PASSWORD', ''))
        self.warehouse = config.config.get('warehouse', 'COMPUTE_WH')
        self.database = config.config.get('database', 'METRICFORGE')
        self.schema = config.config.get('schema', 'PUBLIC')
    
    def validate_connection(self) -> bool:
        """Validate Snowflake connection."""
        if not all([self.account, self.user, self.password]):
            print("Snowflake connection requires account, user, and password")
            return False
        
        try:
            import snowflake.connector
            conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
            )
            conn.cursor().execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"Snowflake connection failed: {e}")
            return False
    
    def get_connection_string(self) -> str:
        """Return Snowflake connection string."""
        return f"snowflake://{self.user}:{self.password}@{self.account}/{self.database}/{self.schema}"
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Return Snowflake environment variables."""
        return {
            "SNOWFLAKE_ACCOUNT": self.account,
            "SNOWFLAKE_USER": self.user,
            "SNOWFLAKE_PASSWORD": self.password,
            "SNOWFLAKE_WAREHOUSE": self.warehouse,
            "SNOWFLAKE_DATABASE": self.database,
            "SNOWFLAKE_SCHEMA": self.schema,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Snowflake is cloud-based, no Docker service needed."""
        return None


class BigQueryProvider(DataWarehouseProvider):
    """
    Google BigQuery data warehouse.
    
    Configuration:
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID
        credentials_path: Path to service account JSON (or use GOOGLE_APPLICATION_CREDENTIALS)
    """
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.project_id = config.config.get('project_id')
        self.dataset_id = config.config.get('dataset_id', 'metricforge')
        self.credentials_path = config.config.get(
            'credentials_path',
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        )
    
    def validate_connection(self) -> bool:
        """Validate BigQuery connection."""
        if not self.project_id:
            print("BigQuery requires project_id")
            return False
        
        try:
            from google.cloud import bigquery
            # Credentials are handled via GOOGLE_APPLICATION_CREDENTIALS or ADC
            client = bigquery.Client(project=self.project_id)
            client.get_dataset(self.dataset_id)
            return True
        except Exception as e:
            print(f"BigQuery connection failed: {e}")
            return False
    
    def get_connection_string(self) -> str:
        """Return BigQuery connection string."""
        return f"bigquery://{self.project_id}/{self.dataset_id}"
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Return BigQuery environment variables."""
        env = {
            "GCP_PROJECT_ID": self.project_id,
            "BIGQUERY_DATASET": self.dataset_id,
        }
        if self.credentials_path:
            env["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
        return env
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """BigQuery is cloud-based, no Docker service needed."""
        return None


# Provider registry
DATA_WAREHOUSE_PROVIDERS = {
    'duckdb_local': DuckDBLocalProvider,
    'motherduck': MotherDuckProvider,
    'snowflake': SnowflakeProvider,
    'bigquery': BigQueryProvider,
}


def get_data_warehouse_provider(provider_type: str, config: ConnectionConfig) -> DataWarehouseProvider:
    """Factory function to create data warehouse provider instances."""
    provider_class = DATA_WAREHOUSE_PROVIDERS.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unknown data warehouse provider: {provider_type}")
    return provider_class(config)
