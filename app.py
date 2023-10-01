import base64

import streamlit as st
import pandas as pd
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('protein_data.db')

# Streamlit app
st.title("Protein Interaction Energy Database")

# Filters
st.sidebar.header("Filters")

# Protein 1 & 2
protein1 = st.sidebar.text_input("Protein 1:")
protein2 = st.sidebar.text_input("Protein 2:")

experiment_types = pd.read_sql("SELECT DISTINCT Experiment FROM protein_data", conn)['Experiment'].tolist()

# Columns to Display
all_columns = pd.read_sql("SELECT * FROM protein_data", conn).columns.tolist()
default_columns = ['Protein 1', 'Protein 2', 'Binding free energy (ΔG)', 'Change in binding free energy (ΔΔG)']

with st.sidebar.expander("Select Columns to Display"):
    selected_columns = [col for col in all_columns if st.checkbox(col, value=(col in default_columns))]

sortable_columns = selected_columns

# sort_column = st.sidebar.selectbox("Sort By:", ["None"] + sortable_columns)

sort_column = st.sidebar.expander("Sort By:").selectbox("", ["None"] + sortable_columns)
sort_order = st.sidebar.radio("Sort Order:", ["Ascending", "Descending"]) if sort_column != "None" else None

# Experiment Type
with st.sidebar.expander("Select Experiments"):
    selected_experiments = [experiment for experiment in experiment_types if st.checkbox(experiment, value=True)]

# Temperature & pH
min_temp, max_temp = st.sidebar.slider("Temperature Range (K)", 250, 310, (250, 310))
min_ph, max_ph = st.sidebar.slider("pH Range", 5.0, 9.0, (5.0, 9.0))

# Binding Free Energy
min_dG, max_dG = st.sidebar.slider("Binding Free Energy (ΔG) Range", -20.0, 0.0, (-20.0, 0.0))

# Change in Binding Free Energy
min_ddG, max_ddG = st.sidebar.slider("Change in Binding Free Energy (ΔΔG) Range", -10.0, 10.0, (-5.0, 10.0))

# Journal & Authors
journal = st.sidebar.text_input("Journal:")
authors = st.sidebar.text_input("Authors:")

# PDB ID
pdb_id = st.sidebar.text_input("PDB ID:")

# Query based on filters
query = f"""
SELECT * FROM protein_data 
WHERE (`Protein 1` LIKE ? OR ? = '') 
AND (`Protein 2` LIKE ? OR ? = '') 
AND Experiment IN ({', '.join(['?'] * len(selected_experiments))}) 
AND Temperature BETWEEN ? AND ? 
AND pH BETWEEN ? AND ? 
AND `Binding free energy (ΔG)` BETWEEN ? AND ? 
AND (`Change in binding free energy (ΔΔG)` BETWEEN ? AND ?)
AND (Journal LIKE ? OR ? = '') 
AND (Authors LIKE ? OR ? = '') 
AND (PDB LIKE ? OR ? = '')
"""
params = (
    f"%{protein1}%", protein1, f"%{protein2}%", protein2, *selected_experiments, min_temp, max_temp, min_ph, max_ph,
    min_dG,
    max_dG,
    min_ddG, max_ddG,
    f"%{journal}%", journal, f"%{authors}%", authors, f"%{pdb_id}%", pdb_id)

results = pd.read_sql(query, conn, params=params)[selected_columns]

results = results.drop_duplicates()

if "PubMed ID" in selected_columns:
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    results["PubMed ID"] = results["PubMed ID"].apply(lambda x: f'<a href="{base_url}{x}" target="_blank">{x}</a>')

if "PDB" in selected_columns:
    base_url = "https://www.rcsb.org/structure/"
    results["PDB"] = results["PDB"].apply(lambda x: f'<a href="{base_url}{x}" target="_blank">{x}</a>')

# Display
if len(results) > 0:
    col1, col2, c3, c4, c5 = st.columns(5)

    col1.write(f"{len(results)} results")
    # st.write(results)

    csv = results.to_csv(index=False).encode()
    c5.download_button(
        label="Download CSV",
        data=csv,
        file_name="protein_data_results.csv",
        mime="text/csv",
    )

def generate_csv_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Encoding the CSV to base64
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href


# Close the database connection
conn.close()


# Define CSS styles for the table
table_styles = """
<style>

table {
    margin: 0;
    border-radius: 8px;
    width: 100%; 
    font-family: 'Source Sans Pro', sans-serif;
    font-size: 14px;
    color: #31333f;
    background-color: white;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden; 
    border: none;
}

th, td {
    padding: 4px 8px;
    border: none;
}

table tbody tr:not(:first-child) td {
    border-top: none;
}

table tbody tr: td {
    border-top: none;
}

table tbody td:not(:first-child) {
    border-left: none;
}

th {
    background-color: #f0f0f0;
    text-align: left;
    border: none;
}

a {
    color: #FF2E63;
    text-decoration: none;
}

table thead th:first-child,
table tfoot tr:first-child td:first-child {
    border-top-left-radius: 8px;
}

table thead th:last-child,
table tfoot tr:first-child td:last-child {
    border-top-right-radius: 8px;
}

table tbody tr:last-child td:first-child,
table tfoot tr:last-child td:first-child {
    border-bottom-left-radius: 8px;
}

table tbody tr:last-child td:last-child,
table tfoot tr:last-child td:last-child {
    border-bottom-right-radius: 8px;
}
</style>
"""

if sort_column != "None":
    is_ascending = sort_order == "Ascending"
    results = results.sort_values(by=sort_column, ascending=is_ascending)

# Add styled table to Streamlit
if not results.empty:
    st.markdown(table_styles, unsafe_allow_html=True)
    st.markdown(results.to_html(escape=False, index=False), unsafe_allow_html=True)

