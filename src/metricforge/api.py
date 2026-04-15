"""FastAPI service for programmatic MetricForge project provisioning.

Exposes the same functionality as the CLI (init, build, upgrade, add-pipeline)
as REST endpoints, intended for integration with a signup website or internal
automation.

Run:
    uvicorn metricforge.api:app --host 0.0.0.0 --port 8000

Or:
    metricforge serve --port 8000
"""

import logging
import re
import shutil
import uuid
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from metricforge.utils.template_engine import (
    scaffold_project,
    DW_TYPE_MAP,
    SL_TYPE_MAP,
    _replace_foundry_refs,
    _parameterize_dlt_destination,
    context_from_project_config,
)
from metricforge.utils.project_setup import ProjectInitializer

app = FastAPI(
    title="MetricForge Provisioning API",
    version="0.1.0",
    description="Programmatic data platform provisioning",
)

# ── Configuration ─────────────────────────────────────────────────

# These can be overridden with env vars or a config file
CRUCIBLE_PATH: Path | None = None
OUTPUT_ROOT: Path = Path("/var/metricforge/projects")

_PROJECT_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")

logger = logging.getLogger(__name__)


def _resolve_crucible() -> Path:
    """Resolve Crucible repo path from env or default."""
    import os

    if CRUCIBLE_PATH and CRUCIBLE_PATH.is_dir():
        return CRUCIBLE_PATH

    env = os.environ.get("CRUCIBLE_PATH")
    if env:
        p = Path(env)
        if p.is_dir():
            return p

    raise HTTPException(
        status_code=500,
        detail="CRUCIBLE_PATH not configured. Set it as an environment variable.",
    )


def _resolve_output_root() -> Path:
    """Resolve the root directory for generated projects."""
    import os

    env = os.environ.get("METRICFORGE_OUTPUT_ROOT")
    if env:
        return Path(env)
    return OUTPUT_ROOT


def _safe_project_path(project_name: str) -> Path:
    """Validate project_name and return a safe path under OUTPUT_ROOT."""
    if not _PROJECT_NAME_RE.match(project_name) or len(project_name) > 100:
        raise HTTPException(status_code=400, detail="Invalid project name")
    output_root = _resolve_output_root()
    project_path = (output_root / project_name).resolve()
    # Ensure resolved path is still under output root
    if not str(project_path).startswith(str(output_root.resolve())):
        raise HTTPException(status_code=400, detail="Invalid project name")
    return project_path


# ── Request / Response models ─────────────────────────────────────


class ProjectCreateRequest(BaseModel):
    """Request body for project creation."""

    project_name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    organization: str = ""
    data_warehouse: str = Field(..., description="duckdb | motherduck | snowflake | bigquery")
    semantic_layer: str = Field(..., description="cube | cube-cloud | looker | metabase | superset")
    support_software: Optional[str] = Field(None, description="zendesk | salesforce")
    sales_software: Optional[str] = Field(None, description="zendesk | salesforce")
    include_docker: bool = True
    include_cicd: bool = True
    include_git: bool = True


class ProjectCreateResponse(BaseModel):
    """Response after project creation."""

    project_id: str
    project_name: str
    project_path: str
    status: str


class ProjectStatusResponse(BaseModel):
    """Status check response."""

    project_id: str
    project_name: str
    exists: bool
    has_docker_compose: bool
    has_metricforge_yaml: bool


class AddPipelineRequest(BaseModel):
    """Request body for adding a pipeline."""

    area: Literal["support", "sales"] = Field(..., description="support | sales")
    software: Literal["zendesk", "salesforce"] = Field(..., description="zendesk | salesforce")


class UpgradeResponse(BaseModel):
    """Response after project upgrade."""

    project_name: str
    old_version: str
    new_version: str
    status: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    crucible_available: bool
    version: str


# ── Endpoints ─────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Service health check."""
    crucible_ok = False
    try:
        _resolve_crucible()
        crucible_ok = True
    except HTTPException:
        pass

    from metricforge import __version__

    return HealthResponse(
        status="ok",
        crucible_available=crucible_ok,
        version=__version__,
    )


