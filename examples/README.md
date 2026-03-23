# Quick Start Examples

This directory contains example configurations for popular MetricForge Crucible setups.

## Available Examples

### Development Stack: Everything Local
**File:** `duckdb_cube_oss.yaml`

Best for: Learning, testing, rapid prototyping, tutorials

Stack:
- DuckDB (local file)
- Cube.js OSS (Docker)
- Docker Compose

Cost: Free
Setup Time: < 5 minutes

```bash
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git my-project
# Choose: duckdb_local + cube_oss
```

Then test:
```bash
cd my-project
docker compose up -d
python Foundry-Orchestration/main.py
# Visit http://localhost:4000
```

### Managed Cloud Stack
**File:** `motherduck_cube_cloud.yaml`

Best for: Teams wanting managed services, production readiness, minimal ops

Stack:
- MotherDuck (managed DuckDB cloud)
- Cube Cloud (managed SaaS)

Cost: Moderate ($50-500+/month)
Setup Time: 15-30 minutes

```bash
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git my-project
# Choose: motherduck + cube_cloud
```

Configuration:
```bash
export MD_TOKEN="your_motherduck_token"
export CUBE_CLOUD_TOKEN="your_cube_token"

python Foundry-Orchestration/main.py
```

### Enterprise Stack: Snowflake + Looker
**File:** `snowflake_looker.yaml`

Best for: Large enterprises, regulated data, extensive BI features

Stack:
- Snowflake (enterprise DW)
- Looker (Google Cloud BI)

Cost: Premium (Snowflake: $2+/credit, Looker: $70K+/year)
Setup Time: 1-2 hours

```bash
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git my-project
# Choose: snowflake + looker
```

### GCP-Native Stack: BigQuery + Superset
**File:** `bigquery_superset.yaml`

Best for: GCP environments, serverless, open source BI

Stack:
- BigQuery (serverless DW)
- Apache Superset (open source BI, Docker)

Cost: Low to moderate (BQ pay-per-query, Superset operational cost)
Setup Time: 20-30 minutes

```bash
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git my-project
# Choose: bigquery + superset

export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
docker compose up -d
python Foundry-Orchestration/main.py
# Visit http://localhost:8088
```

---

## Using These Examples

### Method 1: Copy and Modify

1. Pick the example closest to your use case
2. Copy its configuration
3. Customize for your environment
4. Follow setup steps

### Method 2: Reference During Setup

When running `copier copy`, the interactive prompts will guide you through choices similar to these examples.

### Method 3: Post-Generation Customization

After generating a project, replace `metricforge.yaml` with an example configuration and fill in your credentials:

```bash
# Generate project with default config
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git my-project

# Overwrite with example
cp examples/motherduck_cube_cloud.yaml my-project/metricforge.yaml

# Edit with your credentials
nano my-project/metricforge.yaml
```

---

## Common Modifications

### Using a Different Port for Cube OSS

Edit `metricforge.yaml`:
```yaml
semantic_layer:
  type: cube_oss
  config:
    port: 5000  # Change from 4000 to 5000
```

### Changing DuckDB Database Path

```yaml
data_warehouse:
  type: duckdb_local
  config:
    database_path: /data/warehouse/metricforge.duckdb
```

### Pointing to Different Snowflake Warehouse

```yaml
data_warehouse:
  type: snowflake
  config:
    warehouse: PRODUCTION_WH  # Change warehouse
```

---

## Troubleshooting

### Port Already in Use

Find process using the port:
```bash
lsof -i :4000  # For Cube OSS port

# Kill it or change port in metricforge.yaml
```

### Docker Not Running

```bash
# Start Docker Desktop or daemon
docker ps  # Should list running containers

# If not running:
sudo systemctl start docker  # Linux
# or open Docker Desktop GUI
```

### Connection to Data Warehouse Failed

1. Verify credentials in `metricforge.yaml`
2. Check environment variables are set: `echo $MD_TOKEN`
3. Run validation: `python -c "from metricforge.utils import MetricForgeConfig; MetricForgeConfig().get_data_warehouse_provider().validate_connection()"`

### Semantic Layer UI Not Accessible

For Docker-based services:
```bash
# Check if service is running
docker compose ps

# View logs
docker compose logs cube  # Or metabase, superset

# Restart if needed
docker compose restart
```

---

## Next Steps

- [Configuration Reference](../docs/CONFIGURATION.md)
- [Full documentation](../docs/)
- [GitHub Discussions](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/discussions)
