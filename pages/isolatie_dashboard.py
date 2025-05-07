import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO

# Set page configuration
# st.set_page_config(
#     page_title="Isolatie Meldcodelijst Dashboard",
#     page_icon="🏠",
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
        file_path = "../data/Meldcodelijst Isolatie - april 2025 (1).xlsx"
        df = pd.read_excel(file_path, sheet_name="Meldcodes")
    except FileNotFoundError:
        # Fallback to absolute path or alternative location
        file_path = "data/Meldcodelijst Isolatie - april 2025 (1).xlsx"
        df = pd.read_excel(file_path, sheet_name="Meldcodes")
    
    # Rename columns to ensure they are consistent and easier to work with
    df = df.rename(columns={
        'Fabrikant / Merknaam': 'FABRIKANT',
        'NAAM_MATERIAAL': 'MATERIAAL',
        'MIN_WAARDE_RD': 'RD_WAARDE',
        'MIN_DIKTE_MM': 'DIKTE',
        'Subsidiebedrag bij een enkele maatregel': 'SUBSIDIE_ENKEL',
        'Subsidiebedrag bij meerdere maateregelen': 'SUBSIDIE_MEERDERE',
        'BioBased Bonus': 'BIOBASED_BONUS',
        'Categorie': 'CATEGORIE',
        'Woning Type': 'WONING_TYPE'
    })
    
    # Clean subsidy amounts (remove € and convert to numeric)
    for col in ['SUBSIDIE_ENKEL', 'SUBSIDIE_MEERDERE', 'BIOBASED_BONUS']:
        df[col] = df[col].astype(str).str.replace('€', '').str.replace(',', '.').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure numeric values
    df['RD_WAARDE'] = pd.to_numeric(df['RD_WAARDE'], errors='coerce')
    df['DIKTE'] = pd.to_numeric(df['DIKTE'], errors='coerce')
    
    # Fill NaN values in string columns with a placeholder
    df['MATERIAAL'] = df['MATERIAAL'].fillna('Onbekend')
    df['FABRIKANT'] = df['FABRIKANT'].fillna('Onbekend')
    df['CATEGORIE'] = df['CATEGORIE'].fillna('Onbekend')
    df['WONING_TYPE'] = df['WONING_TYPE'].fillna('Onbekend')
    
    # Add a flag for biobased products
    df['IS_BIOBASED'] = df['BIOBASED_BONUS'] > 0
    
    return df

# Main title
st.title("Isolatie Meldcodelijst Dashboard")
st.subheader("Visualisatie van data uit de ISDE Meldcodelijst april 2025")

# Load data
try:
    df = load_data()
    st.success(f"Data geladen: {len(df)} isolatieproducten")
