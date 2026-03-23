"""Semantic layer provider implementations."""

from typing import Any, Dict, Optional
import os
import yaml

from .base import SemanticLayerProvider, DataWarehouseProvider, ConnectionConfig


class CubeOSSProvider(SemanticLayerProvider):
    """
    Cube.js OSS (Open Source) semantic layer.
    
    Runs locally in Docker. Requires Docker Compose.
    
    Configuration:
        port: Port for Playground UI (default: 4000)
        sql_port: Port for SQL API (default: 15432)
        api_secret: API secret (default: 'metricforge-local-dev-secret')
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        super().__init__(config, dw_provider)
        self.port = config.config.get('port', 4000)
        self.sql_port = config.config.get('sql_port', 15432)
        self.api_secret = config.config.get('api_secret', 'metricforge-local-dev-secret')
        self.image = config.config.get('image', 'cubejs/cube:v1.3')
    
    def validate_connection(self) -> bool:
        """Check if Cube instance is running."""
        try:
            import requests
            resp = requests.get(
                f"http://localhost:{self.port}/cubejs-api/v1/meta",
                headers={"Authorization": self.api_secret},
                timeout=5
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Cube OSS connection check failed (this is normal if not running): {e}")
            return False
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for orchestration tools."""
        dw_env = self.dw_provider.get_environment_vars()
        
        env = {
            "CUBE_DB_TYPE": self._get_cube_db_type(),
            "CUBE_API_SECRET": self.api_secret,
            "CUBE_DEV_MODE": "true",
            "CUBE_PORT": str(self.port),
            "CUBE_SQL_PORT": str(self.sql_port),
            **dw_env
        }
        
        # Add data warehouse-specific Cube environment variables
        if isinstance(self.dw_provider, type(self)):  # Duck typing for DuckDB
            env["CUBE_DB_HOST"] = self.dw_provider.database_path
        
        return env
    
    def _get_cube_db_type(self) -> str:
        """Map data warehouse provider to Cube DB type."""
        provider_class_name = self.dw_provider.__class__.__name__
        
        mapping = {
            'DuckDBLocalProvider': 'duckdb',
            'MotherDuckProvider': 'duckdb',
            'SnowflakeProvider': 'snowflake',
            'BigQueryProvider': 'bigquery',
        }
        
        return mapping.get(provider_class_name, 'duckdb')
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Return Docker Compose service for Cube OSS."""
        dw_env = self.dw_provider.get_environment_vars()
        
        # Build environment for Docker
        environment = {
            "CUBEJS_DB_TYPE": self._get_cube_db_type(),
            "CUBEJS_API_SECRET": self.api_secret,
            "CUBEJS_DEV_MODE": "true",
            "CUBEJS_EXTERNAL_DEFAULT": "true",
            "CUBEJS_SCHEMA_PATH": "model",
            "CUBEJS_PG_SQL_PORT": str(self.sql_port),
        }
        
        # Add data warehouse environment variables with CUBEJS prefix
        for key, value in dw_env.items():
            # Map to Cube environment variable naming
            cube_key = key.replace('DUCKDB_', 'CUBEJS_DB_DUCKDB_').replace('MOTHERDUCK_', 'CUBEJS_')
            environment[cube_key] = value
        
        return {
            "cube": {
                "image": self.image,
                "ports": [f"{self.port}:4000", f"{self.sql_port}:15432"],
                "environment": environment,
                "volumes": [
                    "./cube-models:/cube/conf/model:ro",
                    "../db:/cube/db",
                ],
            }
        }
    
    def get_ui_endpoints(self) -> Dict[str, str]:
        """Get Cube UI endpoints."""
        return {
            "playground": f"http://localhost:{self.port}",
            "docs": f"http://localhost:{self.port}/docs",
        }
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Cube API endpoints."""
        return {
            "rest": f"http://localhost:{self.port}/cubejs-api/v1",
            "sql": f"localhost:{self.sql_port}",
        }


