import streamlit as st
import importlib
import sys
from pathlib import Path

# Add current directory and pages directory to path to ensure imports work
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

# Set page configuration
st.set_page_config(
    page_title="Subsidie Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default elements and hamburger menu in the top left
hide_elements = """
    <style>
        #MainMenu {visibility: hidden;}
        div[data-testid="collapsedControl"] {display: none;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        div.block-container {padding-top: 1rem;}
    </style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# Define app modules
MODULES = {
    "pages.warmtepomp_dashboard": {
        "title": "Warmtepomp Dashboard",
        "description": "Visualisatie van warmtepompen uit de ISDE meldcodelijst",
        "icon": "🌡️",
        "color": "#1f77b4"
    },
    "pages.warmtepomp_large_calculator": {
        "title": "Warmtepomp >70kW Calculator",
        "description": "Rekentool voor subsidies voor grote warmtepompen",
        "icon": "🔥",
        "color": "#ff7f0e",
        "function": "display_large_heatpump_calculator"
    },
    "pages.isolatie_dashboard": {
        "title": "Isolatie Dashboard",
        "description": "Visualisatie van isolatiemaatregelen uit de ISDE meldcodelijst",
        "icon": "🏠",
        "color": "#2ca02c"
    }
}

# Create sidebar with logo and navigation
def render_sidebar():
    with st.sidebar:
        st.title("Subsidie Dashboard")
        st.markdown("---")
        
        # Home page navigation
        if st.sidebar.button("🏠 Home", key="home_btn", use_container_width=True):
            st.session_state["current_page"] = "home"
        
        st.markdown("## Dashboards")
        
        # Create navigation buttons for each module
        for module_name, module_info in MODULES.items():
            icon = module_info["icon"]
            title = module_info["title"]
            color = module_info.get("color", "#1f77b4")
            
            if st.sidebar.button(
                f"{icon} {title}", 
                key=f"nav_{module_name}",
                use_container_width=True
            ):
                st.session_state["current_page"] = module_name
        
        # Add footer to sidebar
        st.markdown("---")
        st.markdown("© 2024 Subsidie Dashboard")
        st.markdown("Ontwikkeld voor duurzaamheidsadviseurs")

# Home page content
def render_home():
    st.title("Subsidie Dashboard")
    st.subheader("Alles-in-één platform voor subsidieberekeningen en visualisaties")
    
    # Introduction
    st.markdown("""
    Welkom bij het Subsidie Dashboard! Dit platform biedt verschillende tools om inzicht te krijgen in beschikbare subsidies voor verduurzaming.
    
    Gebruik de navigatie in de zijbalk om naar de verschillende dashboards te gaan.
    """)
    
    # Display some metrics about the available subsidies
    st.subheader("Beschikbare subsidies 2024")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ISDE Subsidie 2024", "€4.000", "Voor particulieren en zakelijke gebruikers")
    with col2:
        st.metric("EIA Voordeel", "45%", "Fiscale aftrek voor bedrijven")
    with col3:
        st.metric("SDE++", "€300/ton CO₂", "Voor grootschalige projecten")
    
    # Cards for different dashboards
    st.subheader("Beschikbare dashboards")
    
    # Create two rows of module cards
    col1, col2 = st.columns(2)
    
    modules_list = list(MODULES.items())
    
    with col1:
        for i in range(0, len(modules_list), 2):
            if i < len(modules_list):
                module_name, module_info = modules_list[i]
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; background-color: {module_info['color']}20;">
                    <h3>{module_info['icon']} {module_info['title']}</h3>
                    <p>{module_info['description']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Open {module_info['title']}", key=f"open_{module_name}_1", use_container_width=True):
                    st.session_state["current_page"] = module_name
    
    with col2:
        for i in range(1, len(modules_list), 2):
            if i < len(modules_list):
                module_name, module_info = modules_list[i]
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; background-color: {module_info['color']}20;">
                    <h3>{module_info['icon']} {module_info['title']}</h3>
                    <p>{module_info['description']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Open {module_info['title']}", key=f"open_{module_name}_2", use_container_width=True):
                    st.session_state["current_page"] = module_name
    
    # Recent updates section
    st.subheader("Recente updates")
    st.markdown("""
    - **April 2024**: ISDE Meldcodelijsten bijgewerkt naar april 2025 versies
    - **Maart 2024**: Nieuwe warmtepomp calculator voor installaties >70kW toegevoegd
    - **Februari 2024**: Speciale rijksmonument isolatie dashboard gelanceerd
    """)

# Function to load and run a module
def load_module(module_name):
    try:
        if module_name in MODULES:
            module_info = MODULES[module_name]
            
            # If module has a specific function to call
            if "function" in module_info:
                module = importlib.import_module(module_name)
                function = getattr(module, module_info["function"])
                function()
            else:
                # Otherwise, import the module which will run its Streamlit code
                importlib.import_module(module_name)
                
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het laden van de module: {str(e)}")

# Main app logic
def main():
    # Initialize session state for navigation
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"
    
    # Render the sidebar with navigation
    render_sidebar()
    
    # Determine which page to show
    current_page = st.session_state["current_page"]
    
    # Render the selected page
    if current_page == "home":
        render_home()
    else:
        # Load and run the selected module
        load_module(current_page)

if __name__ == "__main__":
    main() 