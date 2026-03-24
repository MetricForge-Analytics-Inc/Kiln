# Installation & Setup Guide

Complete setup guide for MetricForge Crucible.

## Prerequisites

- **Python 3.11+** - Check: `python --version`
- **pip** (comes with Python)
- **Docker Desktop** (optional, for containerized services)

## Step 1: Install MetricForge Crucible

```bash
pip install metricforge-crucible
```

## Step 2: Create Your First Project

Run the interactive CLI to create a new project:

```bash
metricforge init
```

Answer the prompts:
- **Project name**: e.g., `my-analytics-platform`
- **Data warehouse**: duckdb | motherduck | snowflake | bigquery
- **Semantic layer**: cube | cube-cloud | looker | metabase | superset

## Step 3: Configure Your Project

Navigate to your new project:

```bash
cd my-analytics-platform
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Edit the configuration file with your provider credentials:

```bash
nano metricforge.yaml
```

Key sections to configure:
- **data_warehouse.config** - Database credentials/endpoints
- **semantic_layer.config** - BI tool settings and credentials

## Step 4: Run Your Platform

### Start the orchestration engine:

```bash
python Crucible-Orchestration/main.py
```

### Access your semantic layer

The URL depends on your chosen platform:
- **Cube OSS**: http://localhost:4000
- **Metabase**: http://localhost:3000
- **Superset**: http://localhost:8088
- **Looker**: Managed by Google Cloud
- **Cube Cloud**: Managed SaaS

See your project's `README.md` for specific instructions.

## Additional Resources

- **Configuration Details**: See `CONFIGURATION.md` in `/docs`
- **Provider-Specific Setup**: See `PROVIDER_DEVELOPMENT.md` in `/docs`
- **Example Projects**: Check `/examples` directory

## Troubleshooting

### Python Version Issues

```bash
python --version  # Should be 3.11+

# If using multiple versions:
python3.11 -m pip install --upgrade pip
python3.11 -m pip install metricforge-crucible
```

### Missing Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# For specific provider:
pip install duckdb  # For DuckDB
pip install snowflake-connector-python  # For Snowflake
pip install google-cloud-bigquery  # For BigQuery
```

### Docker Issues

```bash
# Check if Docker is running
docker ps

# Pull required images
docker pull cubejs/cube:v1.3
docker pull metabase/metabase:latest
docker pull apache/superset:latest
```

### Connection Issues

1. **Check credentials** in `metricforge.yaml`
2. **Verify environment variables**: `env | grep -i duckdb`
3. **Test connection**:
   ```bash
   python -c "
   from metricforge.utils import MetricForgeConfig
   config = MetricForgeConfig()
   print(config.get_data_warehouse_provider().validate_connection())
   "
   ```

## Platform-Specific Notes

### macOS

Using M1/M2 (ARM64):
```bash
# Some packages may need to be installed from conda
brew install python@3.11
python3.11 -m pip install metricforge-crucible
```

### Windows

Use PowerShell as Administrator:
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install
pip install metricforge-crucible
metricforge init
```

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install metricforge-crucible
```

## Getting Help

- **Documentation**: See [docs/](docs/) directory
- **Examples**: Check [examples/](examples/) for sample configurations
- **Issues**: Open a [GitHub Issue](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/discussions)

## Next: Configure Your Platform

Choose your setup:
- [Development Setup](docs/CONFIGURATION.md#duckdb-local) - DuckDB Local
- [Production Setup](docs/CONFIGURATION.md#motherduck) - MotherDuck + Cube Cloud
- [Enterprise Setup](docs/CONFIGURATION.md#snowflake) - Snowflake + Looker
- [GCP Setup](docs/CONFIGURATION.md#bigquery) - BigQuery + Superset

See [Configuration Reference](docs/CONFIGURATION.md) for detailed options.
