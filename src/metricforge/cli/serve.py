"""CLI command to start the MetricForge provisioning API server."""

import click


@click.command("serve")
@click.option("--host", default="0.0.0.0", help="Bind host")
@click.option("--port", default=8000, type=int, help="Bind port")
@click.option("--crucible", default=None, envvar="CRUCIBLE_PATH", help="Path to Crucible repo")
@click.option("--output-root", default=None, envvar="METRICFORGE_OUTPUT_ROOT",
              help="Root directory for generated projects")
def serve(host: str, port: int, crucible: str | None, output_root: str | None) -> None:
    """Start the MetricForge provisioning API server."""
    try:
        import uvicorn
    except ImportError:
        click.echo("uvicorn is required: pip install metricforge-crucible[api]", err=True)
        raise click.Abort()

    import os
    from pathlib import Path

    if crucible:
        os.environ["CRUCIBLE_PATH"] = crucible
    if output_root:
        os.environ["METRICFORGE_OUTPUT_ROOT"] = output_root

    click.echo(f"Starting MetricForge API on {host}:{port}")
    click.echo(f"  CRUCIBLE_PATH: {os.environ.get('CRUCIBLE_PATH', '(auto-detect)')}")
    click.echo(f"  OUTPUT_ROOT: {os.environ.get('METRICFORGE_OUTPUT_ROOT', '/var/metricforge/projects')}")

    uvicorn.run("metricforge.api:app", host=host, port=port, reload=False)
