"""Utilities for project initialization and setup."""

from typing import Dict, Any, Optional
from pathlib import Path
import shutil
import textwrap


class ProjectInitializer:
    """Handles initialization of new MetricForge projects."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_path.mkdir(parents=True, exist_ok=True)
    
    def create_directory_structure(self, config: Dict[str, Any]):
        """Create the directory structure for a MetricForge project."""
        directories = [
            'db',
            'Crucible-Pipelines',
            'Crucible-Orchestration',
            'Crucible-Semantic-Cubes',
            'Crucible-Visualization',
            'Documentation',
            '.github/workflows',
            '.sqlmesh',
        ]
        
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
    
    def create_config_file(self, config: Dict[str, Any]):
        """Create metricforge.yaml configuration file."""
        config_content = self._generate_config_yaml(config)
        config_file = self.project_path / 'metricforge.yaml'
        config_file.write_text(config_content)
    
    def _generate_config_yaml(self, config: Dict[str, Any]) -> str:
        """Generate YAML configuration content."""
        # Build YAML content with proper structure
        lines = [
            "# MetricForge Project Configuration",
            "",
            f"project_name: {config.get('project_name', 'metricforge-project')}",
            f"organization: {config.get('organization', 'Organization')}",
            "",
            "# Data Warehouse Configuration",
            "data_warehouse:",
            f"  type: {config.get('data_warehouse_type', 'duckdb_local')}",
            "  config:",
        ]
        
        # Add data warehouse specific config
        dw_type = config.get('data_warehouse_type', 'duckdb_local')
        if dw_type == 'duckdb_local':
            lines.append("    database_path: ./db/metricforge.duckdb")
        elif dw_type == 'motherduck':
            lines.extend([
                "    database: metricforge",
                "    # motherduck_token: <token> # Or set MD_TOKEN env var",
            ])
        elif dw_type == 'snowflake':
            lines.extend([
                "    account: <account>",
                "    user: <username>",
                "    # password: <password> # Or set SNOWFLAKE_PASSWORD env var",
                "    warehouse: COMPUTE_WH",
                "    database: METRICFORGE",
                "    schema: PUBLIC",
            ])
        elif dw_type == 'bigquery':
            lines.extend([
                "    project_id: <gcp-project-id>",
                "    dataset_id: metricforge",
                "    # credentials_path: ./credentials.json # Or set GOOGLE_APPLICATION_CREDENTIALS",
            ])
        
        lines.extend([
            "",
            "# Semantic Layer Configuration",
            "semantic_layer:",
            f"  type: {config.get('semantic_layer_type', 'cube_oss')}",
            "  config:",
        ])
        
        # Add semantic layer specific config
        sl_type = config.get('semantic_layer_type', 'cube_oss')
        if sl_type == 'cube_oss':
            lines.extend([
                "    port: 4000",
                "    sql_port: 15432",
                "    api_secret: metricforge-local-dev-secret",
            ])
        elif sl_type == 'cube_cloud':
            lines.extend([
                "    deploy_id: <deployment-id>",
                "    # api_token: <token> # Or set CUBE_CLOUD_TOKEN env var",
            ])
        elif sl_type == 'looker':
            lines.extend([
                "    instance_url: <looker-instance-url>",
                "    client_id: <client-id>",
                "    # client_secret: <secret>",
            ])
        elif sl_type in ['metabase', 'superset']:
            lines.extend([
                "    port: 3000",
                "    admin_email: admin@metricforge.local",
                "    # admin_password: <password>",
            ])
        
        lines.extend([
            "",
            "# Feature Flags",
            f"include_docker: {str(config.get('include_docker', True)).lower()}",
            f"include_tests: {str(config.get('include_tests', True)).lower()}",
            f"include_cicd: {str(config.get('include_cicd', True)).lower()}",
            "",
        ])
        
        return "\n".join(lines)
    
    def create_dockerignore(self):
        """Create .dockerignore file."""
        content = textwrap.dedent("""
            __pycache__
            *.pyc
            .git
            .gitignore
            .vscode
            .idea
            *.egg-info
            .eggs
            build
            dist
            venv
            env
            .DS_Store
            *.duckdb
        """).strip()
        
        (self.project_path / '.dockerignore').write_text(content)
    
    def create_readme(self, config: Dict[str, Any]):
        """Create initial README.md."""
        project_name = config.get('project_name', 'MetricForge Project')
        dw_type = config.get('data_warehouse_type', 'duckdb_local')
        sl_type = config.get('semantic_layer_type', 'cube_oss')
        
        dw_display = {
            'duckdb_local': 'DuckDB (Local)',
            'motherduck': 'MotherDuck (Cloud)',
            'snowflake': 'Snowflake',
            'bigquery': 'BigQuery',
        }
        
        sl_display = {
            'cube_oss': 'Cube.js OSS',
            'cube_cloud': 'Cube Cloud',
            'looker': 'Looker',
            'metabase': 'Metabase',
            'superset': 'Apache Superset',
        }
        
        content = textwrap.dedent(f"""
            # {project_name}
            
            A modern data platform powered by MetricForge.
            
            ## Architecture
            
            - **Data Warehouse**: {dw_display.get(dw_type, dw_type)}
            - **Semantic Layer**: {sl_display.get(sl_type, sl_type)}
            - **Orchestration**: Prefect
            - **Transformation**: SQLMesh
            - **Data Loading**: DLT (Data Load Tool)
            - **Visualization**: Evidence (or integrated with semantic layer)
            
            ## Configuration
            
            The project is configured via `metricforge.yaml`. Key settings:
            - Data warehouse connection details
            - Semantic layer endpoints
            - Feature flags for Docker, tests, CI/CD
            
            ## Quick Start
            
            ### 1. Install dependencies
            
            ```bash
            pip install -r requirements.txt
            ```
            
            ### 2. Configure your environment
            
            Edit `metricforge.yaml` with your {dw_display.get(dw_type, dw_type)} and {sl_display.get(sl_type, sl_type)} details.
            
            ### 3. Run the pipeline
            
            ```bash
            python Crucible-Orchestration/main.py
            ```
            
            ### 4. Start the semantic layer
            
            ```bash
            cd Crucible-Semantic-Cubes
            docker compose up -d
            ```
            
            Then visit the UI at the configured endpoint.
            
            ## Project Structure
            
            - `Crucible-Pipelines/` - Data extraction, transformation, and quality
            - `Crucible-Orchestration/` - Pipeline orchestration (Prefect)
            - `Crucible-Semantic-Cubes/` - Semantic layer configuration and models
            - `Crucible-Visualization/` - BI dashboards and reports
            - `Documentation/` - Architecture, design decisions, and runbooks
            
            ## Documentation
            
            See `Documentation/` for detailed information on:
            - Architecture overview
            - Provider-specific setup
            - Deployment and scaling
            
            ## Support
            
            For issues or questions, refer to the [MetricForge Crucible](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible) template repository.
        """).strip()
        
        (self.project_path / 'README.md').write_text(content)
    
    def create_example_configs(self):
        """Create example configuration files for different providers."""
        examples_dir = self.project_path / 'Documentation' / 'examples'
        examples_dir.mkdir(parents=True, exist_ok=True)
        
        # Example configurations for each provider combination
        examples = {
            'duckdb_cube_oss.yaml': _get_example_config_duckdb_cube_oss(),
            'motherduck_cube_cloud.yaml': _get_example_config_motherduck_cube_cloud(),
            'snowflake_looker.yaml': _get_example_config_snowflake_looker(),
            'bigquery_superset.yaml': _get_example_config_bigquery_superset(),
        }
        
        for filename, content in examples.items():
            (examples_dir / filename).write_text(content)


def _get_example_config_duckdb_cube_oss() -> str:
    """Example config: Local DuckDB + Cube OSS."""
    return textwrap.dedent("""
        # Example: Local DuckDB + Cube.js OSS (Docker)
        # Perfect for development and testing
        
        project_name: Local-Dev-Platform
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
            api_secret: metricforge-dev-secret
        
        include_docker: true
        include_tests: true
        include_cicd: true
    """).strip()


def _get_example_config_motherduck_cube_cloud() -> str:
    """Example config: MotherDuck + Cube Cloud."""
    return textwrap.dedent("""
        # Example: MotherDuck + Cube Cloud (SaaS)
        # Recommended for production with managed services
        
        project_name: Production-Platform
        organization: MyOrganization
        
        data_warehouse:
          type: motherduck
          config:
            database: metricforge_prod
            # Set MD_TOKEN environment variable for authentication
        
        semantic_layer:
          type: cube_cloud
          config:
            deploy_id: your-deployment-id
            api_endpoint: https://api.cubecloudapp.com
            # Set CUBE_CLOUD_TOKEN environment variable for authentication
        
        include_docker: false
        include_tests: true
        include_cicd: true
    """).strip()


def _get_example_config_snowflake_looker() -> str:
    """Example config: Snowflake + Looker."""
    return textwrap.dedent("""
        # Example: Snowflake + Looker
        # Enterprise setup with Snowflake DW and Google Cloud Looker BI
        
        project_name: Enterprise-Platform
        organization: MyOrganization
        
        data_warehouse:
          type: snowflake
          config:
            account: xy12345.us-east-1
            user: datalake_user
            warehouse: COMPUTE_WH
            database: ANALYTICS
            schema: PUBLIC
            # Set SNOWFLAKE_PASSWORD environment variable
        
        semantic_layer:
          type: looker
          config:
            instance_url: https://myinstance.cloud.looker.com
            api_version: "4.0"
            # Set LOOKER environment variables
        
        include_docker: false
        include_tests: true
        include_cicd: true
    """).strip()


def _get_example_config_bigquery_superset() -> str:
    """Example config: BigQuery + Superset."""
    return textwrap.dedent("""
        # Example: BigQuery + Apache Superset
        # Google Cloud native with open source Superset BI
        
        project_name: GCP-Platform
        organization: MyOrganization
        
        data_warehouse:
          type: bigquery
          config:
            project_id: my-gcp-project
            dataset_id: metricforge
            # Set GOOGLE_APPLICATION_CREDENTIALS for service account
        
        semantic_layer:
          type: superset
          config:
            port: 8088
            admin_username: admin
            # Set admin_password in environment or securely
        
        include_docker: true
        include_tests: true
        include_cicd: true
    """).strip()
