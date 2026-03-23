# MetricForge Crucible - Templated Data Platform

A comprehensive, modular template for building data platforms with flexible architecture choices.

## 🎯 Overview

MetricForge Crucible enables users to generate customized data platforms by choosing from a flexible set of components:

### Data Warehouses
- **DuckDB** (Local) - Best for development and testing
- **MotherDuck** - Managed DuckDB in the cloud
- **Snowflake** - Enterprise cloud data warehouse
- **BigQuery** - Google Cloud data warehouse

### Semantic Layers
- **Cube.js OSS** - Open-source, locally hosted
- **Cube Cloud** - Managed SaaS by Cube
- **Looker** - Google Cloud BI platform
- **Metabase** - Open-source BI tool
- **Apache Superset** - Open-source BI platform

### Core Stack (Unified)
- **Orchestration**: Prefect - workflow orchestration
- **Transformation**: SQLMesh - SQL transformation framework
- **Data Loading**: DLT - data load tool
- **Data Catalog**: Provided by semantic layer

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Data Sources                           │
│        (APIs, Files, Databases, Data Lakes)            │
└────────────────────────┬────────────────────────────────┘
                         │
                    DLT Pipeline
                    (Extract)
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Data Warehouse (User Choice)                   │
│  ├─ DuckDB (Local)                                      │
│  ├─ MotherDuck (Cloud)                                  │
│  ├─ Snowflake                                           │
│  └─ BigQuery                                            │
└────────────────────────┬────────────────────────────────┘
                         │
                    SQLMesh Models
                    (Transform)
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Semantic Layer (User Choice)                   │
│  ├─ Cube.js (OSS)                                       │
│  ├─ Cube Cloud                                          │
│  ├─ Looker                                             │
│  ├─ Metabase                                            │
│  └─ Apache Superset                                     │
└────────────────────────┬────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
      REST API                    Web UI
      & SQL API                  Dashboards
```

## 🚀 Getting Started

### Option 1: Using Copier CLI (Recommended)

Install Copier:
```bash
pip install copier
```

Create new project:
```bash
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git /path/to/new-project
```

Follow the interactive prompts to select:
- Project name
- Data warehouse provider
- Semantic layer provider
- Optional features (testing, CI/CD, LLM agents, etc.)

### Option 2: Using Web UI (Browser-Based)

For a visual, interactive experience:

```bash
# Clone the repository
git clone https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible.git
cd MetricForge-Crucible

# Install dependencies
pip install -r requirements.txt

# Start the web UI
./web_ui.sh
# or: python web_ui.py
```

Then open your browser to `http://localhost:8501` and:
- **Initialize Project** - Visual wizard to create a new project
- **Configure Project** - Upload and edit YAML configurations

### Option 3: Fork the Template

Fork this repository and edit configuration files manually:
1. Fork [MetricForge-Crucible](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible)
2. Edit `metricforge.yaml` with your choices
3. Customize pipeline code
4. Deploy!

## 🌐 Choosing Your Interface

| Interface | Best For | Installation |
|-----------|----------|--------------|
| **CLI (Copier)** | Automation, scripting, CI/CD | `pip install copier` |
| **Web UI (Streamlit)** | Visual interaction, exploring options, team collaboration | Built-in, just run `./web_ui.sh` |
| **Manual Configuration** | Fine-grained control, custom workflows | Fork + edit locally |

All three approaches share the same underlying **provider framework** — choose what works best for your workflow!

## 📦 Provider Framework

MetricForge uses an abstraction layer for providers, making it easy to:
- Add new data warehouse or BI tool support
- Switch providers without changing pipeline logic
- Share configuration across different environments

### Provider Classes

**DataWarehouseProvider** - Handles:
- Connection management
- Environment variable setup
- Docker service configuration
- Connection validation

**SemanticLayerProvider** - Handles:
- Semantic model deployment
- UI/API endpoint configuration
- Authentication setup
- Refresh mechanisms

## 🔧 Configuration

All projects use `metricforge.yaml` for configuration:

```yaml
project_name: MyDataPlatform
organization: MyOrganization

data_warehouse:
  type: duckdb_local
  config:
    database_path: ./db/metricforge.duckdb

semantic_layer:
  type: cube_oss
  config:
    port: 4000
    sql_port: 15432
```

See [Configuration Guide](docs/CONFIGURATION.md) for detailed options for each provider.

## 📚 Documentation

- [Configuration Guide](docs/CONFIGURATION.md) - Detailed provider configuration
- [Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md) - Why certain choices were made
- [Provider Development](docs/PROVIDER_DEVELOPMENT.md) - How to add new providers
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment patterns
- [Examples](examples/) - Sample configurations for popular stacks

## 🏆 Popular Configuration Combinations

### Development Stack
```
DuckDB Local + Cube.js OSS
Perfect for: Learning, testing, rapid prototyping
Cost: Free
```

### Managed Cloud Stack
```
MotherDuck + Cube Cloud
Perfect for: Teams wanting managed services
Cost: Moderate
```

### Enterprise Stack
```
Snowflake + Looker
Perfect for: Large organizations with existing Looker
Cost: Premium
```

### Open Source Stack
```
DuckDB Local + Apache Superset
Perfect for: Cost-conscious teams wanting open source
Cost: Free (self-hosted)
```

## 🔐 Security Considerations

- Credentials stored in environment variables or `.env` files
- Never commit sensitive data to version control
- Use `.gitignore` to exclude database files and config overrides
- Support for cloud provider IAM authentication
- Prefect enables secure workflow execution

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Adding a New Data Warehouse Provider

1. Create provider class in `src/metricforge/providers/data_warehouse.py`
2. Implement `DataWarehouseProvider` interface
3. Register in `DATA_WAREHOUSE_PROVIDERS` dictionary
4. Add to copier.yml choices
5. Create template files for test configurations
6. Add documentation

### Adding a New Semantic Layer Provider

Same pattern as data warehouse providers, but implement `SemanticLayerProvider` interface.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/discussions)
- **Documentation**: [Full Documentation](docs/)

## 🎓 Learning Resources

- [SQLMesh Docs](https://sqlmesh.readthedocs.io/) - SQL transformation framework
- [DLT Docs](https://dlthub.com/docs) - Data loading and extraction
- [Cube.js Docs](https://cube.dev/docs/) - Semantic layer & BI
- [Prefect Docs](https://docs.prefect.io/) - Workflow orchestration
- [Example Projects](examples/README.md) - Ready-to-use configurations

---

**Built with ❤️ by MetricForge Analytics Inc** 
