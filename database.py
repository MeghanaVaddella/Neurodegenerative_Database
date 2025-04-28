import streamlit as st
import pandas as pd
import requests
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import py3Dmol
import matplotlib.pyplot as plt
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="NEUROGEN PPI", layout="wide")

# --- Inject MADEVoyager Font ---
st.markdown("""
    <style>
    @font-face {
        font-family: 'MADEVoyager';
        src: url('https://raw.githubusercontent.com/MeghanaVaddella/Neurodegenerative_Database/main/MADEVoyagerPERSONAL_USE-Bold.otf') format('opentype');
    }
    </style>
""", unsafe_allow_html=True)

# --- Theme Colors (Dark Mode Palette) ---
body_bg = "#C4D8E2"            # Columbia Blue - Full Background and Navbar
header_bg = "#3B5875"          # Police Blue - Header Background
header_text_color = "#C4AEAD"  # Silver Pink - "NEUROGEN PPI" title
general_text_color = "#001C3D" # Maastricht Blue - General Text
button_bg = "#36454F"          # Charcoal - Download Button background
button_text_color = "#DBE9F4"  # Azureish White - Button text
table_bg = "#36454F"           # Charcoal - Table background
table_border_color = "#5D8AA8" # Rackley - Table border
search_bg = "#A7C7E7"          # Pastel Blue - Search bar background
remaining_bg = "#8BA8B7"       # Pewter Blue - Other areas

