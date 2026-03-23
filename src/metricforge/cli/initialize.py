"""
CLI initialization tool for MetricForge projects.

This is invoked after Copier template generation to complete project setup.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from metricforge.utils.config import create_default_config, MetricForgeConfig
from metricforge.utils.init import ProjectInitializer


def initialize_project(config_data: dict, project_path: Optional[str] = None) -> bool:
    """
    Initialize a new MetricForge project with the given configuration.
    
    Args:
        config_data: Configuration dictionary from copier
        project_path: Path to create project in (defaults to current directory)
        
    Returns:
        True if initialization was successful
    """
    project_path = Path(project_path) if project_path else Path.cwd()
    
    print(f"🚀 Initializing MetricForge project: {config_data.get('project_name')}")
    print(f"📁 Location: {project_path}")
    
    # Create project initializer
    initializer = ProjectInitializer(project_path)
    
    # Create directory structure
    print("📂 Creating directory structure...")
    initializer.create_directory_structure(config_data)
    
    # Create configuration file
    print("⚙️  Creating configuration file...")
    initializer.create_config_file(config_data)
    
    # Create Docker ignore
    print("🐳 Creating Docker configuration...")
    initializer.create_dockerignore()
    
    # Create README
    print("📖 Creating README...")
    initializer.create_readme(config_data)
    
    # Create example configs
    print("📋 Creating example configurations...")
    initializer.create_example_configs()
    
    print("\n✅ Project initialization complete!")
    print(f"\nNext steps:")
    print(f"  1. cd {project_path}")
    print(f"  2. Edit metricforge.yaml with your credentials")
    print(f"  3. pip install -r requirements.txt")
    print(f"  4. python Foundry-Orchestration/main.py")
    
    return True


def main():
    """Main entry point for CLI initialization."""
    parser = argparse.ArgumentParser(
        description="MetricForge Project Initializer"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to copier configuration (JSON format)",
    )
    parser.add_argument(
        "--project-path",
        type=str,
        default=".",
        help="Path where to create the project",
    )
    
    args = parser.parse_args()
    
    # Parse configuration
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config_data = json.load(f)
    else:
        # Use defaults for testing
        config_data = {
            "project_name": "MetricForge-Project",
            "project_slug": "metricforge_project",
            "organization_name": "MyOrganization",
            "data_warehouse_type": "duckdb_local",
            "semantic_layer_type": "cube_oss",
            "include_docker": True,
            "include_tests": True,
            "include_cicd": True,
        }
    
    try:
        success = initialize_project(config_data, args.project_path)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Initialization failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
