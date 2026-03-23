# MetricForge Provider Development Guide

This guide explains how to add support for new data warehouse or semantic layer providers in MetricForge Crucible.

## Architecture Overview

MetricForge uses an abstract provider pattern that allows swapping implementations without changing pipeline logic.

### Base Classes

All providers inherit from abstract base classes defined in `src/metricforge/providers/base.py`:

- `DataWarehouseProvider` - Data warehouse implementations
- `SemanticLayerProvider` - BI/semantic layer implementations

### Provider Lifecycle

1. **Initialization** - Provider class instantiated with `ConnectionConfig`
2. **Validation** - `validate_connection()` called to verify connectivity
3. **Configuration** - `get_environment_vars()` and `get_docker_compose_service()` called
4. **Deployment** - Environment variables set, Docker services started if needed
5. **Operation** - Provider instance available to pipeline

## Adding a Data Warehouse Provider

### Step 1: Create Provider Class

Add to `src/metricforge/providers/data_warehouse.py`:

```python
from typing import Any, Dict, Optional
import os
from .base import DataWarehouseProvider, ConnectionConfig


class MyDWProvider(DataWarehouseProvider):
    """
    My custom data warehouse provider.
    
    Configuration:
        host: Database host
        port: Database port
        database: Database name
        credentials: Authentication method
    """
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.host = config.config.get('host')
        self.port = config.config.get('port', 5432)
        self.database = config.config.get('database')
        # ... additional configuration
    
    def validate_connection(self) -> bool:
        """Test database connection."""
        try:
            # Attempt connection
            # Return True if successful
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_connection_string(self) -> str:
        """Return driver-specific connection string."""
        return f"mydw://user:pass@{self.host}:{self.port}/{self.database}"
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Return environment variables for tools like DLT, SQLMesh."""
        return {
            "MYDW_HOST": self.host,
            "MYDW_PORT": str(self.port),
            "MYDW_DATABASE": self.database,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Return Docker service if needed. Return None for managed services."""
        return None  # Cloud service doesn't need Docker
```

### Step 2: Register Provider

In `src/metricforge/providers/data_warehouse.py`, add to the registry:

```python
DATA_WAREHOUSE_PROVIDERS = {
    'duckdb_local': DuckDBLocalProvider,
    'motherduck': MotherDuckProvider,
    'snowflake': SnowflakeProvider,
    'bigquery': BigQueryProvider,
    'mydw': MyDWProvider,  # Add here
}
```

### Step 3: Update Copier Configuration

Add to `copier.yml`:

```yaml
data_warehouse:
  type: str
  help: Choose your primary data warehouse
  default: duckdb_local
  choices:
    duckdb_local: "DuckDB (Local file-based)"
    motherduck: "MotherDuck (Managed DuckDB Cloud)"
    snowflake: "Snowflake (Enterprise cloud DW)"
    bigquery: "BigQuery (Google Cloud)"
    mydw: "My Data Warehouse (Custom)"  # Add here
```

### Step 4: Create Configuration Examples

Add example configurations to `docs/examples/`:

```yaml
# docs/examples/mydw_cube_oss.yaml
project_name: mydw-project
organization: MyOrg

data_warehouse:
  type: mydw
  config:
    host: mydw.example.com
    port: 5432
    database: analytics
    user: analyst
    # password via env var

semantic_layer:
  type: cube_oss
  config:
    port: 4000
```

### Step 5: Add Documentation

Create setup guide: `docs/DATA_WAREHOUSE_SETUP.md`

Include:
- Prerequisites
- Account/credential setup
- Configuration examples
- Common issues and troubleshooting
- Cost/pricing information

## Adding a Semantic Layer Provider

### Step 1: Create Provider Class

Add to `src/metricforge/providers/semantic_layer.py`:

```python
from typing import Any, Dict, Optional
import os
from .base import SemanticLayerProvider, DataWarehouseProvider, ConnectionConfig


class MyBIProvider(SemanticLayerProvider):
    """
    My custom BI/semantic layer provider.
    
    Configuration:
        api_endpoint: BI tool API endpoint
        api_key: Authentication key
        workspace_id: Workspace/account identifier
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        super().__init__(config, dw_provider)
        self.api_endpoint = config.config.get('api_endpoint')
        self.api_key = config.config.get('api_key', os.getenv('MYBI_API_KEY'))
        self.workspace_id = config.config.get('workspace_id')
    
    def validate_connection(self) -> bool:
        """Validate BI tool connection."""
        try:
            import requests
            resp = requests.get(
                f"{self.api_endpoint}/v1/status",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables."""
        return {
            "MYBI_API_ENDPOINT": self.api_endpoint,
            "MYBI_API_KEY": self.api_key,
            "MYBI_WORKSPACE_ID": self.workspace_id,
        }
    
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Cloud service doesn't need Docker."""
        return None
    
    def get_ui_endpoints(self) -> Dict[str, str]:
        """Return UI endpoints."""
        return {
            "dashboard": f"{self.api_endpoint}/workspaces/{self.workspace_id}",
        }
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Return API endpoints."""
        return {
            "api": f"{self.api_endpoint}/v1",
        }
```

