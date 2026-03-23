# Configuration Reference

Complete guide to all configuration options in MetricForge projects.

## Basic Configuration

### metricforge.yaml Structure

```yaml
# Project metadata
project_name: MyDataPlatform
organization: MyOrganization

# Data warehouse configuration
data_warehouse:
  type: duckdb_local|motherduck|snowflake|bigquery
  config:
    # Provider-specific options

# Semantic layer configuration
semantic_layer:
  type: cube_oss|cube_cloud|looker|metabase|superset
  config:
    # Provider-specific options

# Feature flags
include_docker: true|false
include_tests: true|false
include_cicd: true|false
```

## Data Warehouse Configurations

### DuckDB Local

Local file-based SQLite-like database. Best for development.

```yaml
data_warehouse:
  type: duckdb_local
  config:
    database_path: ./db/metricforge.duckdb
```

**Pros:**
- Zero setup, no external dependencies
- Perfect for development and testing
- Smallest possible footprint
- Works on all platforms

**Cons:**
- Not suitable for concurrent access
- Limited to single machine
- No built-in redundancy

**Requirements:**
- DuckDB Python package (included in requirements.txt)

---

### MotherDuck

Managed DuckDB in the cloud. Same SQL dialect as local DuckDB but hosted.

```yaml
data_warehouse:
  type: motherduck
  config:
    database: metricforge_prod
    # motherduck_token: xxx (optional, can use MD_TOKEN env var)
```

**Environment Variables:**
```bash
export MD_TOKEN="your_motherduck_token"
```

**Pros:**
- Fully managed service
- Automatic scaling
- No infrastructure to maintain
- Same DuckDB SQL dialect

**Cons:**
- Requires paid account
- Internet connection required
- Data on external servers

