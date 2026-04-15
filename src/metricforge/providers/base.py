"""
Provider abstraction layer for MetricForge.

This module defines the base interfaces for data warehouse and semantic layer providers,
allowing users to swap different implementations without changing core pipeline logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ConnectionConfig:
    """Base configuration for any data warehouse or semantic layer connection."""
    
    provider_type: str
    name: str
    config: Dict[str, Any]


class DataWarehouseProvider(ABC):
    """
    Abstract base class for data warehouse providers.
    
    Implementations should handle:
    - Connection initialization and testing
    - Schema/table creation
    - Data loading and querying
    - Authentication and credentials
    """
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.provider_name = config.name
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Test if the connection is valid and accessible."""
        pass
    
    @abstractmethod
    def get_connection_string(self) -> str:
        """
        Get the connection string for this provider.
        
        Returns:
            Connection string in the format expected by DLT, SQLMesh, etc.
        """
        pass
    
    @abstractmethod
    def get_environment_vars(self) -> Dict[str, str]:
        """
        Get environment variables needed for this provider.
        
        Used by orchestration and transformation tools to connect.
        """
        pass
    
    @abstractmethod
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """
        Get Docker Compose service definition if needed (e.g., for local databases).
        
        Returns None if this provider doesn't need a local service.
        """
        pass


class SemanticLayerProvider(ABC):
    """
    Abstract base class for semantic layer (BI tool) providers.
    
    Implementations should handle:
    - Connection to data warehouse
    - Semantic model generation/configuration
    - Authentication
    - API/UI availability and configuration
    """
    
    def __init__(self, config: ConnectionConfig, dw_provider: DataWarehouseProvider):
        self.config = config
        self.dw_provider = dw_provider
        self.provider_name = config.name
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Test if the connection is valid and accessible."""
        pass
    
    @abstractmethod
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables needed for this semantic layer."""
        pass
    
    @abstractmethod
    def get_docker_compose_service(self) -> Optional[Dict[str, Any]]:
        """Get Docker Compose service definition if needed."""
        pass
    
    @abstractmethod
    def get_ui_endpoints(self) -> Dict[str, str]:
        """
        Get UI endpoints for the semantic layer.
        
        Returns:
            Dictionary with endpoint names and URLs (e.g., {'playground': 'http://localhost:4000'})
        """
        pass
    
    @abstractmethod
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoints for the semantic layer."""
        pass