@app.post("/projects", response_model=ProjectCreateResponse, status_code=201)
def create_project(req: ProjectCreateRequest):
    """Provision a new data platform project.

    This is the primary endpoint for website integration.
    """
    crucible_path = _resolve_crucible()
    output_root = _resolve_output_root()

    project_id = str(uuid.uuid4())[:8]
    project_path = _safe_project_path(req.project_name)

    if project_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Project '{req.project_name}' already exists at {project_path}",
        )

    # Normalize DW/SL types
    dw_type = DW_TYPE_MAP.get(req.data_warehouse, req.data_warehouse)
    sl_type = SL_TYPE_MAP.get(req.semantic_layer, req.semantic_layer.replace("-", "_"))

    pipelines = {}
    if req.support_software:
        pipelines["support"] = {"software": req.support_software}
    if req.sales_software:
        pipelines["sales"] = {"software": req.sales_software}

    config_data = {
        "project_name": req.project_name,
        "project_slug": req.project_name.lower().replace(" ", "_").replace("-", "_"),
        "organization": req.organization or req.project_name,
        "data_warehouse_type": dw_type,
        "semantic_layer_type": sl_type,
        "include_docker": req.include_docker,
        "include_tests": True,
        "include_cicd": req.include_cicd,
        "pipelines": pipelines,
    }

    try:
        initializer = ProjectInitializer(project_path, crucible_path)
        initializer.scaffold(config_data)

        if req.include_git:
            initializer.git_init()
    except Exception as e:
        # Clean up on failure
        if project_path.exists():
            shutil.rmtree(project_path)
        logger.exception("Failed to create project %s", req.project_name)
        raise HTTPException(status_code=500, detail="Project creation failed")

    return ProjectCreateResponse(
        project_id=project_id,
        project_name=req.project_name,
        project_path=str(project_path),
        status="created",
    )


@app.get("/projects/{project_name}", response_model=ProjectStatusResponse)
def get_project_status(project_name: str):
    """Check the status of an existing project."""
    project_path = _safe_project_path(project_name)

    return ProjectStatusResponse(
        project_id="",
        project_name=project_name,
        exists=project_path.exists(),
        has_docker_compose=(project_path / "docker-compose.yml").exists(),
        has_metricforge_yaml=(project_path / "metricforge.yaml").exists(),
    )


@app.post("/projects/{project_name}/pipelines", status_code=201)
def add_pipeline(project_name: str, req: AddPipelineRequest):
    """Add a pipeline to an existing project."""
    crucible_path = _resolve_crucible()
    project_path = _safe_project_path(project_name)

    if not (project_path / "metricforge.yaml").exists():
        raise HTTPException(status_code=404, detail="Project not found or not initialized")

    from metricforge.utils.config import MetricForgeConfig
    from metricforge.utils.template_engine import render_template, _CRUCIBLE_PIPELINES

    cfg = MetricForgeConfig(str(project_path / "metricforge.yaml"))
    existing = cfg.get_pipelines()
    if req.area in existing and existing[req.area].get("software") == req.software:
        raise HTTPException(
            status_code=409,
            detail=f"Pipeline '{req.area}' with software '{req.software}' already exists",
        )

    cfg.add_pipeline(req.area, req.software)
    cfg.save()

    # Copy pipeline from Crucible
    key = (req.area, req.software)
    for src_rel, dst_rel in _CRUCIBLE_PIPELINES.get(key, []):
        src = crucible_path / src_rel
        dst = project_path / dst_rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Parameterize copied files
    full_config = cfg.to_dict()
    project_slug = full_config.get("project_name", "").lower().replace(" ", "_").replace("-", "_")
    if project_slug:
        _replace_foundry_refs(project_path, project_slug)
    dw_type = full_config.get("data_warehouse", {}).get("type", "")
    if dw_type:
        _parameterize_dlt_destination(project_path, dw_type)

    # Re-render orchestration
    context = context_from_project_config(full_config)
    orch_content = render_template("Orchestration/Support-Main.py.j2", context)
    orch_path = project_path / "Orchestration" / "Support-Main.py"
    orch_path.parent.mkdir(parents=True, exist_ok=True)
    orch_path.write_text(orch_content, encoding="utf-8")

    return {"status": "added", "area": req.area, "software": req.software}


@app.post("/projects/{project_name}/upgrade", response_model=UpgradeResponse)
def upgrade_project(project_name: str):
    """Upgrade a project to the latest Crucible version."""
    crucible_path = _resolve_crucible()
    project_path = _safe_project_path(project_name)

    config_file = project_path / "metricforge.yaml"
    if not config_file.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    from metricforge.utils.config import MetricForgeConfig
    from metricforge.utils.template_engine import _get_kiln_version

    cfg = MetricForgeConfig(str(config_file))
    full_config = cfg.to_dict()
    old_version = full_config.get("kiln_version", "unknown")
    new_version = _get_kiln_version()

    # Backup preserved files
    env_file = project_path / ".env"
    env_backup = env_file.read_text(encoding="utf-8") if env_file.exists() else None
    config_backup = config_file.read_text(encoding="utf-8")

    context = context_from_project_config(full_config)

    scaffold_project(project_path, crucible_path, context)

    # Restore preserved files
    config_file.write_text(config_backup, encoding="utf-8")
    if env_backup is not None:
        env_file.write_text(env_backup, encoding="utf-8")

    cfg2 = MetricForgeConfig(str(config_file))
    cfg2.config["kiln_version"] = new_version
    cfg2.save()

    return UpgradeResponse(
        project_name=project_name,
        old_version=old_version,
        new_version=new_version,
        status="upgraded",
    )


@app.delete("/projects/{project_name}")
def delete_project(project_name: str):
    """Delete a project (destructive)."""
    project_path = _safe_project_path(project_name)

    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    shutil.rmtree(project_path)
    return {"status": "deleted", "project_name": project_name}