class CubeCloudProvider(SemanticLayerProvider):
    """
    Cube Cloud SaaS semantic layer.
    
    Managed service hosted by Cube. Requires account and deployment.
    
    Configuration:
        api_endpoint: Cube Cloud API endpoint
        deploy_id: Deployment ID
        api_token: API token (can use CUBE_CLOUD_TOKEN env var)
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        super().__init__(config, dw_provider)
        self.api_endpoint = config.config.get('api_endpoint', 'https://api.cubecloudapp.com')
        self.deploy_id = config.config.get('deploy_id')
        self.api_token = config.config.get('api_token', os.getenv('CUBE_CLOUD_TOKEN'))
    
    def validate_connection(self) -> bool:
        """Validate Cube Cloud API connection."""
        if not self.api_token:
            print("Cube Cloud token not provided. Set CUBE_CLOUD_TOKEN env var.")
            return False
        
        try:
            import requests
            resp = requests.get(
                f"{self.api_endpoint}/v1/status",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Cube Cloud connection failed: {e}")
            return False
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for Cube Cloud."""
        return {
            "CUBE_CLOUD_DEPLOY_ID": self.deploy_id,
            "CUBE_CLOUD_API_TOKEN": self.api_token,
            "CUBE_CLOUD_API_ENDPOINT": self.api_endpoint,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Cube Cloud is managed, no Docker service needed."""
        return None
    
    def get_ui_endpoints(self) -> Dict[str, str]:
        """Get Cube Cloud endpoints."""
        return {
            "dashboard": f"{self.api_endpoint}/deployments/{self.deploy_id}",
        }
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Cube Cloud API endpoints."""
        return {
            "api": f"{self.api_endpoint}/v1",
        }


class LookerProvider(SemanticLayerProvider):
    """
    Looker (Google Cloud) semantic layer.
    
    Configuration:
        instance_url: Looker instance URL
        client_id: OAuth 2.0 client ID
        client_secret: OAuth 2.0 client secret
        api_version: Looker API version (default: '4.0')
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        super().__init__(config, dw_provider)
        self.instance_url = config.config.get('instance_url')
        self.client_id = config.config.get('client_id')
        self.client_secret = config.config.get('client_secret')
        self.api_version = config.config.get('api_version', '4.0')
    
    def validate_connection(self) -> bool:
        """Validate Looker API connection."""
        if not all([self.instance_url, self.client_id, self.client_secret]):
            print("Looker requires instance_url, client_id, and client_secret")
            return False
        
        try:
            import requests
            auth_url = f"{self.instance_url}/api/{self.api_version}/login"
            resp = requests.post(
                auth_url,
                json={"client_id": self.client_id, "client_secret": self.client_secret},
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Looker connection failed: {e}")
            return False
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for Looker."""
        return {
            "LOOKER_INSTANCE_URL": self.instance_url,
            "LOOKER_CLIENT_ID": self.client_id,
            "LOOKER_CLIENT_SECRET": self.client_secret,
            "LOOKER_API_VERSION": self.api_version,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Looker is managed, no Docker service needed."""
        return None
    
    def get_ui_endpoints(self) -> Dict[str, str]:
        """Get Looker UI endpoints."""
        return {
            "instance": self.instance_url,
        }
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Looker API endpoints."""
        return {
            "api": f"{self.instance_url}/api/{self.api_version}",
        }


class MetabaseProvider(SemanticLayerProvider):
    """
    Metabase open source BI tool.
    
    Can run locally in Docker or self-hosted.
    
    Configuration:
        port: Port for Metabase UI (default: 3000)
        database_url: Postgres database URL for Metabase metadata
        admin_email: Admin user email
        admin_password: Admin user password
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        super().__init__(config, dw_provider)
        self.port = config.config.get('port', 3000)
        self.database_url = config.config.get('database_url', 'postgres://metabase:password@postgres:5432/metabase')
        self.admin_email = config.config.get('admin_email', 'admin@metricforge.local')
        self.admin_password = config.config.get('admin_password')
        self.image = config.config.get('image', 'metabase/metabase:latest')
    
    def validate_connection(self) -> bool:
        """Check if Metabase is running."""
        try:
            import requests
            resp = requests.get(f"http://localhost:{self.port}/api/health", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"Metabase connection check failed (normal if not running): {e}")
            return False
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for Metabase."""
        return {
            "MB_DB_TYPE": "postgres",
            "MB_DB_CONNECTION_POOL_SIZE": "15",
            "MB_ADMIN_EMAIL": self.admin_email,
            "MB_ADMIN_PASSWORD": self.admin_password or "changeme",
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Return Docker Compose services for Metabase + Postgres."""
        return {
            "postgres": {
                "image": "postgres:15-alpine",
                "environment": {
                    "POSTGRES_DB": "metabase",
                    "POSTGRES_USER": "metabase",
                    "POSTGRES_PASSWORD": "password",
                },
                "volumes": ["metabase-postgres-data:/var/lib/postgresql/data"],
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready -U metabase"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5,
                },
            },
            "metabase": {
                "image": self.image,
                "ports": [f"{self.port}:3000"],
                "environment": {
                    "MB_DB_TYPE": "postgres",
                    "MB_DB_HOST": "postgres",
                    "MB_DB_PORT": "5432",
                    "MB_DB_NAME": "metabase",
                    "MB_DB_USER": "metabase",
                    "MB_DB_PASS": "password",
                    "MB_ADMIN_EMAIL": self.admin_email,
                    "MB_ADMIN_PASSWORD": self.admin_password or "changeme",
                },
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                },
            },
        }
    
    def get_ui_endpoints(self) -> Dict[str, str]:
        """Get Metabase UI endpoints."""
        return {
            "ui": f"http://localhost:{self.port}",
        }
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Metabase API endpoints."""
        return {
            "api": f"http://localhost:{self.port}/api",
        }


class SupersetProvider(SemanticLayerProvider):
    """
    Apache Superset open source BI tool.
    
    Can run locally in Docker or self-hosted.
    
    Configuration:
        port: Port for Superset UI (default: 8088)
        admin_username: Admin username (default: 'admin')
        admin_password: Admin password
        secret_key: Flask secret key
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        super().__init__(config, dw_provider)
        self.port = config.config.get('port', 8088)
        self.admin_username = config.config.get('admin_username', 'admin')
        self.admin_password = config.config.get('admin_password', 'admin')
        self.secret_key = config.config.get('secret_key', 'metricforge-dev-key')
        self.image = config.config.get('image', 'apache/superset:latest')
    
    def validate_connection(self) -> bool:
        """Check if Superset is running."""
        try:
            import requests
            resp = requests.get(f"http://localhost:{self.port}/health", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"Superset connection check failed (normal if not running): {e}")
            return False
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for Superset."""
        return {
            "SUPERSET_ADMIN_USERNAME": self.admin_username,
            "SUPERSET_ADMIN_PASSWORD": self.admin_password,
            "SECRET_KEY": self.secret_key,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Return Docker Compose service for Superset."""
        return {
            "superset": {
                "image": self.image,
                "ports": [f"{self.port}:8088"],
                "environment": {
                    "SUPERSET_ADMIN_USERNAME": self.admin_username,
                    "SUPERSET_ADMIN_PASSWORD": self.admin_password,
                    "SECRET_KEY": self.secret_key,
                    "SUPERSET_CONFIG_PATH": "/etc/superset/superset_config.py",
                },
                "volumes": [
                    "./superset-config:/etc/superset",
                ],
            }
        }
    
    def get_ui_endpoints(self) -> Dict[str, str]:
        """Get Superset UI endpoints."""
        return {
            "ui": f"http://localhost:{self.port}",
        }
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Superset API endpoints."""
        return {
            "api": f"http://localhost:{self.port}/api/v1",
        }


# Provider registry
SEMANTIC_LAYER_PROVIDERS = {
    'cube_oss': CubeOSSProvider,
    'cube_cloud': CubeCloudProvider,
    'looker': LookerProvider,
    'metabase': MetabaseProvider,
    'superset': SupersetProvider,
}


def get_semantic_layer_provider(
    provider_type: str,
    config: ConnectionConfig,
    dw_provider: DataWarehouseProvider
) -> SemanticLayerProvider:
    """Factory function to create semantic layer provider instances."""
    provider_class = SEMANTIC_LAYER_PROVIDERS.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unknown semantic layer provider: {provider_type}")
    return provider_class(config, dw_provider)
