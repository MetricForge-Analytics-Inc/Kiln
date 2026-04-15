"""CLI command to upgrade an existing project from a newer Crucible version."""

import shutil
import click
from pathlib import Path
from metricforge.utils.config import MetricForgeConfig
from metricforge.utils.template_engine import (
    build_context, scaffold_project, _CRUCIBLE_STATIC, _get_kiln_version,
)
from metricforge.cli.initialize import _find_crucible


@click.command('upgrade')
@click.option('--path', default='.', help='Project root directory')
@click.option('--crucible', default=None, envvar='CRUCIBLE_PATH',
              help='Path to Crucible repo')
@click.option('--dry-run', is_flag=True, help='Show what would be updated without writing')
def upgrade(path: str, crucible: str | None, dry_run: bool) -> None:
    """Upgrade project files from a newer Crucible version.

    Re-copies static files (Dockerfiles, SQL sources, components, etc.)
    from Crucible and re-renders parameterized templates.  Your
    metricforge.yaml and .env are preserved.
    """
    crucible_path = _find_crucible(crucible)
    project_path = Path(path)
    config_file = project_path / 'metricforge.yaml'

    if not config_file.exists():
        click.echo("No metricforge.yaml found. Run 'metricforge init' first.", err=True)
        raise click.Abort()

    cfg = MetricForgeConfig(str(config_file))
    full_config = cfg.to_dict()

    old_version = full_config.get('kiln_version', 'unknown')
    new_version = _get_kiln_version()

    click.echo(f"   Upgrading project: {full_config.get('project_name', '?')}")
    click.echo(f"   From Kiln v{old_version} → v{new_version}")
    click.echo(f"   Crucible source: {crucible_path}")

    if dry_run:
        click.echo("\n[dry-run] Files that would be updated:")
        for src_rel, dst_rel in _CRUCIBLE_STATIC:
            src = crucible_path / src_rel
            if src.exists():
                click.echo(f"  {dst_rel}")
        click.echo("\n[dry-run] No files modified.")
        return

    # Build context from the existing metricforge.yaml
    context = build_context({
        'project_name': full_config.get('project_name', 'metricforge-project'),
        'organization': full_config.get('organization', ''),
        'data_warehouse_type': full_config.get('data_warehouse', {}).get('type', 'duckdb_local'),
        'semantic_layer_type': full_config.get('semantic_layer', {}).get('type', 'cube_oss'),
        'include_docker': full_config.get('include_docker', True),
        'include_tests': full_config.get('include_tests', True),
        'include_cicd': full_config.get('include_cicd', True),
        'pipelines': full_config.get('pipelines', {}),
    })

    # Preserve .env and metricforge.yaml by backing them up
    env_file = project_path / '.env'
    env_backup = None
    if env_file.exists():
        env_backup = env_file.read_text(encoding='utf-8')

    config_backup = config_file.read_text(encoding='utf-8')

    # Re-scaffold
    scaffold_project(project_path, crucible_path, context)

    # Restore preserved files
    config_file.write_text(config_backup, encoding='utf-8')
    if env_backup is not None:
        env_file.write_text(env_backup, encoding='utf-8')

    # Update the kiln_version in the config
    cfg2 = MetricForgeConfig(str(config_file))
    cfg2.config['kiln_version'] = new_version
    cfg2.save()

    click.echo(f"\n Project upgraded to Kiln v{new_version}!")
