#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import csv
import streamlit as st

# Function to convert TXT to CSV
def txt_to_csv(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.txt'):
            input_path = os.path.join(input_folder, file_name)
            output_file_name = os.path.splitext(file_name)[0] + '.csv'
            output_path = os.path.join(output_folder, output_file_name)

            try:
                processed_rows = []
                with open(input_path, 'r', newline='', encoding='utf-8') as txt_file:
                    for line in txt_file:
                        line = line.strip()
                        if not line:
                            continue

                        if line.startswith('-'):
                            headers = line.split()
                            processed_rows.append(headers)
                        else:
                            processed_row = [col.strip() for col in line.split() if col]
                            processed_rows.append(processed_row)

                max_columns = max(len(row) for row in processed_rows)
                normalized_rows = [row + [''] * (max_columns - len(row)) for row in processed_rows]

                with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(normalized_rows)

                st.success(f"Converted: {file_name} -> {output_file_name}")

            except Exception as e:
                st.error(f"Failed to convert {file_name}: {e}")

# Function to process CSV files
def process_csv_files(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)

            try:
                df = pd.read_csv(file_path)
                df = df.iloc[35:].reset_index(drop=True)

                new_headers = [
                    "Measure", "Away 1", "Toward 1", "Away 2", "Toward 2",
                    "Away 3", "Toward 3", "Away Mean", "Toward Mean"
                ]
                if len(new_headers) <= len(df.columns):
                    df.columns = new_headers + list(df.columns[len(new_headers):])
                else:
                    df.columns = new_headers[:len(df.columns)]

                def safe_mean(row, columns):
                    try:
                        return round(pd.to_numeric(row[columns], errors='coerce').mean(), 1)
                    except Exception:
                        return None

                df['Away Mean'] = df.apply(lambda row: safe_mean(row, ["Away 1", "Away 2", "Away 3"]), axis=1)
                df['Toward Mean'] = df.apply(lambda row: safe_mean(row, ["Toward 1", "Toward 2", "Toward 3"]), axis=1)

                df.to_csv(file_path, index=False)
                st.success(f"Processed and updated: {file_name}")

            except Exception as e:
                st.error(f"Failed to process {file_name}: {e}")

# Streamlit UI
st.title("TXT to CSV Converter and Processor")
st.markdown("Right-click the folder you want to input/ export to/ from and select 'Copy as path'. Paste this into the boxes and be sure to remove the speech marks from the start and end of the text")
# Folder inputs
input_folder = st.text_input("Input Folder Path", "")
output_folder = st.text_input("Output Folder Path", "")

if st.button("Convert TXT to CSV"):
    if os.path.exists(input_folder):
        txt_to_csv(input_folder, output_folder)
    else:
        st.error("Input folder does not exist.")

if st.button("Process CSV Files"):
    if os.path.exists(output_folder):
        process_csv_files(output_folder)
    else:
        st.error("Output folder does not exist.")

