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

PIPELINE_SOFTWARE = ['zendesk', 'salesforce']


def _find_crucible(hint: str | None) -> Path:
    """Resolve the Crucible repo path.

    Order: explicit --crucible flag  →  CRUCIBLE_PATH env var  →  sibling dir.
    """
    import os

    if hint:
        p = Path(hint)
        if p.is_dir():
            return p
        raise click.BadParameter(f"Crucible path does not exist: {p}")

    env = os.environ.get("CRUCIBLE_PATH")
    if env:
        p = Path(env)
        if p.is_dir():
            return p

    # Convention: Kiln and Crucible sit side-by-side under the same parent
    kiln_root = Path(__file__).resolve().parent.parent.parent.parent  # → .../Kiln/src/metricforge/cli/ → .../Kiln/
    sibling = kiln_root.parent / "Crucible"
    if sibling.is_dir():
        return sibling

    raise click.UsageError(
        "Cannot locate the Crucible repository. "
        "Set --crucible, CRUCIBLE_PATH env var, or place Crucible alongside Kiln."
    )


@click.command()
@click.option('--name', prompt='Project name', help='Name for your project')
@click.option('--dw', type=click.Choice(list(DATA_WAREHOUSES.keys())),
              prompt='Data warehouse', help='Choose data warehouse')
@click.option('--sl', type=click.Choice(list(SEMANTIC_LAYERS.keys())),
              prompt='Semantic layer', help='Choose semantic layer')
@click.option('--path', default='.', help='Directory to create project in')
@click.option('--crucible', default=None, envvar='CRUCIBLE_PATH',
              help='Path to Crucible repo (default: auto-detect sibling dir)')
@click.option('--support-software', type=click.Choice(PIPELINE_SOFTWARE),
              default=None, help='Software tool for Support pipeline')
@click.option('--sales-software', type=click.Choice(PIPELINE_SOFTWARE),
              default=None, help='Software tool for Sales pipeline')
@click.option('--git/--no-git', default=True, help='Initialize a git repository')
def init(name: str, dw: str, sl: str, path: str, crucible: str | None,
         support_software: str, sales_software: str, git: bool) -> None:
    """Initialize a new MetricForge data platform project."""

    crucible_path = _find_crucible(crucible)
    project_path = Path(path) / name

    click.echo(f"   Creating MetricForge project: {name}")
    click.echo(f"   Crucible source: {crucible_path}")
    click.echo(f"   Data Warehouse: {DATA_WAREHOUSES[dw]}")
    click.echo(f"   Semantic Layer: {SEMANTIC_LAYERS[sl]}")
    if support_software:
        click.echo(f"   Support Pipeline: {support_software}")
    if sales_software:
        click.echo(f"   Sales Pipeline: {sales_software}")
    click.echo(f"   Location: {project_path}")

    pipelines = {}
    if support_software:
        pipelines['support'] = {'software': support_software}
    if sales_software:
        pipelines['sales'] = {'software': sales_software}

    dw_type = 'duckdb_local' if dw == 'duckdb' else dw
    sl_type = 'cube_oss' if sl == 'cube' else sl.replace('-', '_')

    config_data = {
        'project_name': name,
        'project_slug': name.lower().replace(' ', '_').replace('-', '_'),
        'organization': name,
        'data_warehouse_type': dw_type,
        'semantic_layer_type': sl_type,
        'include_docker': True,
        'include_tests': True,
        'include_cicd': True,
        'pipelines': pipelines,
    }

    try:
        initializer = ProjectInitializer(project_path, crucible_path)

        click.echo("Scaffolding project from Crucible + Kiln templates...")
        initializer.scaffold(config_data)

        if git:
            click.echo("Initializing git repository...")
            initializer.git_init()

        click.echo("\n Project initialized successfully!")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. cd {project_path}")
        click.echo(f"  2. cp .env.example .env  # fill in your credentials")
        click.echo(f"  3. docker compose up -d")
        click.echo(f"  4. Open http://localhost:3000 for dashboards")

    except Exception as e:
        click.echo(f"Failed to initialize project: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    init()
