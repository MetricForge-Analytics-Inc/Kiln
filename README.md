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

### Option 1: CLI (Command Line)

Install MetricForge Crucible:
```bash
pip install metricforge-crucible
```

Create a new project:
```bash
metricforge init
```

Answer the interactive prompts to choose your:
- Project name
- Data warehouse (DuckDB, MotherDuck, Snowflake, BigQuery)
- Semantic layer (Cube.js, Looker, Metabase, Superset)

### After Project Creation

Navigate to your new project and configure it:

```bash
cd my-project
pip install -r requirements.txt
python Crucible-Orchestration/main.py
```

### Manual Configuration

For advanced use cases or fine-grained control:
1. Fork [MetricForge-Crucible](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible)
2. Edit `metricforge.yaml` with your choices
3. Customize pipeline code
4. Deploy!

## 🌐 Usage

The CLI provides an interactive experience for guided project setup with the underlying **provider framework** handling all connection and configuration details.

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
4. Add to CLI choices in `src/metricforge/cli/initialize.py`
5. Create example configuration in `examples/` directory
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