except Exception as e:
    st.error(f"Fout bij het laden van de data: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

# Filter by manufacturer
all_manufacturers = sorted([str(x) for x in df['FABRIKANT'].unique() if pd.notna(x)])
selected_manufacturers = st.sidebar.multiselect(
    "Selecteer fabrikanten",
    options=all_manufacturers,
    default=[]
)

# Filter by category
all_categories = sorted([str(x) for x in df['CATEGORIE'].unique() if pd.notna(x)])
selected_categories = st.sidebar.multiselect(
    "Selecteer categorieën",
    options=all_categories,
    default=[]
)

# Filter by material
all_materials = sorted([str(x) for x in df['MATERIAAL'].unique() if pd.notna(x)])
selected_materials = st.sidebar.multiselect(
    "Selecteer materialen",
    options=all_materials,
    default=[]
)

# Filter by Rd value range
min_rd = float(df['RD_WAARDE'].min())
max_rd = float(df['RD_WAARDE'].max())
rd_range = st.sidebar.slider(
    "Rd-waarde",
    min_value=min_rd,
    max_value=max_rd,
    value=(min_rd, max_rd)
)

# Filter by biobased
biobased_filter = st.sidebar.radio(
    "BioBased producten",
    options=["Alle producten", "Alleen BioBased", "Geen BioBased"],
    index=0
)

# Apply filters
filtered_df = df.copy()

if selected_manufacturers:
    filtered_df = filtered_df[filtered_df['FABRIKANT'].astype(str).isin(selected_manufacturers)]

if selected_categories:
    filtered_df = filtered_df[filtered_df['CATEGORIE'].astype(str).isin(selected_categories)]

if selected_materials:
    filtered_df = filtered_df[filtered_df['MATERIAAL'].astype(str).isin(selected_materials)]

# Make sure we have valid numeric values for the Rd-value filter
filtered_df = filtered_df[filtered_df['RD_WAARDE'].notna()]
filtered_df = filtered_df[(filtered_df['RD_WAARDE'] >= rd_range[0]) & 
                          (filtered_df['RD_WAARDE'] <= rd_range[1])]

if biobased_filter == "Alleen BioBased":
    filtered_df = filtered_df[filtered_df['IS_BIOBASED']]
elif biobased_filter == "Geen BioBased":
    filtered_df = filtered_df[~filtered_df['IS_BIOBASED']]

# Display metrics
st.header("Samenvatting")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Totaal aantal producten", f"{len(filtered_df)}")
with col2:
    st.metric("Gemiddelde Rd-waarde", f"{filtered_df['RD_WAARDE'].mean():.2f}")
with col3:
    st.metric("Gem. subsidie enkel (€)", f"{filtered_df['SUBSIDIE_ENKEL'].mean():.0f}")
with col4:
    st.metric("Aantal BioBased producten", f"{filtered_df['IS_BIOBASED'].sum()}")

# Visualizations
st.header("Visualisaties")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Subsidie per categorie", 
    "Materiaal analyse", 
    "Rd-waarde verdeling", 
    "Top fabrikanten",
    "Data tabel"
])

