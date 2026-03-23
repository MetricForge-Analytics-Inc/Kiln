"""
MetricForge Crucible - Web UI
Main Streamlit application entry point
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure page
st.set_page_config(
    page_title="MetricForge Crucible",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🚀 MetricForge Crucible")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Initialize Project", "Configure Project"],
    index=0
)

# Home page
if page == "Home":
    st.markdown("""
    # 📊 MetricForge Crucible
    
    **Build data platforms your way.**
    
    Choose your data warehouse and semantic layer from a flexible set of options,
    then instantly generate a complete, production-ready project structure.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🏢 Data Warehouses
        
        - **DuckDB** (Local)
        - **MotherDuck** (Cloud)
        - **Snowflake** (Enterprise)
        - **BigQuery** (GCP)
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Semantic Layers
        
        - **Cube.js OSS** (Open Source)
        - **Cube Cloud** (SaaS)
        - **Looker** (Enterprise BI)
        - **Metabase** (Open Source)
        - **Apache Superset** (Open Source)
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Unified Stack
    
    Every project includes:
    - **Orchestration**: Prefect workflows
    - **Transformation**: SQLMesh data models
    - **Loading**: DLT data pipelines
    - **Catalog**: Provider-specific data catalog
    """)
    
    st.markdown("---")
    
    st.info(
        "👉 **Get Started**: Use the navigation menu to create a new project or configure an existing one."
    )

# Initialize Project page
elif page == "Initialize Project":
    st.title("🚀 Initialize New Project")
    
    with st.form("init_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name",
                placeholder="my-data-platform",
                help="Name for your new data platform project"
            )
            
            data_warehouse = st.selectbox(
                "Data Warehouse",
                ["DuckDB Local", "MotherDuck", "Snowflake", "BigQuery"],
                help="Choose your data warehouse solution"
            )
        
        with col2:
            project_slug = st.text_input(
                "Project Slug",
                placeholder="my_data_platform",
                help="Slug for directory structure (auto-generated from name)"
            )
            
            semantic_layer = st.selectbox(
                "Semantic Layer",
                ["Cube.js OSS", "Cube Cloud", "Looker", "Metabase", "Apache Superset"],
                help="Choose your BI/semantic layer tool"
            )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            org_name = st.text_input(
                "Organization Name",
                placeholder="My Organization",
                help="Organization or team name"
            )
            
            include_examples = st.checkbox(
                "Include example configurations",
                value=True,
                help="Include example data models and queries"
            )
            
            include_docker = st.checkbox(
                "Include Docker Compose",
                value=True,
                help="Generate docker-compose.yaml for easy local deployment"
            )
        
        submitted = st.form_submit_button("🎯 Create Project", use_container_width=True)
    
    if submitted:
        if not project_name or not project_slug:
            st.error("❌ Project name and slug are required!")
        else:
            # Import initialization utilities
            from metricforge.utils.init import ProjectInitializer
            from metricforge.providers.data_warehouse import (
                DuckDBLocalProvider, MotherDuckProvider,
                SnowflakeProvider, BigQueryProvider
            )
            from metricforge.providers.semantic_layer import (
                CubeOSSProvider, CubeCloudProvider, LookerProvider,
                MetabaseProvider, SupersetProvider
            )
            
            # Map provider names
            dw_map = {
                "DuckDB Local": DuckDBLocalProvider,
                "MotherDuck": MotherDuckProvider,
                "Snowflake": SnowflakeProvider,
                "BigQuery": BigQueryProvider
            }
            
            sl_map = {
                "Cube.js OSS": CubeOSSProvider,
                "Cube Cloud": CubeCloudProvider,
                "Looker": LookerProvider,
                "Metabase": MetabaseProvider,
                "Apache Superset": SupersetProvider
            }
            
            try:
                dw_provider = dw_map[data_warehouse]()
                sl_provider = sl_map[semantic_layer]()
                
                # Initialize project
                initializer = ProjectInitializer(project_slug)
                initializer.create_project_structure()
                
                # Generate config
                config = initializer.generate_default_config(
                    dw_provider=dw_provider,
                    sl_provider=sl_provider,
                    org_name=org_name or "MyOrg"
                )
                
                st.success(
                    f"✅ Project '{project_name}' created successfully!\n\n"
                    f"📂 Location: `{project_slug}/`\n\n"
                    f"Stack:\n"
                    f"- Data Warehouse: {data_warehouse}\n"
                    f"- Semantic Layer: {semantic_layer}"
                )
                
                st.markdown("### 📋 Next Steps")
                st.code(f"""
