#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import csv
import streamlit as st
from io import StringIO

# Function to convert a single TXT file to CSV
def txt_to_csv_single(input_file):
    try:
        processed_rows = []
        with StringIO(input_file.getvalue().decode("utf-8")) as txt_file:
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

        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(normalized_rows)
        output.seek(0)

        st.download_button(
            label="Download CSV",
            data=output.getvalue(),
            file_name=f"{os.path.splitext(input_file.name)[0]}.csv",
            mime="text/csv"
        )

        st.success(f"Converted: {input_file.name} -> {os.path.splitext(input_file.name)[0]}.csv")

    except Exception as e:
        st.error(f"Failed to convert {input_file.name}: {e}")

# Function to process a single CSV file
def process_csv_file(csv_file):
    try:
        df = pd.read_csv(csv_file)
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

        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        st.download_button(
            label="Download Processed CSV",
            data=output.getvalue(),
            file_name=f"{csv_file.name}_final",
            mime="text/csv"
        )

        st.success(f"Processed and updated: {csv_file.name}")

    except Exception as e:
        st.error(f"Failed to process {csv_file.name}: {e}")

# Streamlit UI
st.title("TXT to CSV Converter and Processor")

# File selection for TXT to CSV conversion
st.header("Convert TXT to CSV")
txt_file = st.file_uploader("Select a TXT file", type=['txt'])

if st.button("Convert to CSV"):
    if txt_file:
        txt_to_csv_single(txt_file)
    else:
        st.error("Please select a TXT file.")

# File selection for CSV processing
st.header("Process CSV File")
csv_file = st.file_uploader("Select a CSV file", type=['csv'])

if st.button("Process CSV"):
    if csv_file:
        process_csv_file(csv_file)
    else:
        st.error("Please select a CSV file to process.")

