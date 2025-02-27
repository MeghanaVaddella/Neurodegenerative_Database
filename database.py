import streamlit as st
import pandas as pd
import requests
import networkx as nx
import streamlit.components.v1 as components
from streamlit_cytoscapejs import st_cytoscapejs

# ---- PAGE CONFIGURATION ----
st.set_page_config(
    page_title="Protein-Protein Interaction for Neurodegenerative Diseases",
    layout="wide"
)

# ---- CUSTOM CSS ----
st.markdown(
    """
    <style>
        body {
            background-color: #FEF2DB;
        }
        .main-container {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 15px;
        }
        .title {
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            color: #E7C484;
        }
        .summary {
            text-align: center;
            font-size: 18px;
            color: #5D5F6E;
            margin-bottom: 30px;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #F7E5C3;
        }
        .sidebar .stButton>button {
            background-color: #F0D7A9;
            color: white;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- PAGE HEADER ----
st.markdown("<h1 class='title'>Protein-Protein Interaction for Neurodegenerative Diseases</h1>", unsafe_allow_html=True)

st.markdown(
    """
    <p class='summary'>
    Neurodegenerative disorders, such as Alzheimer's and Parkinson's disease, involve the progressive loss of structure and function of neurons. 
    These disorders are characterized by protein misfolding, aggregation, and synaptic dysfunction, which contribute to neurodegeneration. 
    Identifying protein-protein interactions (PPI) helps in understanding disease mechanisms and discovering therapeutic targets. 
    PPI networks provide insights into the biological pathways and functional relationships between proteins. 
    Studying these interactions can guide drug discovery and the development of precision medicine. 
    Our platform aims to facilitate the exploration of these critical interactions in neurodegenerative diseases.
    </p>
    """,
    unsafe_allow_html=True
)

# ---- LOAD DATA FROM GITHUB ----
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://raw.githubusercontent.com/MeghanaVaddella/my-cv-dataset/main/my-cv-data.csv"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(url)
    else:
        st.error("Error loading dataset from GitHub. Please check the file path.")
        return pd.DataFrame()

df = load_data()

# ---- CREATE NETWORKX GRAPH ----
def create_ppi_graph(data):
    G = nx.Graph()
    for _, row in data.iterrows():
        G.add_edge(str(row.iloc[0]), str(row.iloc[1]))
    return G

ppi_graph = create_ppi_graph(df)

# ---- TABS FOR NAVIGATION ----
tabs = st.tabs(["Home", "Visualization Tools", "Data", "GitHub Edit"])

with tabs[0]:  # Home Tab
    col1, col2 = st.columns(2)
    with col1:
        protein_a = st.text_input("Search for Protein A:")
    with col2:
        protein_b = st.text_input("Search for Protein B:")
    
    if protein_a or protein_b:
        filtered_df = df[
            (df.iloc[:, 0].astype(str).str.contains(protein_a, case=False, na=False)) |
            (df.iloc[:, 1].astype(str).str.contains(protein_b, case=False, na=False))
        ]
        
        st.write(f"### Search Results for '{protein_a}' and '{protein_b}'")
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.write("### No interactions found")

with tabs[1]:  # Visualization Tools Tab
    st.write("### Network Visualization and Functional Annotations")
    
    # Convert NetworkX graph to Cytoscape elements
    elements = [
        {"data": {"id": node, "label": node}} for node in ppi_graph.nodes()
    ] + [
        {"data": {"source": edge[0], "target": edge[1]}} for edge in ppi_graph.edges()
    ]

    # Define Cytoscape styles
    stylesheet = [
        {"selector": "node", "style": {"label": "data(label)", "width": 20, "height": 20, "background-color": "#E7C484"}},
        {"selector": "edge", "style": {"width": 2, "line-color": "#F0D7A9"}}
    ]
    
    # Cytoscape Network Visualization
    st_cytoscapejs(
        elements=elements, 
        height="500px",
        stylesheet=stylesheet
    )
    
    # KEGG Pathway Viewer
    kegg_url = "https://www.genome.jp/kegg/pathway.html"
    st.markdown(f"[View KEGG Pathways]({kegg_url})")

with tabs[2]:  # Data Tab
    st.write("### Full Protein-Protein Interaction Data")
    st.dataframe(df)
    st.download_button(
        "Download Processed Data", df.to_csv(index=False), file_name="PPI_data.csv", mime="text/csv"
    )

with tabs[3]:  # GitHub Edit Tab
    st.markdown("[Edit Data on GitHub](https://github.com/MeghanaVaddella/my-cv-dataset/edit/main/my-cv-data.csv)")

# ---- REMOVE STREAMLIT BRANDING ----
st.markdown("""<style> footer {visibility: hidden;} </style>""", unsafe_allow_html=True)
