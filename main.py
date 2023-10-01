import pandas as pd
import sqlite3

file_path = "project-dataset1-protein-protein.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')
conn = sqlite3.connect('protein_data.db')
df.to_sql('protein_data', conn, if_exists='replace', index=False)
conn.close()

print("Data imported")

