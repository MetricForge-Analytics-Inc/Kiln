"""CLI command to add a pipeline to an existing MetricForge project."""

import shutil
import click
from pathlib import Path
from metricforge.utils.config import MetricForgeConfig
from metricforge.utils.template_engine import (
    render_template, _CRUCIBLE_PIPELINES,
    _replace_foundry_refs, _parameterize_dlt_destination,
    context_from_project_config,
)
from metricforge.cli.initialize import _find_crucible


BUSINESS_AREAS = ['support', 'sales']
PIPELINE_SOFTWARE = ['zendesk', 'salesforce']


@click.command('add-pipeline')
@click.option('--area', type=click.Choice(BUSINESS_AREAS),
              prompt='Business area', help='Business area for the pipeline')
@click.option('--software', type=click.Choice(PIPELINE_SOFTWARE),
              prompt='Software tool', help='Software tool for the pipeline')
@click.option('--path', default='.', help='Project root directory')
@click.option('--crucible', default=None, envvar='CRUCIBLE_PATH',
              help='Path to Crucible repo')
def add_pipeline(area: str, software: str, path: str, crucible: str | None) -> None:
    """Add a pipeline to an existing MetricForge project."""

    crucible_path = _find_crucible(crucible)
    project_path = Path(path)
    config_file = project_path / 'metricforge.yaml'

    if not config_file.exists():
        click.echo("No metricforge.yaml found. Run 'metricforge init' first.", err=True)
        raise click.Abort()

    cfg = MetricForgeConfig(str(config_file))

    existing = cfg.get_pipelines()
    if area in existing and existing[area].get('software') == software:
        click.echo(f"Pipeline '{area}' with software '{software}' already exists.")
        return

    cfg.add_pipeline(area, software)
    cfg.save()

    # Copy pipeline dir from Crucible
    key = (area, software)
    for src_rel, dst_rel in _CRUCIBLE_PIPELINES.get(key, []):
        src = crucible_path / src_rel
        dst = project_path / dst_rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Ensure Data-Extract and Data-Pipeline dirs exist even if Crucible didn't have them
    area_title = area.title()
    pipeline_dir = project_path / 'Pipeline-Casts' / area_title / software
    (pipeline_dir / 'Data-Extract').mkdir(parents=True, exist_ok=True)
    (pipeline_dir / 'Data-Pipeline').mkdir(parents=True, exist_ok=True)

    # Parameterize copied files: replace Foundry. refs and DLT destinations
    full_config = cfg.to_dict()
    project_slug = full_config.get('project_name', '').lower().replace(' ', '_').replace('-', '_')
    if project_slug:
        _replace_foundry_refs(project_path, project_slug)
    dw_type = full_config.get('data_warehouse', {}).get('type', '')
    if dw_type:
        _parameterize_dlt_destination(project_path, dw_type)

    # Re-render orchestration script with updated pipeline list
    context = context_from_project_config(cfg.to_dict())

    orch_content = render_template('Orchestration/Support-Main.py.j2', context)
    orch_path = project_path / 'Orchestration' / 'Support-Main.py'
    orch_path.parent.mkdir(parents=True, exist_ok=True)
    orch_path.write_text(orch_content, encoding='utf-8')

    click.echo(f"   Added {area} pipeline using {software}")
    click.echo(f"   Directory: Pipeline-Casts/{area_title}/{software}/")
    click.echo(f"   Updated: Orchestration/Support-Main.py")
    click.echo(f"   Config updated: metricforge.yaml")
