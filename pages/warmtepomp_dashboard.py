import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
from io import BytesIO

# Set page configuration
# st.set_page_config(
#     page_title="Warmtepomp Meldcodelijst Dashboard",
#     page_icon="🌡️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

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

# Function to load and preprocess data
@st.cache_data
def load_data():
    try:
        # Try the relative path from pages directory
        file_path = "../data/Meldcodelijst Warmtepompen - april 2025 (3).xlsx"
        df = pd.read_excel(file_path, sheet_name="Meldcodes")
    except FileNotFoundError:
        # Fallback to absolute path or alternative location
        file_path = "data/Meldcodelijst Warmtepompen - april 2025 (3).xlsx"
        df = pd.read_excel(file_path, sheet_name="Meldcodes")
    
    # Rename columns to ensure they are consistent
    df.columns = ['MELDCODE', 'FABRIKANT', 'MODEL', 'VERMOGEN_KW', 'SUBSIDIEBEDRAG', 
                 'KOUDEMIDDEL', 'GWP', 'CATEGORIE']
    
    # Clean subsidy amount (remove € and convert to numeric)
    df['SUBSIDIEBEDRAG'] = df['SUBSIDIEBEDRAG'].astype(str).str.replace('€', '').str.replace('.', '').str.strip().astype(float)
    
    # Ensure the GWP is numeric
    df['GWP'] = pd.to_numeric(df['GWP'], errors='coerce')
    
    # Ensure power is numeric
    df['VERMOGEN_KW'] = pd.to_numeric(df['VERMOGEN_KW'], errors='coerce')
    
    return df

# Main title
st.title("Warmtepomp Meldcodelijst Dashboard")
st.subheader("Visualisatie van data uit de ISDE Meldcodelijst april 2025")

# Load data
try:
    df = load_data()
    st.success(f"Data geladen: {len(df)} warmtepompen")
except Exception as e:
    st.error(f"Fout bij het laden van de data: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

# Filter by manufacturer
all_manufacturers = sorted(df['FABRIKANT'].unique())
selected_manufacturers = st.sidebar.multiselect(
    "Selecteer fabrikanten",
    options=all_manufacturers,
    default=[]
)

# Filter by category
all_categories = sorted(df['CATEGORIE'].unique())
selected_categories = st.sidebar.multiselect(
    "Selecteer categorieën",
    options=all_categories,
    default=[]
)

# Filter by refrigerant
all_refrigerants = sorted(df['KOUDEMIDDEL'].unique())
selected_refrigerants = st.sidebar.multiselect(
    "Selecteer koudemiddelen",
    options=all_refrigerants,
    default=[]
)

# Filter by power range
min_power = float(df['VERMOGEN_KW'].min())
max_power = float(df['VERMOGEN_KW'].max())
power_range = st.sidebar.slider(
    "Vermogen (kW)",
    min_value=min_power,
    max_value=max_power,
    value=(min_power, max_power)
)

# Apply filters
filtered_df = df.copy()

if selected_manufacturers:
    filtered_df = filtered_df[filtered_df['FABRIKANT'].isin(selected_manufacturers)]

if selected_categories:
    filtered_df = filtered_df[filtered_df['CATEGORIE'].isin(selected_categories)]

if selected_refrigerants:
    filtered_df = filtered_df[filtered_df['KOUDEMIDDEL'].isin(selected_refrigerants)]

filtered_df = filtered_df[(filtered_df['VERMOGEN_KW'] >= power_range[0]) & 
                          (filtered_df['VERMOGEN_KW'] <= power_range[1])]

# Display metrics
st.header("Samenvatting")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Totaal aantal warmtepompen", f"{len(filtered_df)}")
with col2:
    st.metric("Gemiddeld vermogen (kW)", f"{filtered_df['VERMOGEN_KW'].mean():.1f}")
with col3:
    st.metric("Gemiddelde subsidie (€)", f"{filtered_df['SUBSIDIEBEDRAG'].mean():.0f}")
with col4:
    st.metric("Gemiddelde GWP", f"{filtered_df['GWP'].mean():.0f}")

# Visualizations
st.header("Visualisaties")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Subsidie per categorie", "Vermogen verdeling", 
                                    "Koudemiddelen", "Top Fabrikanten", "Data Tabel"])

