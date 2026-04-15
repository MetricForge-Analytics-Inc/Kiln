# MetricForge Kiln

Lightweight CLI that scaffolds client data platform projects from [Crucible](../Crucible/) — the reference implementation.

## How It Works

Kiln does **not** duplicate Crucible's source files. At scaffold time it:

1. Renders a small set of `.j2` templates (config, docker-compose, env, README, orchestration)
2. Copies everything else (Dockerfiles, SQL models, pipelines, dashboards) directly from Crucible
3. Parameterizes the copied files — replaces `Foundry.` references with the client's project slug and sets the correct DLT destination

The result is a standalone project directory the client can version-control, build, and deploy independently.

## Quick Start

```bash
pip install -e .          # from the Kiln directory
metricforge init          # interactive prompts
```

Or non-interactive:

```bash
metricforge init --name my-platform --dw duckdb --sl cube \
  --support-software zendesk --sales-software salesforce
```

Then:

```bash
cd my-platform
cp .env.example .env      # fill in credentials
docker compose up -d
python Orchestration/Support-Main.py
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `metricforge init` | Scaffold a new project |
| `metricforge add-pipeline` | Add a business area pipeline to an existing project |
| `metricforge build` | Build Docker images (`docker compose build`) |
| `metricforge upgrade` | Re-copy Crucible files + re-render templates (preserves `.env` and `metricforge.yaml`) |
| `metricforge status` | Health check: file presence, Docker services, last pipeline metrics |
| `metricforge serve` | Start the FastAPI provisioning API |

## Architecture

Kiln is intentionally thin. All domain logic lives in Crucible.

```
Crucible (source of truth)          Kiln (scaffolding tool)
├── Orchestration/                  ├── templates/          # 7 .j2 files
├── Pipeline-Casts/                 │   ├── metricforge.yaml.j2
│   ├── Support/zendesk/            │   ├── docker-compose.yml.j2
│   ├── Support/salesforce/         │   ├── .env.example.j2
│   ├── Sales/zendesk/              │   ├── README.md.j2
│   └── Sales/salesforce/           │   └── ...
├── Semantic-Cubes/                 ├── cli/                # Click commands
├── Visualization/                  ├── providers/          # DW + SL abstractions
└── ...                             ├── utils/              # template engine, config
                                    └── api.py              # optional FastAPI service
```

### What lives where

| Concern | Location |
|---------|----------|
| Prefect flows, DLT pipelines, SQLMesh models, Cube definitions, Evidence dashboards | **Crucible** — copied at scaffold time |
| Per-client config (project name, DW type, SL type, feature flags) | **Kiln templates** — rendered at scaffold time |
| Provider abstractions (connection validation, env vars, Docker services) | **Kiln providers/** |
| CI/CD workflow | **Kiln templates/.github/** — copied as static file |

## Configuration

Generated projects use `metricforge.yaml`:

```yaml
project_name: my-platform
organization: MyOrg

data_warehouse:
  type: duckdb_local        # duckdb_local | motherduck | snowflake | bigquery
  config:
    database_path: ./db/metricforge.duckdb

semantic_layer:
  type: cube_oss             # cube_oss | cube_cloud | looker | metabase | superset
  config:
    port: 4000
    sql_port: 15432

pipelines:
  support:
    software: zendesk        # zendesk | salesforce
  sales:
    software: salesforce
```

Credentials go in environment variables or `.env` — never in `metricforge.yaml`.

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for all provider options.

## Provisioning API

For website/automation integration:

```bash
pip install -e ".[api]"
metricforge serve --port 8000
```

Endpoints:
- `POST /projects` — create a project
- `GET /projects/{name}` — status check
- `POST /projects/{name}/pipelines` — add a pipeline
- `POST /projects/{name}/upgrade` — upgrade from latest Crucible
- `DELETE /projects/{name}` — remove a project

## Security

- No hardcoded secrets — API secrets and passwords are generated per-scaffold or read from env vars
- API path traversal protection on all endpoints
- Subprocess calls use list args (no `shell=True`)
- Error responses don't leak filesystem paths

## Documentation

- [Installation](INSTALL.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Provider Development](docs/PROVIDER_DEVELOPMENT.md)
- [Examples](examples/)
- [Contributing](CONTRIBUTING.md)
