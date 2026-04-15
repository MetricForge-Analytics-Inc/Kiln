"""Utilities for project initialization and setup."""

from typing import Dict, Any
from pathlib import Path
import subprocess

from metricforge.utils.template_engine import build_context, scaffold_project


class ProjectInitializer:
    """Handles initialization of new MetricForge projects."""

    def __init__(self, project_path: Path, crucible_path: Path):
        self.project_path = project_path
        self.crucible_path = crucible_path
        self.project_path.mkdir(parents=True, exist_ok=True)

    def scaffold(self, config: Dict[str, Any]) -> None:
        """One-shot project generation.

        Renders .j2 templates from Kiln and copies static files from Crucible.
        """
        context = build_context(config)

        # Ensure key directories exist (even if no templates land inside them)
        for d in ("db", "Documentation/examples", ".sqlmesh", "Orchestration/logs"):
            (self.project_path / d).mkdir(parents=True, exist_ok=True)

        scaffold_project(self.project_path, self.crucible_path, context)

    def git_init(self) -> None:
        """Initialize a git repository and make an initial commit."""
        subprocess.run(
            ["git", "init"],
            cwd=self.project_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=self.project_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial scaffold from MetricForge Kiln"],
            cwd=self.project_path,
            capture_output=True,
        )