# --- Inject Custom Unified Styling ---
st.markdown(f"""
    <style>
    body, .stApp {{
        background-color: {body_bg};
        color: {general_text_color};
    }}
    .block-container {{
        background-color: {body_bg} !important;
    }}
    .header-text {{
        background-color: {header_bg};
        padding: 1.2rem;
        font-family: 'MADEVoyager', sans-serif;
        font-size: 58px;
        text-align: center;
        margin-top: 0.5em;
        margin-bottom: 0.3em;
        color: {header_text_color};
        letter-spacing: 2px;
        border-radius: 12px;
    }}
    /* Navigation Tabs Styling */
    div[data-baseweb="tab-list"] {{
        background-color: {body_bg} !important;
        border-bottom: none !important;
        padding-left: 1rem;
    }}
    button[data-baseweb="tab"] {{
        background-color: {body_bg} !important;
        color: {general_text_color} !important;
        border: none !important;
        font-weight: bold;
        font-size: 18px;
        margin-right: 1.5rem;
    }}
    button[data-baseweb="tab"]:hover {{
        color: #002B5B !important; /* Slightly darker Maastricht Blue on hover */
        background-color: {body_bg} !important;
        border: none !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        border-bottom: 2px solid {general_text_color} !important;
        font-weight: bold;
    }}

    /* Button Styling */
    .stButton button, button {{
        background-color: {button_bg} !important;
        color: {button_text_color} !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }}
    /* Input and Select Styling */
    .stTextInput > div > input,
    .stSelectbox > div,
    .stMultiSelect > div,
    .stSlider > div,
    .stNumberInput > div,
    .stTextArea > div > textarea {{
        background-color: {search_bg} !important;
        color: {general_text_color} !important;
        border: 1px solid {general_text_color} !important;
        border-radius: 6px;
    }}
    /* Data Frame and Table Styling */
    .stDataFrame, .data-box {{
        background-color: {table_bg} !important;
        color: {general_text_color} !important;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid {table_border_color};
    }}
    table {{
        color: {general_text_color} !important;
        background-color: {table_bg} !important;
        border: 1px solid {table_border_color} !important;
    }}
    /* Heading Styling */
    h1, h2, h3, h4, h5, h6 {{
        color: {general_text_color} !important;
        font-family: 'MADEVoyager', sans-serif;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='header-text'>NEUROGEN PPI</div>", unsafe_allow_html=True)

# ---- LOAD DATA FUNCTIONS ----
@st.cache_data(show_spinner=False)
def load_ppi_data():
    url = "https://raw.githubusercontent.com/MeghanaVaddella/my-cv-dataset/refs/heads/main/my-cv-data.csv"
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error loading PPI data: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_3d_data():
    urls = [
        "https://raw.githubusercontent.com/MeghanaVaddella/Neurodegenerative_Database/refs/heads/main/3D%20Structure-1.csv",
        "https://raw.githubusercontent.com/MeghanaVaddella/Neurodegenerative_Database/refs/heads/main/3D%20Structure-2.csv"
    ]
    try:
        dfs = [pd.read_csv(url) for url in urls]
        return pd.concat(dfs, ignore_index=True)
    except Exception as e:
        st.error(f"Error loading 3D structure data: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_no_3d_data():
    url = "https://raw.githubusercontent.com/MeghanaVaddella/Neurodegenerative_Database/refs/heads/main/No%203D%20Structure.csv"
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error loading No 3D structure data: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_disease_data():
    url = "https://raw.githubusercontent.com/MeghanaVaddella/my-cv-dataset/refs/heads/main/disease%20data.txt"
    try:
        response = requests.get(url)
        lines = response.text.splitlines()
        return [line.strip() for line in lines if line.strip()][1:]
    except Exception as e:
        st.error(f"Error loading disease text: {e}")
        return []

# ---- LOAD ALL ----
ppi_df = load_ppi_data()
df_3d = load_3d_data()
no_structure_df = load_no_3d_data()
disease_text = load_disease_data()

# ---- TABS ----
tabs = st.tabs([
    "Home", 
    "Data", 
    "3D Structure Data", 
    "3D Visualizer", 
    "GitHub Edit"
])

# ---- HOME TAB ----
with tabs[0]:
    st.header("🧠 Neurodegenerative Disease Overview")
    keywords = [
        "Alzheimer's Disease", 
        "Parkinson's Disease", 
        "Amyotrophic Lateral Sclerosis (ALS)", 
        "Multiple Sclerosis (MS)", 
        "Friedreich’s Ataxia (FA)"
    ]
    for paragraph in disease_text:
        for keyword in keywords:
            if keyword in paragraph:
                paragraph = paragraph.replace(keyword, f"<span style='color:#d62728; font-weight:bold;'>{keyword}</span>")
        st.markdown(paragraph, unsafe_allow_html=True)

# ---- DATA TAB ----
with tabs[1]:
    st.header("Protein-Protein Interaction Data")
    st.dataframe(ppi_df, use_container_width=True, hide_index=True)
    st.download_button("Download PPI CSV", ppi_df.to_csv(index=False), "PPI_data.csv", "text/csv")

    st.subheader("Visualize Interactions")
    selected_protein = st.selectbox("Choose Protein", pd.unique(ppi_df[['Protein A', 'Protein B']].values.ravel('K')))

    def build_ppi_graph(protein, df):
        G = nx.Graph()
        edges = df[(df['Protein A'] == protein) | (df['Protein B'] == protein)]
        for _, row in edges.iterrows():
            G.add_edge(row['Protein A'], row['Protein B'])
        net = Network(height="600px", width="100%", directed=False)
        net.from_nx(G)
        net.save_graph("ppi_graph.html")
        return "ppi_graph.html"

    if st.button("Show PPI Network"):
        if not ppi_df.empty:
            file_path = build_ppi_graph(selected_protein, ppi_df)
            components.html(open(file_path, 'r').read(), height=600)
            with open(file_path, "rb") as f:
                st.download_button("Download Network HTML", f, "ppi_network.html", "text/html")
        else:
            st.warning("PPI data is empty.")

# ---- 3D STRUCTURE TAB ----
with tabs[2]:
    st.header("3D Structure Data")
    st.dataframe(df_3d, use_container_width=True, hide_index=True)
    st.download_button("Download 3D Structure CSV", df_3d.to_csv(index=False), "3D_structure_data.csv", "text/csv")

    st.subheader("No 3D Structure Data")
    st.dataframe(no_structure_df, use_container_width=True, hide_index=True)
    st.download_button("Download No 3D Structure CSV", no_structure_df.to_csv(index=False), "No_3D_Structure.csv", "text/csv")

import streamlit as st
import requests
import py3Dmol

# ---- 3D VISUALIZER TAB ----
with tabs[3]:  # Check if the 3D Visualizer tab is selected
    st.write("### 3D Protein Structure Visualizer")

    # MolStar Viewer using PDB IDs from your dataset
    if not df_3d.empty:
        col1, col2 = st.columns(2)

        with col1:
            protein_a_options = df_3d['Protein A'].dropna().unique().tolist()
            selected_protein_a = st.selectbox("🔍 Select Protein A", options=[""] + protein_a_options, key="select_protein_a")
        with col2:
            protein_b_options = df_3d['Protein B'].dropna().unique().tolist()
            selected_protein_b = st.selectbox("🔍 Select Protein B", options=[""] + protein_b_options, key="select_protein_b")

        result_col1, result_col2 = st.columns(2)
        pdb_ids = []

        # Protein A visualization
        if selected_protein_a:
            protein_a_data = df_3d[df_3d['Protein A'] == selected_protein_a]
            if not protein_a_data.empty:
                row = protein_a_data.iloc[0]
                with result_col1:
                    st.write(f"**🧬 Protein A:** {row['Protein A']}")
                    st.write(f"**UniProt ID A:** {row['UniProtID A']}")
                    pdb_ids_a = row['PDB ID A'].split(", ")
                    if pdb_ids_a[0] != "NA":
                        pdb_links_a = " | ".join([f"[{pdb}](https://www.rcsb.org/structure/{pdb})" for pdb in pdb_ids_a])
                        st.markdown(f"🔗 **PDB IDs A:** {pdb_links_a}", unsafe_allow_html=True)
                        pdb_ids.extend(pdb_ids_a)
            else:
                with result_col1:
                    st.warning("No matching Protein A found.")

        # Protein B visualization
        if selected_protein_b:
            protein_b_data = df_3d[df_3d['Protein B'] == selected_protein_b]
            if not protein_b_data.empty:
                row = protein_b_data.iloc[0]
                with result_col2:
                    st.write(f"**🧬 Protein B:** {row['Protein B']}")
                    st.write(f"**UniProt ID B:** {row['UniProtID B']}")
                    pdb_ids_b = row['PDB ID B'].split(", ")
                    if pdb_ids_b[0] != "NA":
                        pdb_links_b = " | ".join([f"[{pdb}](https://www.rcsb.org/structure/{pdb})" for pdb in pdb_ids_b])
                        st.markdown(f"🔗 **PDB IDs B:** {pdb_links_b}", unsafe_allow_html=True)
                        pdb_ids.extend(pdb_ids_b)
            else:
                with result_col2:
                    st.warning("No matching Protein B found.")

        # MolStar visualization
        st.write("### 🧬 Mol* (MolStar) Viewer")
        pdb_ids = list(filter(lambda x: x != "NA", pdb_ids))

        if pdb_ids:
            molstar_url = f"https://molstar.org/viewer/?url=" + ",".join([f"https://files.rcsb.org/download/{pdb}.pdb" for pdb in pdb_ids])
            st.components.v1.iframe(molstar_url, width=1000, height=600)
        else:
            st.warning("No valid PDB IDs found for visualization.")

    st.markdown("---")

    # AlphaFold-based 3D Viewer using py3Dmol
    st.write("### 🧬 AlphaFold-based 3D Viewer (py3Dmol)")

    def fetch_alphafold_pdb(uniprot_id):
        """Fetch the AlphaFold PDB file for a given UniProt ID"""
        url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None

    # Protein selection for AlphaFold using the Protein A and Protein B lists
    col3, col4 = st.columns(2)
    with col3:
        protein_a_options = df_3d['UniProtID A'].dropna().unique().tolist()
        selected_uid1 = st.selectbox("🔍 Select UniProt ID for Protein A (AlphaFold)", options=[""] + protein_a_options, key="select_uid1")

    with col4:
        protein_b_options = df_3d['UniProtID B'].dropna().unique().tolist()
        selected_uid2 = st.selectbox("🔍 Select UniProt ID for Protein B (AlphaFold)", options=[""] + protein_b_options, key="select_uid2")

    # Check if both proteins are selected and fetch their PDBs
    if selected_uid1 and selected_uid2:
        pdb1 = fetch_alphafold_pdb(selected_uid1)
        pdb2 = fetch_alphafold_pdb(selected_uid2)

        if pdb1 and pdb2:
            st.subheader("🧪 AlphaFold 3D Viewer")
            viewer = py3Dmol.view(width=1000, height=600)
            viewer.addModel(pdb1, "pdb")
            viewer.setStyle({'model': 0}, {'cartoon': {'color': 'salmon'}})
            viewer.addModel(pdb2, "pdb")
            viewer.setStyle({'model': 1}, {'cartoon': {'color': 'skyblue'}})
            viewer.setBackgroundColor("white")
            viewer.zoomTo()
            st.components.v1.html(viewer._make_html(), height=600)

            # Combine both PDBs and allow user to download them
            combined_pdb = f"REMARK   Protein A: {selected_uid1}\n{pdb1}\nREMARK   Protein B: {selected_uid2}\n{pdb2}"
            st.subheader("💾 Download Combined Structure")
            st.download_button(
                label="Download PDB for Chimera",
                data=combined_pdb,
                file_name=f"{selected_uid1}_{selected_uid2}_combined.pdb",
                mime="chemical/x-pdb"
            )
        else:
            st.error("❌ One or both PDB files could not be fetched from AlphaFold.")

    st.markdown("---")

    # AlphaFold-Multimer FASTA Generator + Custom PDB Upload
    st.write("### 🧬 Predict Protein-Protein Interactions using AlphaFold-Multimer")

    # Protein selection for AlphaFold using the Protein A and Protein B lists
    col3, col4 = st.columns(2)
    with col3:
        protein_a_options = df_3d['UniProtID A'].dropna().unique().tolist()
        selected_uid1 = st.selectbox("🔍 Select UniProt ID for Protein A (AlphaFold)", options=[""] + protein_a_options, key="select_uid1")

    with col4:
        protein_b_options = df_3d['UniProtID B'].dropna().unique().tolist()
        selected_uid2 = st.selectbox("🔍 Select UniProt ID for Protein B (AlphaFold)", options=[""] + protein_b_options, key="select_uid2")

    # Function to fetch the sequence from UniProt for a given UniProt ID
    def fetch_sequence(uniprot_id):
        """Fetches the sequence for a given UniProt ID using the UniProt REST API"""
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
        response = requests.get(url)
        if response.ok:
            return response.text
        else:
            return None

    # Generate FASTA file and download
    if st.button("Generate AlphaFold-Multimer Input (FASTA)"):
        if selected_uid1 and selected_uid2:
            # Fetch sequences for both proteins
            seq1 = fetch_sequence(selected_uid1)
            seq2 = fetch_sequence(selected_uid2)

            if seq1 and seq2:
                combined_fasta = f"{seq1.strip()}\n{seq2.strip()}"
                st.success("FASTA file generated successfully.")
                st.download_button("⬇️ Download FASTA", data=combined_fasta, file_name="multimer_input.fasta", mime="text/plain")
                st.code(combined_fasta)

                # Show the Colab link after FASTA is displayed
                colab_link = "https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb"
                st.markdown(f"🔗 **[Open in Google Colab: AlphaFold-Multimer Notebook]({colab_link})**", unsafe_allow_html=True)

            else:
                st.error("Error fetching sequences. Please check the UniProt IDs.")
        else:
            st.warning("Please enter both UniProt IDs.")

    st.subheader("📦 Upload Predicted PDB File from AlphaFold")
    pdb_file = st.file_uploader("Upload PDB file", type=["pdb"])

    if pdb_file:
        pdb_str = pdb_file.read().decode("utf-8")
        viewer = py3Dmol.view(width=1000, height=600)
        viewer.addModel(pdb_str, "pdb")
        viewer.setStyle({'model': 0}, {'cartoon': {'color': 'spectrum'}})
        viewer.setBackgroundColor("white")
        viewer.zoomTo()
        st.components.v1.html(viewer._make_html(), height=600)

# ---- GITHUB EDIT TAB ----
with tabs[4]:
    st.header("🛠️ GitHub Edit Zone")

    st.markdown("""
      USE THIS SECTION TO ACCESS AND EDIT THE DATASETS DIRECTLY FROM THE GITHUB
    """) 

    github_links = {
        "PPI Data (CSV)": "https://github.com/MeghanaVaddella/my-cv-dataset/blob/main/my-cv-data.csv",
        "Disease Text (TXT)": "https://github.com/MeghanaVaddella/my-cv-dataset/blob/main/disease%20data.txt",
        "3D Structure Data 1": "https://github.com/MeghanaVaddella/Neurodegenerative_Database/blob/main/3D%20Structure-1.csv",
        "3D Structure Data 2": "https://github.com/MeghanaVaddella/Neurodegenerative_Database/blob/main/3D%20Structure-2.csv",
        "No 3D Structure (CSV)": "https://github.com/MeghanaVaddella/Neurodegenerative_Database/blob/main/No%203D%20Structure.csv"
    }

    for label, url in github_links.items():
        st.markdown(f"- 🔗 **[{label}]({url})**")

    st.markdown("""
    📢 **CHANGES IN THE GITHUB WILL BE REFLECTED IN THE APP WHEN THE PAGE IS RELOADED!!**
    """)   