# Navigate to your project
cd {project_slug}

# Review the configuration
cat metricforge.yaml

# Start the services (if using Docker)
docker-compose up -d

# For CLI mode, use Copier directly:
copier copy https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible . \\
    --trust all
                """, language="bash")
                
            except Exception as e:
                st.error(f"❌ Error creating project: {str(e)}")

# Configure Project page
elif page == "Configure Project":
    st.title("⚙️ Configure Project")
    
    tab1, tab2 = st.tabs(["Upload Config", "Edit Config"])
    
    with tab1:
        st.markdown("### Upload Existing Configuration")
        
        uploaded_file = st.file_uploader(
            "Choose a metricforge.yaml file",
            type=["yaml", "yml"]
        )
        
        if uploaded_file is not None:
            st.success("✅ File uploaded successfully!")
            
            # Display file contents
            st.markdown("#### Current Configuration")
            file_contents = uploaded_file.read().decode()
            st.code(file_contents, language="yaml")
            
            st.markdown("#### Edit below or download to modify externally:")
            edited_config = st.text_area(
                "Configuration",
                value=file_contents,
                height=300,
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Configuration"):
                    st.success("✅ Configuration saved!")
            
            with col2:
                st.download_button(
                    label="📥 Download Configuration",
                    data=edited_config,
                    file_name="metricforge.yaml",
                    mime="text/yaml"
                )
    
    with tab2:
        st.markdown("### Create New Configuration")
        st.info(
            "💡 Use this to create a configuration from scratch by selecting providers and settings."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            dw_choice = st.selectbox(
                "Data Warehouse",
                ["DuckDB Local", "MotherDuck", "Snowflake", "BigQuery"],
                key="edit_dw"
            )
        
        with col2:
            sl_choice = st.selectbox(
                "Semantic Layer",
                ["Cube.js OSS", "Cube Cloud", "Looker", "Metabase", "Apache Superset"],
                key="edit_sl"
            )
        
        # Import providers for example config
        from metricforge.providers.data_warehouse import (
            DuckDBLocalProvider, MotherDuckProvider,
            SnowflakeProvider, BigQueryProvider
        )
        from metricforge.providers.semantic_layer import (
            CubeOSSProvider, CubeCloudProvider, LookerProvider,
            MetabaseProvider, SupersetProvider
        )
        
        dw_map = {
            "DuckDB Local": DuckDBLocalProvider,
            "MotherDuck": MotherDuckProvider,
            "Snowflake": SnowflakeProvider,
            "BigQuery": BigQueryProvider
        }
        
        sl_map = {
            "Cube.js OSS": CubeOSSProvider,
            "Cube Cloud": CubeCloudProvider,
            "Looker": LookerProvider,
            "Metabase": MetabaseProvider,
            "Apache Superset": SupersetProvider
        }
        
        try:
            dw_provider = dw_map[dw_choice]()
            sl_provider = sl_map[sl_choice]()
            
            st.markdown("#### Provider Configuration")
            
            # Display provider defaults
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{dw_choice} Settings**")
                st.json({
                    "type": dw_provider.__class__.__name__,
                    "connection_type": type(dw_provider).__name__
                })
            
            with col2:
                st.markdown(f"**{sl_choice} Settings**")
                st.json({
                    "type": sl_provider.__class__.__name__,
                    "connection_type": type(sl_provider).__name__
                })
            
            st.markdown("#### Generated YAML Configuration")
            
            # Create example config
            example_config = f"""
data_warehouse:
  type: {dw_provider.__class__.__name__}
  config:
    # Provider-specific configuration here
    
semantic_layer:
  type: {sl_provider.__class__.__name__}
  config:
    # Provider-specific configuration here

orchestration:
  tool: prefect
  
transformation:
  tool: sqlmesh

data_loading:
  tool: dlt
            """
            
            config_text = st.text_area(
                "YAML Configuration",
                value=example_config.strip(),
                height=300,
                label_visibility="collapsed"
            )
            
            st.download_button(
                label="📥 Download Configuration",
                data=config_text,
                file_name="metricforge.yaml",
                mime="text/yaml",
                use_container_width=True
            )
        
        except Exception as e:
            st.error(f"Error loading providers: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; font-size: 0.9rem; color: #666;'>
    MetricForge Crucible • 
    <a href='https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible'>GitHub</a> • 
    <a href='#'>Documentation</a>
    </div>
    """,
    unsafe_allow_html=True
)
