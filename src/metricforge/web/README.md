# MetricForge Crucible Web UI

Streamlit-based web interface for MetricForge Crucible, providing a visual way to:
- Initialize new data platform projects
- Configure existing projects
- Explore available providers and options

## Running the Web UI

### Quick Start
```bash
./web_ui.sh
```

Or explicitly:
```bash
python web_ui.py
```

The web UI will open at **http://localhost:8501**

## Structure

- **app.py** - Main Streamlit application with all pages
- **pages/** - Future location for multi-page app components
- **config.toml** - Streamlit configuration (.streamlit/config.toml)

## Features

### Home Page
Overview of available data warehouses and semantic layers, plus unified stack information.

### Initialize Project
Visual wizard to create a new MetricForge project:
- Project name and slug
- Data warehouse selection
- Semantic layer selection
- Advanced options (Docker, examples, etc.)

Generates complete project structure in seconds.

### Configure Project
Management interface for YAML configurations:
- Upload existing configurations
- View and edit configurations
- Generate new configurations from scratch
- Download configurations for external editing

## Requirements

All dependencies are managed in the root `requirements.txt`:
- streamlit >= 1.28.0
- streamlit-option-menu >= 0.3.0
- All MetricForge framework dependencies

## Architecture

The web UI shares the same backend as the CLI:
- **Shared Providers**: `metricforge.providers.data_warehouse` and `metricforge.providers.semantic_layer`
- **Shared Configuration**: `metricforge.utils.config`
- **Shared Initialization**: `metricforge.utils.init`

This ensures both interfaces generate identical project structures and configurations.

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
streamlit run src/metricforge/web/app.py --server.port 8502
```

### Dependencies Not Installed
```bash
pip install -r requirements.txt
# or just install Streamlit if it's missing
pip install streamlit streamlit-option-menu
```

### Module Import Errors
Ensure you're running from the project root directory:
```bash
cd /path/to/MetricForge-Crucible
./web_ui.sh
```
