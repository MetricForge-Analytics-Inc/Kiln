"""CLI tool to initialize MetricForge projects locally."""

import click
from pathlib import Path
from metricforge.utils.project_setup import ProjectInitializer


DATA_WAREHOUSES = {
    'duckdb': 'DuckDB (Local/embedabble FOSS file-based OLAP database)',
    'motherduck': 'MotherDuck (Managed cloud-based duckdb)',
    'snowflake': 'Snowflake (Enterprise cloud data warehouse)',
    'bigquery': 'BigQuery (Google Cloud data warehouse)',
}

SEMANTIC_LAYERS = {
    'cube': 'Cube.js OSS (Local/embedabble FOSS semantic layer)',
    'cube-cloud': 'Cube Cloud (Managed cloud-based cube SaaS)',
    'looker': 'Looker (Google Cloud BI tool)',
    'metabase': 'Metabase (Open source BI tool)',
    'superset': 'Superset (Open source BI tool)',
}


@click.command()
@click.option('--name', prompt='Project name', help='Name for your project')
@click.option('--dw', type=click.Choice(list(DATA_WAREHOUSES.keys())), 
              prompt='Data warehouse', help='Choose data warehouse')
@click.option('--sl', type=click.Choice(list(SEMANTIC_LAYERS.keys())), 
              prompt='Semantic layer', help='Choose semantic layer')
@click.option('--path', default='.', help='Directory to create project in')
def init(name: str, dw: str, sl: str, path: str) -> None:
    """Initialize a new MetricForge data platform project."""
    
    project_path = Path(path) / name
    
    click.echo(f"🚀 Creating MetricForge project: {name}")
    click.echo(f"   Data Warehouse: {DATA_WAREHOUSES[dw]}")
    click.echo(f"   Semantic Layer: {SEMANTIC_LAYERS[sl]}")
    click.echo(f"   Location: {project_path}")
    
    config_data = {
        'project_name': name,
        'project_slug': name.lower().replace(' ', '_').replace('-', '_'),
        'organization_name': name,
        'data_warehouse_type': f'duckdb_local' if dw == 'duckdb' else dw,
        'semantic_layer_type': f'cube_oss' if sl == 'cube' else sl,
        'include_docker': True,
        'include_tests': True,
        'include_cicd': True,
    }
    
    try:
        initializer = ProjectInitializer(project_path)
        
        click.echo("📂 Creating directory structure...")
        initializer.create_directory_structure(config_data)
        
        click.echo("⚙️  Creating configuration file...")
        initializer.create_config_file(config_data)
        
        click.echo("🐳 Creating Docker configuration...")
        initializer.create_dockerignore()
        
        click.echo("📖 Creating README...")
        initializer.create_readme(config_data)
        
        click.echo("📋 Creating example configurations...")
        initializer.create_example_configs()
        
        click.echo("\n✅ Project initialized successfully!")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. cd {project_path}")
        click.echo(f"  2. Edit metricforge.yaml with your credentials")
        click.echo(f"  3. pip install -r requirements.txt")
        click.echo(f"  4. python Crucible-Orchestration/main.py")
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize project: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    init()