with tab1:
    st.subheader("Gemiddelde subsidie per categorie")
    
    # Calculate average subsidy per category
    category_subsidy = filtered_df.groupby('CATEGORIE')['SUBSIDIEBEDRAG'].mean().reset_index()
    category_subsidy = category_subsidy.sort_values('SUBSIDIEBEDRAG', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        category_subsidy,
        x='CATEGORIE',
        y='SUBSIDIEBEDRAG',
        title="Gemiddelde subsidie per categorie",
        labels={'CATEGORIE': 'Categorie', 'SUBSIDIEBEDRAG': 'Gemiddelde subsidie (€)'},
        color='CATEGORIE',
        text_auto=True
    )
    fig.update_layout(xaxis_title="Categorie", yaxis_title="Gemiddelde subsidie (€)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Show additional information
    st.info("""
    De grafiek toont de gemiddelde subsidie per categorie warmtepomp. 
    Dit kan helpen bij het kiezen van het type warmtepomp met de meest voordelige subsidie.
    """)

with tab2:
    st.subheader("Vermogen verdeling per categorie")
    
    # Create box plot of power by category
    fig = px.box(
        filtered_df,
        x='CATEGORIE',
        y='VERMOGEN_KW',
        title="Verdeling van vermogen per categorie",
        labels={'CATEGORIE': 'Categorie', 'VERMOGEN_KW': 'Vermogen (kW)'},
        color='CATEGORIE'
    )
    fig.update_layout(xaxis_title="Categorie", yaxis_title="Vermogen (kW)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Histogram of power distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            filtered_df,
            x='VERMOGEN_KW',
            title="Verdeling van vermogen (kW)",
            labels={'VERMOGEN_KW': 'Vermogen (kW)', 'count': 'Aantal warmtepompen'},
            nbins=30
        )
        fig.update_layout(xaxis_title="Vermogen (kW)", yaxis_title="Aantal warmtepompen")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter plot of power vs. subsidy
        fig = px.scatter(
            filtered_df,
            x='VERMOGEN_KW',
            y='SUBSIDIEBEDRAG',
            color='CATEGORIE',
            title="Relatie tussen vermogen en subsidie",
            labels={
                'VERMOGEN_KW': 'Vermogen (kW)', 
                'SUBSIDIEBEDRAG': 'Subsidie (€)',
                'CATEGORIE': 'Categorie'
            },
            opacity=0.7
        )
        fig.update_layout(xaxis_title="Vermogen (kW)", yaxis_title="Subsidie (€)")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Analyse van koudemiddelen")
    
    # Count of refrigerants
    refrigerant_counts = filtered_df['KOUDEMIDDEL'].value_counts().reset_index()
    refrigerant_counts.columns = ['KOUDEMIDDEL', 'Aantal']
    
    # GWP values for each refrigerant
    refrigerant_gwp = filtered_df.groupby('KOUDEMIDDEL')['GWP'].mean().reset_index()
    
    # Merge the data
    refrigerant_data = pd.merge(refrigerant_counts, refrigerant_gwp, on='KOUDEMIDDEL')
    refrigerant_data = refrigerant_data.sort_values('Aantal', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart for refrigerant count
        fig = px.bar(
            refrigerant_data.head(10),
            x='KOUDEMIDDEL',
            y='Aantal',
            title="Top 10 koudemiddelen",
            labels={'KOUDEMIDDEL': 'Koudemiddel', 'Aantal': 'Aantal warmtepompen'},
            color='GWP',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Koudemiddel", yaxis_title="Aantal warmtepompen")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart for GWP values
        fig = px.bar(
            refrigerant_data.head(10),
            x='KOUDEMIDDEL',
            y='GWP',
            title="GWP-waarden van koudemiddelen",
            labels={'KOUDEMIDDEL': 'Koudemiddel', 'GWP': 'Global Warming Potential'},
            color='GWP',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Koudemiddel", yaxis_title="GWP")
        st.plotly_chart(fig, use_container_width=True)
    
    # Information about refrigerants and GWP
    st.info("""
    **Global Warming Potential (GWP)** is een maat voor de bijdrage van een broeikasgas aan de opwarming van de aarde.
    Hoe lager de GWP-waarde, hoe milieuvriendelijker het koudemiddel is.
    
    Nieuwere koudemiddelen zoals R32 hebben een lagere GWP-waarde dan oudere zoals R410A.
    """)

with tab4:
    st.subheader("Top Fabrikanten")
    
    # Count models per manufacturer
    manufacturer_counts = filtered_df['FABRIKANT'].value_counts().reset_index()
    manufacturer_counts.columns = ['FABRIKANT', 'Aantal_Modellen']
    manufacturer_counts = manufacturer_counts.sort_values('Aantal_Modellen', ascending=False).head(15)
    
    # Average subsidy per manufacturer
    manufacturer_subsidy = filtered_df.groupby('FABRIKANT')['SUBSIDIEBEDRAG'].mean().reset_index()
    manufacturer_subsidy.columns = ['FABRIKANT', 'Gemiddelde_Subsidie']
    
    # Merge data
    manufacturer_data = pd.merge(manufacturer_counts, manufacturer_subsidy, on='FABRIKANT')
    
    # Create horizontal bar chart
    fig = px.bar(
        manufacturer_data,
        y='FABRIKANT',
        x='Aantal_Modellen',
        title="Top 15 fabrikanten op aantal modellen",
        labels={'FABRIKANT': 'Fabrikant', 'Aantal_Modellen': 'Aantal modellen'},
        color='Gemiddelde_Subsidie',
        color_continuous_scale='Viridis',
        orientation='h'
    )
    fig.update_layout(yaxis_title="Fabrikant", xaxis_title="Aantal modellen")
    st.plotly_chart(fig, use_container_width=True)
    
    # Create scatter plot of number of models vs average subsidy
    fig = px.scatter(
        manufacturer_data,
        x='Aantal_Modellen',
        y='Gemiddelde_Subsidie',
        title="Relatie tussen aantal modellen en gemiddelde subsidie per fabrikant",
        labels={
            'Aantal_Modellen': 'Aantal modellen', 
            'Gemiddelde_Subsidie': 'Gemiddelde subsidie (€)'
        },
        size='Aantal_Modellen',
        color='Gemiddelde_Subsidie',
        color_continuous_scale='Viridis',
        hover_name='FABRIKANT'
    )
    fig.update_layout(xaxis_title="Aantal modellen", yaxis_title="Gemiddelde subsidie (€)")
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Data Tabel")
    
    # Download button
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Warmtepompen', index=False)
        return output.getvalue()
    
    excel_data = convert_df_to_excel(filtered_df)
    st.download_button(
        label="Download gefilterde data als Excel",
        data=excel_data,
        file_name="gefilterde_warmtepomp_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Display the data table
    st.dataframe(filtered_df, height=400) 