# Quick Reference

## Install

```bash
pip install -e .                     # from Kiln directory
pip install -e ".[api]"              # with provisioning API
```

## CLI Commands

```bash
metricforge init                     # interactive scaffold
metricforge init --name X --dw duckdb --sl cube --support-software zendesk
metricforge add-pipeline --area sales --software salesforce
metricforge build                    # docker compose build
metricforge upgrade                  # re-copy from Crucible
metricforge upgrade --dry-run        # preview changes
metricforge status                   # health check
metricforge status --json-output     # machine-readable
metricforge serve --port 8000        # start API server
```

## Data Warehouse Options

| Type | Config key | Cost | Best for |
|------|-----------|------|----------|
| DuckDB | `duckdb_local` | Free | Dev/testing |
| MotherDuck | `motherduck` | $ | Small teams |
| Snowflake | `snowflake` | $$$ | Enterprise |
| BigQuery | `bigquery` | $$ | GCP-native |

## Semantic Layer Options

| Type | Config key | Cost | Best for |
|------|-----------|------|----------|
| Cube OSS | `cube_oss` | Free | Self-hosted |
| Cube Cloud | `cube_cloud` | $ | Managed |
| Looker | `looker` | $$$ | Enterprise |
| Metabase | `metabase` | Free | Simple BI |
| Superset | `superset` | Free | Dashboards |

## Project Structure (generated)

```
my-project/
├── Orchestration/          # Prefect flow + trigger
├── Pipeline-Casts/         # DLT extract + SQLMesh transform per area
├── Semantic-Cubes/         # Cube.js YAML definitions
├── Visualization/          # Evidence dashboards + sources
├── .github/workflows/      # CI/CD pipeline
├── metricforge.yaml        # project config
├── docker-compose.yml      # container services
├── .env.example            # credential template
└── README.md               # generated docs
```

## Credentials

Always use environment variables — never put secrets in `metricforge.yaml`.

```bash
# Copy template and fill in
cp .env.example .env

# Or export directly
export MD_TOKEN="..."
export SNOWFLAKE_PASSWORD="..."
export CUBE_CLOUD_TOKEN="..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/creds.json"
```

## Run

```bash
cd my-project
cp .env.example .env              # edit with real values
docker compose up -d              # start services
python Orchestration/Main.py   # run pipeline
```

## Default Ports

| Service | Port |
|---------|------|
| Cube Playground | 4000 |
| Cube SQL API | 15432 |
| Evidence dashboards | 3000 |
| Metabase | 3000 |
| Superset | 8088 |

## Links

- [Installation](INSTALL.md)
- [Configuration](docs/CONFIGURATION.md)
- [Provider Development](docs/PROVIDER_DEVELOPMENT.md)
- [Examples](examples/)
- [Contributing](CONTRIBUTING.md)
- **Docs**: Full documentation in `docs/` directory

### File Structure of Generated Project

```
my-project/
├── metricforge.yaml                 # Your configuration
├── requirements.txt                 # Python dependencies
├── docker-compose.yaml              # Docker services
├── Orchestration/
│   └── main.py                      # Pipeline orchestration
├── Pipeline-Casts/
│   └── [Theme]/[Site]/
│       ├── Data-Extract/            # DLT extraction
│       └── Data-Pipeline/           # SQLMesh transformation
├── Semantic-Cubes/
│   └── models/                      # Semantic models (YAML)
├── Visualization/
│   └── dashboards/                  # BI dashboards
└── Documentation/
    └── examples/                    # Reference configs
```

### Next Steps

1. ✅ Run `metricforge init` to create project
2. ✅ Edit `metricforge.yaml` with your settings
3. ✅ Run `docker compose up` (if using Docker)
4. ✅ Run `python Orchestration/main.py`
5. ✅ Visit semantic layer UI
6. ✅ Create your data pipelines!

---

**Ready to build? Start here**: Run `pip install metricforge-crucible && metricforge init` 🚀
