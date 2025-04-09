import streamlit as st
import pandas as pd
import pymysql

# MySQL connection
def get_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        database='export_data',
        charset='utf8mb4'
    )

# Load filter options
@st.cache_data
def get_filter_options():
    conn = get_connection()
    df = pd.read_sql("SELECT DISTINCT year, HS2, HS2_desc, exporter, importer FROM filtered_export_data", conn)
    conn.close()

    hs2_with_desc = df[['HS2', 'HS2_desc']].drop_duplicates().dropna()
    hs2_display = [f"{row['HS2']} - {row['HS2_desc']}" for _, row in hs2_with_desc.iterrows()]
    hs2_mapping = dict(zip(hs2_display, hs2_with_desc['HS2']))

    return {
        "year": sorted(df['year'].dropna().unique()),
        "hs2_display": hs2_display,
        "hs2_mapping": hs2_mapping,
    }

# Main UI
st.title("📊 Export Data From China-USA")

# Load filter options
options = get_filter_options()

# Multi-select filters
selected_years = st.multiselect("Select Years", options['year'])
selected_hs2_disp = st.multiselect("Select HS2 Codes", options['hs2_display'])

# Map selected HS2 display names back to actual HS2 codes
selected_hs2 = [options['hs2_mapping'][d] for d in selected_hs2_disp]

# Apply filters
if st.button("🔍 Show Filtered Data"):
    where_clauses = []
    values = []

    if selected_years:
        placeholders = ','.join(['%s'] * len(selected_years))
        where_clauses.append(f"year IN ({placeholders})")
        values.extend(selected_years)

    if selected_hs2:
        placeholders = ','.join(['%s'] * len(selected_hs2))
        where_clauses.append(f"HS2 IN ({placeholders})")
        values.extend(selected_hs2)

    where_sql = " AND ".join(where_clauses)
    query = "SELECT * FROM filtered_export_data"
    if where_sql:
        query += " WHERE " + where_sql

    conn = get_connection()
    df = pd.read_sql(query, conn, params=values)
    conn.close()

    if not df.empty:
        # Convert to numeric for summary stats
        df['quantity(in metric tons)'] = pd.to_numeric(df['quantity(in metric tons)'], errors='coerce')
        df['value(thousands USD)'] = pd.to_numeric(df['value(thousands USD)'], errors='coerce')

        # Show summary stats
        total_quantity = df['quantity(in metric tons)'].sum()
        total_value = df['value(thousands USD)'].sum()

        st.markdown("### 📦 Summary")
        st.markdown(f"**Total Traded Quantity (Metric Tons):** `{total_quantity:,.2f}`")
        st.markdown(f"**Total Value (Thousands USD):** `{total_value:,.2f}`")

        # Show filtered data
        st.markdown(f"### Filtered Data ({len(df)} rows)")
        st.dataframe(df.head(100))

        # Download button
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="filtered_data.csv")
    else:
        st.warning("No data found for the selected filters.")