**Setup:**
1. Create [MotherDuck account](https://motherduck.com)
2. Generate API token
3. Set `MD_TOKEN` environment variable

---

### Snowflake

Enterprise cloud data warehouse.

```yaml
data_warehouse:
  type: snowflake
  config:
    account: xy12345.us-east-1
    user: datalake_user
    warehouse: COMPUTE_WH
    database: ANALYTICS
    schema: PUBLIC
    # password: xxx (optional, can use SNOWFLAKE_PASSWORD env var)
```

**Environment Variables:**
```bash
export SNOWFLAKE_PASSWORD="your_password"
```

**Pros:**
- Enterprise-ready
- Excellent performance
- Built-in security and compliance
- Extensive third-party integrations

**Cons:**
- Significant cost
- Complexity in configuration
- Requires account setup

**Setup:**
1. Create [Snowflake account](https://www.snowflake.com)
2. Create warehouse, database, and schema
3. Create user with appropriate permissions
4. Update configuration with account identifiers

---

### BigQuery

Google Cloud native data warehouse.

```yaml
data_warehouse:
  type: bigquery
  config:
    project_id: my-gcp-project-id
    dataset_id: metricforge
    # credentials_path: ./credentials.json (optional, can use GOOGLE_APPLICATION_CREDENTIALS)
```

**Environment Variables:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

**Pros:**
- Serverless, no infrastructure
- Integrates with Google Cloud ecosystem
- Excellent for large datasets
- Pay-per-query pricing

**Cons:**
- GCP vendor lock-in
- Complex IAM setup
- Query cost varies by data scanned

**Setup:**
1. Create [GCP project](https://cloud.google.com)
2. Enable BigQuery API
3. Create service account with BigQuery permissions
4. Download service account JSON
5. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

---

## Semantic Layer Configurations

### Cube.js OSS

Open-source, locally hosted semantic layer.

```yaml
semantic_layer:
  type: cube_oss
  config:
    port: 4000
    sql_port: 15432
    api_secret: metricforge-local-dev-secret
    image: cubejs/cube:v1.3  # Optional: specify version
```

**Ports:**
- `4000`: Web Playground UI and REST API
- `15432`: SQL API (Postgres-compatible wire protocol)

**Pros:**
- Open source, no licensing fees
- Full control, self-hosted
- Feature parity with Cloud version
- Excellent for development

**Cons:**
- Requires Docker
- You manage infrastructure
- Limited SLAs
- Operational overhead

**Getting Started:**
```bash
docker compose up -d

# Now visit:
# http://localhost:4000 (Playground)
# Connect via SQL: localhost:15432 (psql client)
```

---

### Cube Cloud

SaaS version managed by Cube. Same features as OSS but hosted.

```yaml
semantic_layer:
  type: cube_cloud
  config:
    deploy_id: your-deployment-id
    api_endpoint: https://api.cubecloudapp.com
    # api_token: xxx (optional, can use CUBE_CLOUD_TOKEN env var)
```

**Environment Variables:**
```bash
export CUBE_CLOUD_TOKEN="your_token"
```

**Pros:**
- Fully managed service
- Automatic scaling
- Built-in security and monitoring
- No infrastructure overhead

**Cons:**
- Requires paid subscription
- Vendor lock-in
- Limited customization

---

### Looker

Google Cloud BI platform.

```yaml
semantic_layer:
  type: looker
  config:
    instance_url: https://myinstance.cloud.looker.com
    client_id: xxx
    # client_secret: xxx (optional, can use env var)
    api_version: "4.0"
```

**Environment Variables:**
```bash
export LOOKER_INSTANCE_URL="https://..."
export LOOKER_CLIENT_ID="..."
export LOOKER_CLIENT_SECRET="..."
```

**Pros:**
- Enterprise BI platform
- Deep integration with GCP
- Advanced analytics features
- Strong governance

**Cons:**
- Premium pricing
- Steep learning curve
- Complex setup

---

### Metabase

Open-source BI tool, can self-host via Docker.

```yaml
semantic_layer:
  type: metabase
  config:
    port: 3000
    admin_email: admin@metricforge.local
    admin_password: changeme
    database_url: postgres://user:pass@postgres:5432/metabase
```

**Pros:**
- Simple UI, easy for users
- Open source
- Quick to set up
- Great for small teams

**Cons:**
- Limited advanced features
- Requires Postgres for metadata
- Smaller ecosystem

---

### Apache Superset

Open-source BI and data visualization.

```yaml
semantic_layer:
  type: superset
  config:
    port: 8088
    admin_username: admin
    admin_password: admin
    secret_key: metricforge-dev-key
```

**Pros:**
- Rich visualization library
- Open source
- Modern web interface
- Good for dashboards

**Cons:**
- Steeper learning curve
- Requires more setup
- Feature evolution pace

---

## Common Environment Variables

These can be used across all configurations:

```bash
# Logging
LOG_LEVEL=info          # debug, info, warning, error

# Prefect orchestration
PREFECT_API_URL=http://localhost:4200/api
PREFECT_API_KEY=xxx

# SQLMesh
SQLMESH_ENVIRONMENT=dev  # dev, staging, prod

# DLT
DLT_SECRETS_TOML_PATH=.dlt/secrets.toml

# Python
PYTHONUNBUFFERED=1     # Prevent output buffering
```

---

## Configuration Management

### Loading Configuration

```python
from metricforge.utils import MetricForgeConfig

# Load from file
config = MetricForgeConfig('metricforge.yaml')

# Access providers
dw_provider = config.get_data_warehouse_provider()
sl_provider = config.get_semantic_layer_provider()

# Export as dict/yaml/json
config_dict = config.to_dict()
config.save('metricforge-backup.yaml', format='yaml')
```

### Environment Variable Precedence

1. Environment variables (highest priority)
2. `.env` file
3. `metricforge.yaml` config file
4. Default values from provider classes

### Secrets Management

Never commit secrets to git:

```bash
# Add to .gitignore
echo "metricforge.yaml" >> .gitignore
echo ".env" >> .gitignore
echo "credentials.json" >> .gitignore
```

Use environment variables for sensitive data:

```yaml
# metricforge.yaml - don't include secrets
data_warehouse:
  type: snowflake
  config:
    account: xy12345.us-east-1
    user: datalake_user
    # password omitted - use SNOWFLAKE_PASSWORD env var
```

---

## Provider Selection Guide

### Scenarios and Recommendations

| Scenario | DW | Semantic | Notes |
|----------|----|-----------  |-------|
| **Local development** | DuckDB Local | Cube OSS | Zero cost, no setup |
| **Managed cloud** | MotherDuck | Cube Cloud | Fast setup, moderate cost |
| **Enterprise PII** | Snowflake | Looker | Best for regulated data |
| **GCP-native** | BigQuery | Superset | Tight GCP integration |
| **Cost-conscious** | DuckDB Local | Metabase | Free/minimal cost |
| **POC/Testing** | DuckDB Local or MotherDuck | Metabase | Fast iteration |

---

## Validation and Debugging

### Test Connection

```python
from metricforge.utils import MetricForgeConfig

config = MetricForgeConfig()
dw = config.get_data_warehouse_provider()

if dw.validate_connection():
    print("✅ DW connection OK")
    print(f"Connection string: {dw.get_connection_string()}")
else:
    print("❌ DW connection failed")

sl = config.get_semantic_layer_provider()
if sl.validate_connection():
    print("✅ Semantic layer connection OK")
    print(f"UI: {sl.get_ui_endpoints()}")
else:
    print("❌ Semantic layer connection failed")
```

### Check Environment Variables

```python
import os
from metricforge.utils import MetricForgeConfig

config = MetricForgeConfig()
dw = config.get_data_warehouse_provider()

env_vars = dw.get_environment_vars()
for key, value in env_vars.items():
    print(f"{key}={os.getenv(key, '(not set)')}")
```

---

## Next Steps

- [Quick Start Guide](../README.md#quick-start)
- [Provider Development Guide](./PROVIDER_DEVELOPMENT.md)
- [Example Configurations](../examples/)
