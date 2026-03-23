"""Configuration management for MetricForge projects."""

from typing import Any, Dict, Optional
from pathlib import Path
import yaml
import json

from .providers import (
    ConnectionConfig,
    get_data_warehouse_provider,
    get_semantic_layer_provider,
)


class MetricForgeConfig:
    """
    Configuration container for a MetricForge project.
    
    Manages both user choices and provider configurations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration from file or defaults.
        
        Args:
            config_path: Path to metricforge.yaml or metricforge.json config file
        """
        self.config_path = Path(config_path) if config_path else Path("metricforge.yaml")
        self.config: Dict[str, Any] = {}
        self.dw_provider = None
        self.sl_provider = None
        
        if self.config_path.exists():
            self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_path.suffix in ['.yaml', '.yml']:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        elif self.config_path.suffix == '.json':
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {self.config_path.suffix}")
    
    def _validate_config(self):
        """Validate required configuration keys."""
        required_keys = ['project_name', 'data_warehouse', 'semantic_layer']
        missing = [k for k in required_keys if k not in self.config]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return dict(self.config)
    
    def to_yaml(self) -> str:
        """Export configuration as YAML string."""
        return yaml.dump(self.config, default_flow_style=False)
    
    def to_json(self) -> str:
        """Export configuration as JSON string."""
        return json.dumps(self.config, indent=2)
    
    def save(self, path: Optional[str] = None, format: str = 'yaml'):
        """Save configuration to file."""
        target_path = Path(path) if path else self.config_path
        
        if format == 'yaml':
            with open(target_path, 'w') as f:
                f.write(self.to_yaml())
        elif format == 'json':
            with open(target_path, 'w') as f:
                f.write(self.to_json())
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_data_warehouse_provider(self):
        """Get or initialize data warehouse provider."""
        if not self.dw_provider:
            self._validate_config()
            dw_type = self.config['data_warehouse']['type']
            dw_config = self.config['data_warehouse'].get('config', {})
            
            config = ConnectionConfig(
                provider_type=dw_type,
                name=self.config.get('project_name'),
                config=dw_config
            )
            self.dw_provider = get_data_warehouse_provider(dw_type, config)
        
        return self.dw_provider
    
    def get_semantic_layer_provider(self):
        """Get or initialize semantic layer provider."""
        if not self.sl_provider:
            self._validate_config()
            sl_type = self.config['semantic_layer']['type']
            sl_config = self.config['semantic_layer'].get('config', {})
            
            dw_provider = self.get_data_warehouse_provider()
            
            config = ConnectionConfig(
                provider_type=sl_type,
                name=self.config.get('project_name'),
                config=sl_config
            )
            self.sl_provider = get_semantic_layer_provider(sl_type, config, dw_provider)
        
        return self.sl_provider


def create_default_config(
    project_name: str,
    dw_type: str,
    sl_type: str,
    dw_config: Optional[Dict[str, Any]] = None,
    sl_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> MetricForgeConfig:
    """Factory function to create a default configuration."""
    config = MetricForgeConfig()
    
    config.config = {
        'project_name': project_name,
        'organization': kwargs.get('organization', 'MetricForge'),
        'data_warehouse': {
            'type': dw_type,
            'config': dw_config or _get_default_dw_config(dw_type),
        },
        'semantic_layer': {
            'type': sl_type,
            'config': sl_config or _get_default_sl_config(sl_type),
        },
        **{k: v for k, v in kwargs.items() if k not in ['organization']},
    }
    
    return config


def _get_default_dw_config(dw_type: str) -> Dict[str, Any]:
    """Get default configuration for data warehouse type."""
    defaults = {
        'duckdb_local': {
            'database_path': './db/metricforge.duckdb',
        },
        'motherduck': {
            'database': 'metricforge',
        },
        'snowflake': {
            'warehouse': 'COMPUTE_WH',
            'database': 'METRICFORGE',
            'schema': 'PUBLIC',
        },
        'bigquery': {
            'dataset_id': 'metricforge',
        },
    }
    return defaults.get(dw_type, {})


def _get_default_sl_config(sl_type: str) -> Dict[str, Any]:
    """Get default configuration for semantic layer type."""
    defaults = {
        'cube_oss': {
            'port': 4000,
            'sql_port': 15432,
            'api_secret': 'metricforge-local-dev-secret',
        },
        'cube_cloud': {
            'api_endpoint': 'https://api.cubecloudapp.com',
        },
        'metabase': {
            'port': 3000,
            'admin_email': 'admin@metricforge.local',
        },
        'superset': {
            'port': 8088,
            'admin_username': 'admin',
            'admin_password': 'admin',
        },
    }
    return defaults.get(sl_type, {})
