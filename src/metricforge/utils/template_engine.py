"""Template engine that renders parameterized .j2 files from Kiln and copies
static source files directly from the Crucible repository.

Kiln stays lightweight — it only stores the handful of files that need
per-client parameterization (.j2 templates).  Everything else (Dockerfiles,
SQL sources, Svelte components, Evidence pages, entrypoints, etc.) is read
straight from the Crucible repo at scaffold time.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import secrets
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Small set of Jinja2 templates that live inside the Kiln package
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# ── mapping tables ────────────────────────────────────────────────

_EVIDENCE_DATASOURCE = {
    "duckdb_local": "@evidence-dev/duckdb",
    "motherduck": "@evidence-dev/motherduck",
    "snowflake": "@evidence-dev/snowflake",
    "bigquery": "@evidence-dev/bigquery",
}

DW_TYPE_MAP = {
    "duckdb": "duckdb_local",
    "motherduck": "motherduck",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
}

SL_TYPE_MAP = {
    "cube": "cube_oss",
    "cube-cloud": "cube_cloud",
    "looker": "looker",
    "metabase": "metabase",
    "superset": "superset",
}

# Static files / directories to copy from Crucible → generated project.
# Each entry is (crucible_relative_path, output_relative_path).
# Directories are copied recursively; files are copied as-is.
_CRUCIBLE_STATIC: List[Tuple[str, str]] = [
    # Orchestration
    ("Orchestration/Dockerfile", "Orchestration/Dockerfile"),
    ("Orchestration/entrypoint.sh", "Orchestration/entrypoint.sh"),
    ("Orchestration/requirements.txt", "Orchestration/requirements.txt"),
    ("Orchestration/trigger.py", "Orchestration/trigger.py"),
    # Visualization
    ("Visualization/Dockerfile", "Visualization/Dockerfile"),
    ("Visualization/entrypoint.sh", "Visualization/entrypoint.sh"),
    ("Visualization/dev.sh", "Visualization/dev.sh"),
    ("Visualization/degit.json", "Visualization/degit.json"),
    ("Visualization/requirements.txt", "Visualization/requirements.txt"),
    ("Visualization/pages", "Visualization/pages"),
    ("Visualization/sources", "Visualization/sources"),
    ("Visualization/components", "Visualization/components"),
    # Semantic Cubes (static cubes — the first one has a .j2 override)
    ("Semantic-Cubes/model/cube.py", "Semantic-Cubes/model/cube.py"),
    ("Semantic-Cubes/model/cubes/2_tickets_case_response_time.yaml",
     "Semantic-Cubes/model/cubes/2_tickets_case_response_time.yaml"),
    ("Semantic-Cubes/model/cubes/3_tickets_case_reassigned_time.yaml",
     "Semantic-Cubes/model/cubes/3_tickets_case_reassigned_time.yaml"),
    ("Semantic-Cubes/model/cubes/4_tickets_case_incident_time.yaml",
     "Semantic-Cubes/model/cubes/4_tickets_case_incident_time.yaml"),
    ("Semantic-Cubes/model/cubes/5_tickets_case_reopened_time.yaml",
     "Semantic-Cubes/model/cubes/5_tickets_case_reopened_time.yaml"),
    ("Semantic-Cubes/model/cubes/6_tickets_case_closed_time.yaml",
     "Semantic-Cubes/model/cubes/6_tickets_case_closed_time.yaml"),
    ("Semantic-Cubes/model/cubes/END_tickets_case_detail.yaml",
     "Semantic-Cubes/model/cubes/END_tickets_case_detail.yaml"),
]

# Pipeline-Casts are conditional — only copied when the area is selected.
# Keyed by (business_area, vendor).  Paths are relative to Crucible root.
_CRUCIBLE_PIPELINES: Dict[Tuple[str, str], List[Tuple[str, str]]] = {
    ("support", "zendesk"): [
        ("Pipeline-Casts/Support/zendesk", "Pipeline-Casts/Support/zendesk"),
    ],
    ("support", "salesforce"): [
        ("Pipeline-Casts/Support/salesforce", "Pipeline-Casts/Support/salesforce"),
    ],
    ("sales", "zendesk"): [
        ("Pipeline-Casts/Sales/zendesk", "Pipeline-Casts/Sales/zendesk"),
    ],
    ("sales", "salesforce"): [
        ("Pipeline-Casts/Sales/salesforce", "Pipeline-Casts/Sales/salesforce"),
    ],
}


def _make_env() -> Environment:
    """Create a Jinja2 environment rooted at the Kiln templates directory."""
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape([]),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_context(config: Dict[str, Any]) -> Dict[str, Any]:
    """Build the full template context from a metricforge config dict."""
    project_name = config.get("project_name", "metricforge-project")
    project_slug = (
        config.get("project_slug")
        or project_name.lower().replace(" ", "_").replace("-", "_")
    )
    dw_type = config.get("data_warehouse_type", "duckdb_local")
    sl_type = config.get("semantic_layer_type", "cube_oss")

    pipelines = config.get("pipelines", {})
    support_software = pipelines.get("support", {}).get("software")
    sales_software = pipelines.get("sales", {}).get("software")

    areas = []
    if support_software:
        areas.append({"name": "support", "title": "Support", "software": support_software})
    if sales_software:
        areas.append({"name": "sales", "title": "Sales", "software": sales_software})

    return {
        "project_name": project_name,
        "project_slug": project_slug,
        "organization": config.get("organization", project_name),
        "dw_type": dw_type,
        "sl_type": sl_type,
        "include_docker": config.get("include_docker", True),
        "include_tests": config.get("include_tests", True),
        "include_cicd": config.get("include_cicd", True),
        "areas": areas,
        "support_software": support_software,
        "sales_software": sales_software,
        "has_support": support_software is not None,
        "has_sales": sales_software is not None,
        "evidence_datasource": _EVIDENCE_DATASOURCE.get(dw_type, "@evidence-dev/duckdb"),
        "cube_api_secret": secrets.token_urlsafe(32),
        "kiln_version": _get_kiln_version(),
    }


def render_template(template_path: str, context: Dict[str, Any]) -> str:
    """Render a single .j2 template and return the string content."""
    env = _make_env()
    tmpl = env.get_template(template_path)
    return tmpl.render(**context)


def scaffold_project(
    output_dir: Path,
    crucible_path: Path,
    context: Dict[str, Any],
) -> None:
    """Generate a complete project into *output_dir*.

    1. Render all ``.j2`` templates from Kiln's templates dir.
    2. Copy static files from the Crucible repo.
    3. Copy pipeline-specific dirs based on selected areas/vendors.
    """
    env = _make_env()

    # ── Step 1: Render .j2 templates from Kiln ───────────────────
    for j2_file in TEMPLATES_DIR.rglob("*.j2"):
        rel = j2_file.relative_to(TEMPLATES_DIR)
        dest_rel = Path(*rel.parts).with_suffix("")  # strip .j2

        tmpl = env.get_template(rel.as_posix())
        content = tmpl.render(**context)
        dest = output_dir / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    # ── Step 2: Copy static non-.j2 files from Kiln templates ────
    for static_file in TEMPLATES_DIR.rglob("*"):
        if static_file.is_dir() or static_file.suffix == ".j2":
            continue
        rel = static_file.relative_to(TEMPLATES_DIR)
        dest = output_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(static_file, dest)

    # ── Step 3: Copy static files from Crucible ──────────────────
    for src_rel, dst_rel in _CRUCIBLE_STATIC:
        src = crucible_path / src_rel
        dst = output_dir / dst_rel
        if not src.exists():
            continue
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # ── Step 4: Copy pipeline-specific dirs from Crucible ────────
    for area_info in context.get("areas", []):
        key = (area_info["name"], area_info["software"])
        entries = _CRUCIBLE_PIPELINES.get(key, [])
        for src_rel, dst_rel in entries:
            src = crucible_path / src_rel
            dst = output_dir / dst_rel
            if not src.exists():
                continue
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    # ── Step 5: Parameterize copied files ────────────────────────
    # Replace hardcoded "Foundry." references with the client's project slug
    # in all SQL and Python files copied from Crucible.
    project_slug = context.get("project_slug", "")
    if project_slug:
        _replace_foundry_refs(output_dir, project_slug)

    # Parameterize DLT destination to match the client's data warehouse choice.
    dw_type = context.get("dw_type", "")
    if dw_type:
        _parameterize_dlt_destination(output_dir, dw_type)


_DW_TO_DLT_DESTINATION = {
    "duckdb_local": "duckdb",
    "motherduck": "motherduck",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
}


def _parameterize_dlt_destination(output_dir: Path, dw_type: str) -> None:
    """Replace DLT destination='motherduck' with the correct destination."""
    dlt_dest = _DW_TO_DLT_DESTINATION.get(dw_type, dw_type)
    pipeline_casts = output_dir / "Pipeline-Casts"
    if not pipeline_casts.exists():
        return
    for fpath in pipeline_casts.rglob("*_pipeline.py"):
        if fpath.is_file():
            text = fpath.read_text(encoding="utf-8")
            updated = text.replace(
                "destination='motherduck'",
                f"destination='{dlt_dest}'",
            ).replace(
                'destination="motherduck"',
                f'destination="{dlt_dest}"',
            )
            if updated != text:
                fpath.write_text(updated, encoding="utf-8")


def _replace_foundry_refs(output_dir: Path, project_slug: str) -> None:
    """Replace 'Foundry.' with '{project_slug}.' in SQL/Python files."""
    target_dirs = [
        output_dir / "Pipeline-Casts",
        output_dir / "Semantic-Cubes",
    ]
    extensions = {".sql", ".py", ".yaml", ".yml"}
    for target_dir in target_dirs:
        if not target_dir.exists():
            continue
        for fpath in target_dir.rglob("*"):
            if fpath.is_file() and fpath.suffix in extensions:
                text = fpath.read_text(encoding="utf-8")
                if "Foundry." in text:
                    fpath.write_text(
                        text.replace("Foundry.", f"{project_slug}."),
                        encoding="utf-8",
                    )


def _get_kiln_version() -> str:
    try:
        from metricforge import __version__
        return __version__
    except Exception:
        return "0.1.0"
