"""
MetricForge providers package.

Provides abstraction layer for pluggable data warehouse and semantic layer implementations.
"""

from .base import (
    ConnectionConfig,
    DataWarehouseProvider,
    SemanticLayerProvider,
)
from .data_warehouse import (
    DuckDBLocalProvider,
    MotherDuckProvider,
    SnowflakeProvider,
    BigQueryProvider,
    get_data_warehouse_provider,
    DATA_WAREHOUSE_PROVIDERS,
)
from .semantic_layer import (
    CubeOSSProvider,
    CubeCloudProvider,
    LookerProvider,
    MetabaseProvider,
    SupersetProvider,
    get_semantic_layer_provider,
    SEMANTIC_LAYER_PROVIDERS,
)

__all__ = [
    # Base classes
    "ConnectionConfig",
    "DataWarehouseProvider",
    "SemanticLayerProvider",
    # Data warehouse providers
    "DuckDBLocalProvider",
    "MotherDuckProvider",
    "SnowflakeProvider",
    "BigQueryProvider",
    "get_data_warehouse_provider",
    "DATA_WAREHOUSE_PROVIDERS",
    # Semantic layer providers
    "CubeOSSProvider",
    "CubeCloudProvider",
    "LookerProvider",
    "MetabaseProvider",
    "SupersetProvider",
    "get_semantic_layer_provider",
    "SEMANTIC_LAYER_PROVIDERS",
]
