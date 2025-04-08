import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load and cache data
@st.cache_data
def load_data():
    df = pd.read_csv("filtered_data.csv")
    df.columns = df.columns.str.strip()

    # Fix HS6 formatting
    if 'HS6' in df.columns:
        df['HS6'] = df['HS6'].astype(str).apply(lambda x: '0' + x if len(x) == 5 else x)

    # Prepare HS2 display
    hs2_with_desc = df[['HS2', 'HS2_desc']].drop_duplicates().dropna()
    hs2_display = [f"{row['HS2']} - {row['HS2_desc']}" for _, row in hs2_with_desc.iterrows()]
    hs2_mapping = dict(zip(hs2_display, hs2_with_desc['HS2']))

    # Add short HS6 display
    df['HS6_desc'] = df['HS6_desc'].astype(str)
    df['HS6_display'] = df['HS6'] + " - " + df['HS6_desc'].str[:30] + "..."

    return {
        "data": df,
        "year": sorted(df['year'].dropna().unique()),
        "hs2_display": hs2_display,
        "hs2_mapping": hs2_mapping,
    }

# UI Title
st.title("📊 Export Data From China-USA")

# Load data
options = load_data()
df = options['data']

# Sidebar filters
st.sidebar.header("🔎 Filters")
selected_years = st.sidebar.multiselect("Select Years", options['year'])
selected_hs2_disp = st.sidebar.multiselect("Select HS2 Codes", options['hs2_display'])
selected_hs2 = [options['hs2_mapping'][d] for d in selected_hs2_disp]

# Filter HS6 options based on selected HS2
filtered_temp = df[df['HS2'].isin(selected_hs2)] if selected_hs2 else df
hs6_display_list = sorted(filtered_temp[['HS6', 'HS6_display']].drop_duplicates()['HS6_display'].tolist())
selected_hs6_disp = st.sidebar.multiselect("Select HS6 Codes", hs6_display_list)
selected_hs6 = [entry.split(' - ')[0] for entry in selected_hs6_disp]

# Sorting options
st.sidebar.subheader("📈 Sort Options")
sort_column = st.sidebar.selectbox("Sort By", ['value(thousands USD)', 'quantity(in metric tons)'])
sort_order = st.sidebar.radio("Select Type", ['Top N (nlargest)', 'Bottom N (nsmallest)'])
top_n = st.sidebar.number_input("Number of records", min_value=1, max_value=1000, value=10, step=1)

# Graph choice
st.sidebar.subheader("📊 Show Graph")
show_pie = st.sidebar.radio("Show Pie Chart?", ["No", "Yes"])

# Show data button
if st.button("🔍 Show Filtered Data"):
    filtered_df = df.copy()

    if selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    if selected_hs2:
        filtered_df = filtered_df[filtered_df['HS2'].isin(selected_hs2)]
    if selected_hs6:
        filtered_df = filtered_df[filtered_df['HS6'].isin(selected_hs6)]

    # Convert to numeric
    filtered_df['quantity(in metric tons)'] = pd.to_numeric(filtered_df['quantity(in metric tons)'], errors='coerce')
    filtered_df['value(thousands USD)'] = pd.to_numeric(filtered_df['value(thousands USD)'], errors='coerce')

    # Sort
    if sort_order == 'Top N (nlargest)':
        filtered_df = filtered_df.nlargest(top_n, sort_column)
    else:
        filtered_df = filtered_df.nsmallest(top_n, sort_column)

    if not filtered_df.empty:
        # Summary
        st.markdown("### 📦 Summary")
        st.markdown(f"**Total Quantity (Metric Tons):** `{filtered_df['quantity(in metric tons)'].sum():,.2f}`")
        st.markdown(f"**Total Value (Thousands USD):** `{filtered_df['value(thousands USD)'].sum():,.2f}`")

        # Table
        st.markdown(f"### Filtered Data ({len(filtered_df)} rows)")
        st.dataframe(filtered_df.head(100))

        # Download
        st.download_button("📥 Download CSV", filtered_df.to_csv(index=False), file_name="filtered_data_filtered.csv")

        # Pie chart only (if selected)
        if show_pie == "Yes":
            st.markdown("### 🧁 Pie Chart - Top Categories by Value")
            pie_data = (
                filtered_df.groupby('HS2')['value(thousands USD)']
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
                pie_data,
                labels=None,
                autopct='%1.1f%%',
                startangle=140
            )
            # Add labels above the chart
            ax.legend(wedges, pie_data.index, title="HS2", loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3)
            ax.axis('equal')
            st.pyplot(fig)

    else:
        st.warning("No data found for the selected filters.")
