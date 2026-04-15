# Quick Reference Card

## MetricForge Crucible - One-Page Reference

### Installation

```bash
pip install metricforge-crucible
```

### Create New Project

**Interactive CLI**:
```bash
metricforge init
```

**Run Project**:
```bash
cd my-project
python Orchestration/main.py
```

---

### Data Warehouse Options

| Option | Type | Setup Time | Cost | Best For |
|--------|------|-----------|------|----------|
| **DuckDB** | File-based | <1 min | Free | Development, testing |
| **MotherDuck** | Cloud | 10 min | Low ($) | Small teams, managed |
| **Snowflake** | Enterprise DW | 30 min | High ($$) | Large enterprises |
| **BigQuery** | Serverless | 20 min | Low-Mid ($) | GCP-native |

### Semantic Layer Options

| Option | Type | Setup Time | Cost | Best For |
|--------|------|-----------|------|----------|
| **Cube** | Open-source | <1 min | Free | Development, self-hosted |
| **Cube Cloud** | Managed SaaS | 15 min | Low ($) | Managed experience |
| **Looker** | Enterprise BI | 45 min | High ($$) | Enterprises, deep analytics |
| **Metabase** | Open-source BI | 5 min | Free | Simple, user-friendly |
| **Superset** | Open-source BI | 10 min | Free | Modern dashboards |

### Configuration File Format

```yaml
project_name: MyProject
organization: MyOrg

data_warehouse:
  type: duckdb_local|motherduck|snowflake|bigquery
  config:
    # Provider-specific options

semantic_layer:
  type: cube_oss|cube_cloud|looker|metabase|superset
  config:
    # Provider-specific options

include_docker: true|false
include_tests: true|false
include_cicd: true|false
```

### Popular Combinations

**💰 Cheapest - Free**
```yaml
data_warehouse: duckdb_local
semantic_layer: cube_oss  # or metabase, superset
```

**⚡ Fastest Development**
```yaml
data_warehouse: duckdb_local
semantic_layer: metabase
```

**☁️ Managed Cloud**
```yaml
data_warehouse: motherduck
semantic_layer: cube_cloud
```

**🏢 Enterprise**
```yaml
data_warehouse: snowflake
semantic_layer: looker
```

**🚀 GCP-Native**
```yaml
data_warehouse: bigquery
semantic_layer: superset
```

### Project Structure

```
my-project/
  ├── Pipeline-Casts/          # Data extraction & quality
  ├── Orchestration/      # Prefect workflows
  ├── Semantic-Cubes/     # BI model definitions
  ├── Visualization/      # Dashboards & reports
  ├── Documentation/              # Architecture & guides
  ├── metricforge.yaml           # Project configuration
  ├── requirements.txt           # Python dependencies
  └── .dockerignore             # Docker exclusions
```

### Managing Credentials

#### Option 1: Environment Variables (Recommended)

```bash
export MD_TOKEN="your_motherduck_token"
export CUBE_CLOUD_TOKEN="your_cube_token"
export SNOWFLAKE_PASSWORD="your_password"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

#### Option 2: .env File

```bash
cat > .env << EOF
MD_TOKEN=your_motherduck_token
CUBE_CLOUD_TOKEN=your_cube_token
SNOWFLAKE_PASSWORD=your_password
EOF

# Load it
set -a
source .env
set +a
```

#### Option 3: metricforge.yaml (Insecure - Don't!)

```bash
# Never put secrets in metricforge.yaml!
# Always add metricforge.yaml to .gitignore
echo "metricforge.yaml" >> .gitignore
```

### Common Commands

```bash
# Run pipeline
python Orchestration/main.py

# Start semantic layer services
docker compose up -d

# Check data warehouse connection
python -c "from metricforge.utils import MetricForgeConfig; \
config = MetricForgeConfig(); \
print(config.get_data_warehouse_provider().validate_connection())"

# View generated structure
tree -L 2

# Edit configuration
nano metricforge.yaml

# Stop services
docker compose down
```

### After Project Creation

1. **Edit metricforge.yaml** - Add your credentials
2. **Set environment variables** - For sensitive data
3. **docker compose up** - Start services (if using Docker-based)
4. **python Orchestration/main.py** - Run pipeline
5. **Visit UI** - Access semantic layer dashboard

### Semantic Layer URLs (Default Ports)

- **Cube OSS**: http://localhost:4000
- **Metabase**: http://localhost:3000
- **Superset**: http://localhost:8088
- **Cube SQL API**: localhost:15432 (Postgres compatible)

### Quick Troubleshooting

**Port already in use**
```bash
lsof -i :4000  # Find what's using port
kill -9 <PID>  # Kill the process
# Or change port in metricforge.yaml
```

**Docker not running**
```bash
docker ps  # Check if Docker daemon is running
docker compose up -d  # Start services
```

**Connection failed**
```bash
# Verify credentials
cat metricforge.yaml | grep -A5 "data_warehouse"

# Test connection
python -c "from metricforge.utils import MetricForgeConfig; \
MetricForgeConfig().get_data_warehouse_provider().validate_connection()"
```

**Module not found**
```bash
pip install -r requirements.txt
# Or for specific provider:
pip install duckdb  # For DuckDB
pip install snowflake-connector-python  # For Snowflake
pip install google-cloud-bigquery  # For BigQuery
```

### Documentation Links

- 📖 [Installation Guide](INSTALL.md)
- ⚙️ [Configuration Reference](docs/CONFIGURATION.md)
- 🔧 [Provider Development](docs/PROVIDER_DEVELOPMENT.md)
- 💡 [Examples](examples/)
- 🤝 [Contributing](CONTRIBUTING.md)

### Support

- **Issues**: https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/issues
- **Discussions**: https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/discussions
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
