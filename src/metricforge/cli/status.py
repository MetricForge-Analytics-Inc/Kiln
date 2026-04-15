"""CLI command to check project health and pipeline status."""

import click
import subprocess
import json
from pathlib import Path


@click.command("status")
@click.option("--path", default=".", help="Project root directory")
@click.option("--json-output", "as_json", is_flag=True, help="Output as JSON")
def status(path: str, as_json: bool) -> None:
    """Check the health and status of a MetricForge project."""

    project_path = Path(path)
    config_file = project_path / "metricforge.yaml"

    if not config_file.exists():
        click.echo("No metricforge.yaml found. Not a MetricForge project.", err=True)
        raise click.Abort()

    from metricforge.utils.config import MetricForgeConfig

    cfg = MetricForgeConfig(str(config_file))
    full_config = cfg.to_dict()

    report = {
        "project_name": full_config.get("project_name", "?"),
        "kiln_version": full_config.get("kiln_version", "?"),
        "data_warehouse": full_config.get("data_warehouse", {}).get("type", "?"),
        "semantic_layer": full_config.get("semantic_layer", {}).get("type", "?"),
        "pipelines": list(full_config.get("pipelines", {}).keys()),
        "checks": {},
    }

    # File checks
    report["checks"]["metricforge_yaml"] = config_file.exists()
    report["checks"]["docker_compose"] = (project_path / "docker-compose.yml").exists()
    report["checks"]["env_file"] = (project_path / ".env").exists()
    report["checks"]["orchestration"] = (project_path / "Orchestration" / "Support-Main.py").exists()
    report["checks"]["visualization"] = (project_path / "Visualization" / "package.json").exists()

    # Docker service status
    compose_file = project_path / "docker-compose.yml"
    if compose_file.exists():
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                services = []
                for line in result.stdout.strip().splitlines():
                    try:
                        svc = json.loads(line)
                        services.append({
                            "name": svc.get("Name", svc.get("Service", "?")),
                            "state": svc.get("State", "?"),
                            "health": svc.get("Health", "N/A"),
                        })
                    except json.JSONDecodeError:
                        pass
                report["services"] = services
            else:
                report["services"] = []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            report["services"] = "docker not available"

    # Pipeline metrics (last run)
    metrics_file = project_path / "Orchestration" / "logs" / "pipeline_metrics.jsonl"
    if metrics_file.exists():
        lines = metrics_file.read_text(encoding="utf-8").strip().splitlines()
        if lines:
            try:
                last_metrics = [json.loads(l) for l in lines[-10:]]
                report["last_pipeline_metrics"] = last_metrics
            except json.JSONDecodeError:
                report["last_pipeline_metrics"] = "parse error"

    if as_json:
        click.echo(json.dumps(report, indent=2))
    else:
        click.echo(f"Project: {report['project_name']}")
        click.echo(f"Kiln Version: {report['kiln_version']}")
        click.echo(f"Data Warehouse: {report['data_warehouse']}")
        click.echo(f"Semantic Layer: {report['semantic_layer']}")
        click.echo(f"Pipelines: {', '.join(report['pipelines']) or 'none'}")
        click.echo()

        click.echo("File Checks:")
        for name, ok in report["checks"].items():
            icon = "+" if ok else "X"
            click.echo(f"  [{icon}] {name}")

        if "services" in report and isinstance(report["services"], list):
            click.echo()
            click.echo("Docker Services:")
            if report["services"]:
                for svc in report["services"]:
                    click.echo(f"  {svc['name']}: {svc['state']} (health: {svc['health']})")
            else:
                click.echo("  No running services")

        if "last_pipeline_metrics" in report and isinstance(report["last_pipeline_metrics"], list):
            click.echo()
            click.echo("Last Pipeline Run:")
            for m in report["last_pipeline_metrics"]:
                click.echo(f"  {m.get('stage', '?')}: {m.get('elapsed_seconds', '?')}s")
