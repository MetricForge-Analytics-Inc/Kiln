# Installation & Setup Guide

## Prerequisites

- **Python 3.11+** — `python --version`
- **pip** (comes with Python)
- **Docker Desktop** (optional, for containerized services)
- **Crucible repo** — Kiln reads source files from the sibling `Crucible/` directory at scaffold time

## Step 1: Install Kiln

From the Kiln directory (editable install):

```bash
pip install -e .
```

For the provisioning API:

```bash
pip install -e ".[api]"
```

## Step 2: Create a Project

Interactive:

```bash
metricforge init
```

Non-interactive:

```bash
metricforge init --name my-platform --dw duckdb --sl cube \
  --support-software zendesk
```

Kiln auto-detects the sibling `Crucible/` directory. Override with `--crucible /path/to/Crucible` or set `CRUCIBLE_PATH`.

## Step 3: Configure

```bash
cd my-platform
cp .env.example .env    # fill in credentials
```

Key sections in `metricforge.yaml`:
- `data_warehouse.config` — database connection details
- `semantic_layer.config` — BI tool settings
- `pipelines` — which business areas and vendors to run

Credentials always go in environment variables or `.env`, never in YAML.

## Step 4: Run

```bash
# Start Docker services (Cube, Evidence, etc.)
docker compose up -d

# Run the pipeline
python Orchestration/Main.py
```

Default service URLs:
- **Cube Playground**: http://localhost:4000
- **Evidence dashboards**: http://localhost:3000
- **Cube SQL API**: localhost:15432

## Adding Pipelines Later

```bash
metricforge add-pipeline --area sales --software salesforce
```

## Upgrading from Newer Crucible

```bash
metricforge upgrade          # re-copies Crucible files, preserves .env + config
metricforge upgrade --dry-run  # preview only
```

## Troubleshooting

### Crucible not found

```
Cannot locate the Crucible repository.
```

Fix: set `--crucible`, `CRUCIBLE_PATH` env var, or place Crucible alongside Kiln.

### Python version

```bash
python --version  # Should be 3.11+
```

### Docker issues

```bash
docker ps                         # verify Docker is running
docker compose up -d              # start services
docker compose logs orchestration # check logs
```

### Missing provider packages

```bash
pip install duckdb                        # DuckDB
pip install snowflake-connector-python    # Snowflake
pip install google-cloud-bigquery         # BigQuery
```
