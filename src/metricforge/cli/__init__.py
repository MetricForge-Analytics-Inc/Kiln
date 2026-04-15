"""MetricForge CLI tools."""

import click
from .initialize import init
from .add_pipeline import add_pipeline
from .build import build
from .upgrade import upgrade
from .serve import serve
from .status import status


@click.group()
def cli():
    """MetricForge - Generate and manage data platforms."""
    pass


cli.add_command(init, name='init')
cli.add_command(add_pipeline, name='add-pipeline')
cli.add_command(build, name='build')
cli.add_command(upgrade, name='upgrade')
cli.add_command(serve, name='serve')
cli.add_command(status, name='status')


def main():
    """Main entry point for MetricForge CLI."""
    cli()


__all__ = ["cli", "main", "init", "add_pipeline", "build", "upgrade", "serve", "status"]
