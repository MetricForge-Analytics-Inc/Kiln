# Installation & Setup Guide

Quick start guide for MetricForge Crucible.

## Prerequisites

- **Python 3.11+** - Check: `python --version`
- **Git** - Check: `git --version`
- **Docker Desktop** (optional, needed for local services) - Check: `docker --version`
- **pip** (comes with Python)

## Method 1: Using Copier CLI (Recommended)

This is the easiest way to get started.

### 1. Install Copier

```bash
pip install copier
```

### 2. Create New Project

```bash
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git /path/to/my-project
```

### 3. Answer Interactive Questions

The tool will ask you:
- Project name
- Data warehouse (DuckDB local, MotherDuck, Snowflake, BigQuery)
- Semantic layer (Cube OSS, Cube Cloud, Looker, Metabase, Superset)
- Additional features

### 4. Navigate and Install

```bash
cd /path/to/my-project
pip install -r requirements.txt
```

### 5. Configure

Edit `metricforge.yaml` with your specific settings:

```bash
nano metricforge.yaml  # or use your editor
```

### 6. Run!

```bash
python Foundry-Orchestration/main.py
```

## Method 2: Using Web UI (Browser-Based) 🌐

For a visual, interactive interface:

### 1. Clone Repository

```bash
git clone https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git
cd MetricForge-Crucible
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch Web UI

```bash
./web_ui.sh
# or: python web_ui.py
```

The web UI will open automatically at **http://localhost:8501**

### 4. Initialize or Configure Project

**Initialize**: Use the "Initialize Project" tab to create a new data platform
**Configure**: Use the "Configure Project" tab to edit existing YAML configurations

### 5. Next Steps

Once you've created a project:
```bash
cd <your-project-slug>
pip install -r requirements.txt
python Foundry-Orchestration/main.py
```

## Method 3: Fork and Customize

For more control, fork the template and customize manually.

### 1. Fork Repository

- Go to https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible
- Click "Fork" button
- Clone your fork: `git clone https://github.com/YOUR_USERNAME/MetricForge-Crucible.git`

### 2. Choose Template Files

Copy an example configuration from `examples/`:

```bash
cp examples/duckdb_cube_oss.yaml metricforge.yaml
# or
cp examples/motherduck_cube_cloud.yaml metricforge.yaml
```

### 3. Customize

Edit files for your needs:
- `metricforge.yaml` - Configuration
- `Foundry-Pipelines/` - Data extraction and transformation
- `Foundry-Semantic-Cubes/` - Semantic models

### 4. Installation

```bash
pip install -r requirements.txt
```

## Method 2: Fork and Customize

For more control, fork the template and customize manually.

Verify everything is working:

```python
python -c "
from metricforge.utils import MetricForgeConfig

config = MetricForgeConfig()
dw = config.get_data_warehouse_provider()

print('✓ Data Warehouse:', dw.provider_name)
if dw.validate_connection():
    print('✓ Connection successful')
else:
    print('✗ Connection failed - check metricforge.yaml')
"
```

## Next Steps

1. **Edit Configuration**
   - `metricforge.yaml` with credentials
   - Set environment variables for sensitive data

2. **Start Services**
   ```bash
   docker compose up -d  # If using Docker-based services
   ```

3. **Run Pipeline**
   ```bash
   python Foundry-Orchestration/main.py
   ```

4. **Access UI**
   - Cube OSS: http://localhost:4000
   - Metabase: http://localhost:3000
   - Superset: http://localhost:8088

## Troubleshooting

### Python Version

```bash
python --version  # Should be 3.11+

# If using multiple versions:
python3.11 -m pip install copier
python3.11 -c "from copier import run_copy; ..."
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
python3.11 -m pip install -r requirements.txt
```

### Windows

Use PowerShell as Administrator:
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install
pip install copier
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git C:\path\to\project
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
pip install copier
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
