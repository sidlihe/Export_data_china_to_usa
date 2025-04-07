import streamlit as st
import pandas as pd

# Load CSV data and cache it
@st.cache_data
def load_data():
    df = pd.read_csv("filtered_data.csv")

    # Clean up column names if needed
    df.columns = df.columns.str.strip()

    # Prepare HS2 display mapping
    hs2_with_desc = df[['HS2', 'HS2_desc']].drop_duplicates().dropna()
    hs2_display = [f"{row['HS2']} - {row['HS2_desc']}" for _, row in hs2_with_desc.iterrows()]
    hs2_mapping = dict(zip(hs2_display, hs2_with_desc['HS2']))

    return {
        "data": df,
        "year": sorted(df['year'].dropna().unique()),
        "hs2_display": hs2_display,
        "hs2_mapping": hs2_mapping,
    }

# Main UI
st.title("📊 Export Data From China-USA")

# Load data and filter options
options = load_data()
df = options['data']

# Multi-select filters
selected_years = st.multiselect("Select Years", options['year'])
selected_hs2_disp = st.multiselect("Select HS2 Codes", options['hs2_display'])

# Map selected HS2 display names back to actual HS2 codes
selected_hs2 = [options['hs2_mapping'][d] for d in selected_hs2_disp]

# Filter logic
if st.button("🔍 Show Filtered Data"):
    filtered_df = df.copy()

    if selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]

    if selected_hs2:
        filtered_df = filtered_df[filtered_df['HS2'].isin(selected_hs2)]

    if not filtered_df.empty:
        # Convert to numeric for summary stats
        filtered_df['quantity(in metric tons)'] = pd.to_numeric(filtered_df['quantity(in metric tons)'], errors='coerce')
        filtered_df['value(thousands USD)'] = pd.to_numeric(filtered_df['value(thousands USD)'], errors='coerce')

        total_quantity = filtered_df['quantity(in metric tons)'].sum()
        total_value = filtered_df['value(thousands USD)'].sum()

        st.markdown("### 📦 Summary")
        st.markdown(f"**Total Traded Quantity (Metric Tons):** `{total_quantity:,.2f}`")
        st.markdown(f"**Total Value (Thousands USD):** `{total_value:,.2f}`")

        st.markdown(f"### Filtered Data ({len(filtered_df)} rows)")
        st.dataframe(filtered_df.head(100))

        st.download_button("📥 Download CSV", filtered_df.to_csv(index=False), file_name="filtered_data_filtered.csv")
    else:
        st.warning("No data found for the selected filters.")
