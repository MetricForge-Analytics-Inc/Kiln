"""CLI command to build Docker images for a MetricForge project."""

import click
import subprocess
from pathlib import Path


@click.command('build')
@click.option('--path', default='.', help='Project root directory')
@click.option('--service', type=click.Choice(['all', 'orchestration', 'visualization']),
              default='all', help='Which service to build')
def build(path: str, service: str) -> None:
    """Build Docker images for the project."""

    project_path = Path(path)
    compose_file = project_path / 'docker-compose.yml'

    if not compose_file.exists():
        click.echo("No docker-compose.yml found. Run 'metricforge init' first.", err=True)
        raise click.Abort()

    if service == 'all':
        click.echo("Building all services...")
        result = subprocess.run(
            ['docker', 'compose', 'build'],
            cwd=project_path,
        )
    else:
        click.echo(f"Building {service}...")
        result = subprocess.run(
            ['docker', 'compose', 'build', service],
            cwd=project_path,
        )

    if result.returncode == 0:
        click.echo(f"\n Build successful!")
    else:
        click.echo(f"\n Build failed (exit code {result.returncode})", err=True)
        raise click.Abort()