with tab1:
    st.subheader("Subsidie per categorie")
    
    # Calculate average subsidies per category
    category_subsidies = filtered_df.groupby('CATEGORIE').agg({
        'SUBSIDIE_ENKEL': 'mean',
        'SUBSIDIE_MEERDERE': 'mean',
        'BIOBASED_BONUS': 'mean'
    }).reset_index()
    
    # Melt the data for easier plotting
    category_subsidies_melted = pd.melt(
        category_subsidies, 
        id_vars=['CATEGORIE'],
        value_vars=['SUBSIDIE_ENKEL', 'SUBSIDIE_MEERDERE', 'BIOBASED_BONUS'],
        var_name='Subsidie Type',
        value_name='Gemiddeld Bedrag'
    )
    
    # Create grouped bar chart
    fig = px.bar(
        category_subsidies_melted,
        x='CATEGORIE',
        y='Gemiddeld Bedrag',
        color='Subsidie Type',
        barmode='group',
        title="Gemiddelde subsidies per categorie",
        labels={
            'CATEGORIE': 'Categorie', 
            'Gemiddeld Bedrag': 'Gemiddelde subsidie (€)',
            'Subsidie Type': 'Type subsidie'
        },
        color_discrete_map={
            'SUBSIDIE_ENKEL': '#1f77b4',
            'SUBSIDIE_MEERDERE': '#ff7f0e',
            'BIOBASED_BONUS': '#2ca02c'
        }
    )
    fig.update_layout(xaxis_title="Categorie", yaxis_title="Gemiddelde subsidie (€)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Show additional information
    st.info("""
    De grafiek toont de gemiddelde subsidie per categorie isolatieproduct.
    - Enkele maatregel: subsidie wanneer u alleen deze isolatiemaatregel neemt
    - Meerdere maatregelen: subsidie wanneer u deze combineert met andere maatregelen
    - BioBased bonus: extra subsidie voor biologische isolatiematerialen
    """)

with tab2:
    st.subheader("Analyse van isolatiematerialen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Count of materials - make sure all values are strings to avoid sorting issues
        material_counts = filtered_df['MATERIAAL'].astype(str).value_counts().reset_index()
        material_counts.columns = ['MATERIAAL', 'Aantal']
        material_counts = material_counts.sort_values('Aantal', ascending=False)
        
        # Create pie chart
        fig = px.pie(
            material_counts,
            values='Aantal',
            names='MATERIAAL',
            title="Verdeling van isolatiematerialen",
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # BioBased products by material - ensure all material values are strings
        biobased_by_material = filtered_df.groupby(filtered_df['MATERIAAL'].astype(str))['IS_BIOBASED'].mean().reset_index()
        biobased_by_material.columns = ['MATERIAAL', 'Percentage BioBased']
        biobased_by_material['Percentage BioBased'] = biobased_by_material['Percentage BioBased'] * 100
        biobased_by_material = biobased_by_material.sort_values('Percentage BioBased', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            biobased_by_material,
            x='MATERIAAL',
            y='Percentage BioBased',
            title="Percentage BioBased per materiaalsoort",
            labels={'MATERIAAL': 'Materiaal', 'Percentage BioBased': 'Percentage BioBased (%)'},
            color='Percentage BioBased',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Materiaal", yaxis_title="Percentage BioBased (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Material vs subsidy - ensure all material values are strings
    material_subsidies = filtered_df.groupby(filtered_df['MATERIAAL'].astype(str)).agg({
        'SUBSIDIE_ENKEL': 'mean',
        'SUBSIDIE_MEERDERE': 'mean',
        'BIOBASED_BONUS': 'mean'
    }).reset_index()
    material_subsidies = material_subsidies.sort_values('SUBSIDIE_ENKEL', ascending=False)
    
    # Create grouped bar chart
    fig = px.bar(
        material_subsidies,
        x='MATERIAAL',
        y=['SUBSIDIE_ENKEL', 'SUBSIDIE_MEERDERE', 'BIOBASED_BONUS'],
        title="Gemiddelde subsidies per materiaalsoort",
        labels={
            'MATERIAAL': 'Materiaal', 
            'value': 'Gemiddelde subsidie (€)',
            'variable': 'Type subsidie'
        },
        barmode='group'
    )
    fig.update_layout(xaxis_title="Materiaal", yaxis_title="Gemiddelde subsidie (€)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Information about materials
    st.info("""
    **BioBased materialen** zijn gemaakt van hernieuwbare biologische grondstoffen en hebben vaak een lagere milieu-impact.
    Voorbeelden zijn houtvezels, vlas, hennep en schapenwol. Ze komen in aanmerking voor een extra subsidie (BioBased bonus).
    """)

with tab3:
    st.subheader("Rd-waarde en dikte analyse")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of Rd values
        fig = px.histogram(
            filtered_df,
            x='RD_WAARDE',
            title="Verdeling van Rd-waarden",
            labels={'RD_WAARDE': 'Rd-waarde (m²K/W)', 'count': 'Aantal producten'},
            nbins=20,
            color='CATEGORIE'
        )
        fig.update_layout(xaxis_title="Rd-waarde (m²K/W)", yaxis_title="Aantal producten")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter plot of Rd vs thickness - ensure we have only rows with valid numeric values
        valid_data = filtered_df.dropna(subset=['RD_WAARDE', 'DIKTE'])
        fig = px.scatter(
            valid_data,
            x='RD_WAARDE',
            y='DIKTE',
            color='MATERIAAL',
            title="Relatie tussen Rd-waarde en dikte",
            labels={
                'RD_WAARDE': 'Rd-waarde (m²K/W)', 
                'DIKTE': 'Minimale dikte (mm)',
                'MATERIAAL': 'Materiaal'
            },
            opacity=0.7
        )
        fig.update_layout(xaxis_title="Rd-waarde (m²K/W)", yaxis_title="Minimale dikte (mm)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Box plot of Rd values by category
    fig = px.box(
        filtered_df,
        x='CATEGORIE',
        y='RD_WAARDE',
        title="Rd-waarden per categorie",
        labels={'CATEGORIE': 'Categorie', 'RD_WAARDE': 'Rd-waarde (m²K/W)'},
        color='CATEGORIE'
    )
    fig.update_layout(xaxis_title="Categorie", yaxis_title="Rd-waarde (m²K/W)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Information about Rd values
    st.info("""
    **Rd-waarde** is de warmteweerstand van het isolatiemateriaal, uitgedrukt in m²K/W.
    Hoe hoger de Rd-waarde, hoe beter het materiaal isoleert.
    
    Voor ISDE-subsidie geldt een minimale Rd-waarde van:
    - 3,5 m²K/W voor dak-, gevel- en vloerisolatie
    - 2,5 m²K/W voor spouwmuurisolatie
    - 1,1 m²K/W voor isolerend glas
    """)

with tab4:
    st.subheader("Top fabrikanten")
    
    # Count models per manufacturer - ensure values are strings
    manufacturer_counts = filtered_df['FABRIKANT'].astype(str).value_counts().reset_index()
    manufacturer_counts.columns = ['FABRIKANT', 'Aantal_Producten']
    manufacturer_counts = manufacturer_counts.sort_values('Aantal_Producten', ascending=False).head(15)
    
    # Average subsidies per manufacturer - ensure values are strings
    manufacturer_subsidies = filtered_df.groupby(filtered_df['FABRIKANT'].astype(str)).agg({
        'SUBSIDIE_ENKEL': 'mean',
        'SUBSIDIE_MEERDERE': 'mean',
        'BIOBASED_BONUS': 'mean'
    }).reset_index()
    
    # Merge data
    manufacturer_data = pd.merge(manufacturer_counts, manufacturer_subsidies, on='FABRIKANT')
    
    # Create horizontal bar chart
    fig = px.bar(
        manufacturer_data,
        y='FABRIKANT',
        x='Aantal_Producten',
        title="Top 15 fabrikanten op aantal producten",
        labels={'FABRIKANT': 'Fabrikant', 'Aantal_Producten': 'Aantal producten'},
        color='SUBSIDIE_ENKEL',
        color_continuous_scale='Viridis',
        orientation='h'
    )
    fig.update_layout(yaxis_title="Fabrikant", xaxis_title="Aantal producten")
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a chart showing percentage of biobased products by manufacturer
    biobased_by_manufacturer = filtered_df.groupby(filtered_df['FABRIKANT'].astype(str))['IS_BIOBASED'].agg(['sum', 'count']).reset_index()
    biobased_by_manufacturer['Percentage_BioBased'] = (biobased_by_manufacturer['sum'] / biobased_by_manufacturer['count']) * 100
    biobased_by_manufacturer = biobased_by_manufacturer.sort_values('Percentage_BioBased', ascending=False)
    biobased_by_manufacturer = biobased_by_manufacturer[biobased_by_manufacturer['count'] >= 5]  # At least 5 products
    
    fig = px.bar(
        biobased_by_manufacturer.head(15),
        x='FABRIKANT',
        y='Percentage_BioBased',
        title="Percentage BioBased producten per fabrikant (top 15)",
        labels={'FABRIKANT': 'Fabrikant', 'Percentage_BioBased': 'Percentage BioBased (%)'},
        color='Percentage_BioBased',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(xaxis_title="Fabrikant", yaxis_title="Percentage BioBased (%)")
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Data Tabel")
    
    # Download button
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Isolatie', index=False)
        return output.getvalue()
    
    excel_data = convert_df_to_excel(filtered_df)
    st.download_button(
        label="Download gefilterde data als Excel",
        data=excel_data,
        file_name="gefilterde_isolatie_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Display the data table
    st.dataframe(filtered_df, height=400) 