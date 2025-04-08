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

    # Drop unwanted columns
    df = df.drop(columns=[col for col in ['exporter', 'importer', 'HS6_display'] if col in df.columns], errors='ignore')

    # Prepare HS2 display
    hs2_with_desc = df[['HS2', 'HS2_desc']].drop_duplicates().dropna()
    hs2_display = [f"{row['HS2']} - {row['HS2_desc']}" for _, row in hs2_with_desc.iterrows()]
    hs2_mapping = dict(zip(hs2_display, hs2_with_desc['HS2']))

    return {
        "data": df,
        "year": sorted(df['year'].dropna().unique()),
        "hs2_display": hs2_display,
        "hs2_mapping": hs2_mapping,
    }

# Format numbers with commas
def format_number(num):
    try:
        return f"{int(num):,}"
    except:
        return num

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
hs6_display_list = sorted(filtered_temp[['HS6', 'HS6_desc']].drop_duplicates()
                          .apply(lambda row: f"{row['HS6']} - {row['HS6_desc'][:30]}...", axis=1).tolist())
selected_hs6_disp = st.sidebar.multiselect("Select HS6 Codes", hs6_display_list)
selected_hs6 = [entry.split(' - ')[0] for entry in selected_hs6_disp]

# Sorting options
st.sidebar.subheader("📈 Sort Options")
sort_column = st.sidebar.selectbox("Sort By", ['value(thousands USD)', 'quantity(in metric tons)'])
sort_order = st.sidebar.radio("Select Type", ['All Data', 'Top N (nlargest)', 'Bottom N (nsmallest)'])
top_n = st.sidebar.number_input("Number of records", min_value=1, max_value=1000, value=10, step=1)

# # Graph choice
# st.sidebar.subheader("📊 Show Graph")
# show_pie = st.sidebar.radio("Show Pie Chart?", ["No", "Yes"])

# Function to filter and sort
def get_filtered_data():
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
    elif sort_order == 'Bottom N (nsmallest)':
        filtered_df = filtered_df.nsmallest(top_n, sort_column)

    return filtered_df

# Button: Show Filtered Data
show_filtered = st.button("🔍 Show Filtered Data")

# Show preview (if not showing filtered data)
if not show_filtered:
    st.markdown("### 📋 Preview (Top 10 Rows)")
    preview_df = df.copy().head(10)
    preview_df['quantity(in metric tons)'] = preview_df['quantity(in metric tons)'].apply(format_number)
    preview_df['value(thousands USD)'] = preview_df['value(thousands USD)'].apply(format_number)
    st.dataframe(preview_df)

# Show Filtered Data
if show_filtered:
    filtered_df = get_filtered_data()

    if not filtered_df.empty:
        # Summary
        st.markdown("### 📦 Summary")
        st.markdown(f"**Total Quantity (Metric Tons):** `{filtered_df['quantity(in metric tons)'].sum():,.0f}`")
        st.markdown(f"**Total Value (Thousands USD):** `{filtered_df['value(thousands USD)'].sum():,.0f}`")

        # Format columns
        filtered_df['quantity(in metric tons)'] = filtered_df['quantity(in metric tons)'].apply(format_number)
        filtered_df['value(thousands USD)'] = filtered_df['value(thousands USD)'].apply(format_number)

        # Table
        st.markdown(f"### Filtered Data ({len(filtered_df)} rows)")
        st.dataframe(filtered_df.head(100))

        # Download
        st.download_button("📥 Download CSV", filtered_df.to_csv(index=False), file_name="filtered_data_filtered.csv")

        # Pie chart
        # if show_pie == "Yes":
        #     st.markdown("### 🧁 Pie Chart - Top Categories by Value")
        #     pie_data = (
        #         df[df['HS2'].isin(filtered_df['HS2'])]
        #         .groupby('HS2')['value(thousands USD)']
        #         .sum()
        #         .sort_values(ascending=False)
        #         .head(10)
        #     )
        #     fig, ax = plt.subplots()
        #     wedges, _, autotexts = ax.pie(
        #         pie_data,
        #         labels=None,
        #         autopct='%1.1f%%',
        #         startangle=140
        #     )
        #     ax.legend(wedges, pie_data.index, title="HS2", loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3)
        #     ax.axis('equal')
        #     st.pyplot(fig)

    else:
        st.warning("No data found for the selected filters.")
