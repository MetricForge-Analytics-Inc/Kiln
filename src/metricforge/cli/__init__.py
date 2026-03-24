"""MetricForge CLI tools."""

import click
from .initialize import init


@click.group()
def cli():
    """MetricForge - Generate and manage data platforms."""
    pass


cli.add_command(init, name='init')


def main():
    """Main entry point for metricforge CLI."""
    cli()


__all__ = ["cli", "main", "init"]