### Step 2: Register Provider

In `src/metricforge/providers/semantic_layer.py`:

```python
SEMANTIC_LAYER_PROVIDERS = {
    'cube_oss': CubeOSSProvider,
    'cube_cloud': CubeCloudProvider,
    'looker': LookerProvider,
    'metabase': MetabaseProvider,
    'superset': SupersetProvider,
    'mybi': MyBIProvider,  # Add here
}
```

### Step 3: Update Copier Configuration

Add to `copier.yml`:

```yaml
semantic_layer:
  type: str
  help: Choose your semantic layer
  default: cube_oss
  choices:
    cube_oss: "Cube.js OSS (Open source, Docker-based)"
    cube_cloud: "Cube Cloud (Managed SaaS)"
    looker: "Looker (Google Cloud BI)"
    metabase: "Metabase (Open source BI)"
    superset: "Apache Superset (Open source BI)"
    mybi: "My BI Tool (Custom)"  # Add here
```

### Step 4: Create Documentation

Create setup guide: `docs/SEMANTIC_LAYER_SETUP.md`

Include:
- Prerequisites
- Account/credential setup
- Semantic model configuration
- Authentication details
- Common issues and troubleshooting

## Testing Your Provider

### Unit Tests

Create `tests/providers/test_mybi_provider.py`:

```python
import pytest
from metricforge.providers import get_semantic_layer_provider, ConnectionConfig, DuckDBLocalProvider


def test_mybi_provider_validation():
    """Test BI provider initialization and validation."""
    config = ConnectionConfig(
        provider_type='mybi',
        name='test',
        config={
            'api_endpoint': 'https://api.mybi.com',
            'api_key': 'test-key',
            'workspace_id': 'test-ws',
        }
    )
    
    dw_config = ConnectionConfig(
        provider_type='duckdb_local',
        name='test',
        config={'database_path': ':memory:'}
    )
    
    dw_provider = DuckDBLocalProvider(dw_config)
    provider = get_semantic_layer_provider('mybi', config, dw_provider)
    
    assert provider.provider_name == 'test'
    assert provider.api_endpoint == 'https://api.mybi.com'


def test_environment_variables():
    """Test environment variable generation."""
    # ... test implementation
```

### Integration Tests

Test with actual connections if credentials available:

```python
@pytest.mark.integration
def test_mybi_real_connection():
    """Test real connection to BI tool."""
    # Configure with prod credentials
    # Validate connection
    # Check endpoints
```

## Best Practices

1. **Connection Pooling** - Reuse connections efficiently
2. **Timeout Handling** - Set reasonable timeouts (typically 10-30s)
3. **Error Messages** - Provide helpful error context
4. **Documentation** - Document expected environment variables
5. **Versioning** - Support multiple API versions if needed
6. **Authentication** - Prefer environment variables over hardcoded secrets
7. **Type Hints** - Add proper type hints throughout

## Common Patterns

### Optional Local Docker Service

```python
def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
    """Provide optional local Docker service for development."""
    if not self.should_use_docker():
        return None
    
    return {
        "myservice": {
            "image": "myservice:latest",
            "ports": ["8080:8080"],
            "environment": {...},
        }
    }
```

### Environment Variable Mapping

```python
def get_environment_vars(self) -> Dict[str, str]:
    """Map configuration to tool-specific env vars."""
    dw_env = self.dw_provider.get_environment_vars()
    
    # Transform DW env vars for this tool
    transformed = {
        key.replace('DUCKDB_', 'TOOL_DB_'): value
        for key, value in dw_env.items()
    }
    
    return {**transformed, "TOOL_API_KEY": self.api_key}
```

### Validation with External Calls

```python
def validate_connection(self) -> bool:
    """Validate with actual API call."""
    try:
        client = self.create_client()  # May raise
        client.list_resources()  # May raise
        return True
    except AuthenticationError:
        print("Invalid credentials")
        return False
    except ConnectionError:
        print("Cannot reach service")
        return False
    except Exception as e:
        print(f"Validation failed: {e}")
        return False
```

## Troubleshooting

### Provider Not Loading

1. Check registration in `PROVIDERS` dictionary
2. Verify class name matches expected import
3. Check for circular imports
4. Validate YAML syntax in copier.yml

### Credentials Not Working

1. Print `get_environment_vars()` to verify values
2. Test credentials independently
3. Check for special character escaping
4. Verify environment variable names don't conflict

### Docker Service Issues

1. Validate docker-compose.yaml syntax
2. Check volume paths are correct
3. Ensure port numbers don't conflict
4. Test `docker compose up` independently

## Contributing

Submit new providers via pull request to the main repository:

1. Fork repository
2. Create feature branch: `git checkout -b feature/add-mybi-provider`
3. Add provider class, tests, and documentation
4. Ensure all tests pass: `pytest tests/`
5. Check code style: `black src/ tests/`
6. Submit PR with description

---

For questions, see [Contributing Guide](CONTRIBUTING.md) and [GitHub Discussions](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/discussions).
