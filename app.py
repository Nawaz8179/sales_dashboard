import pandas as pd
import plotly.express as px
import streamlit as st

# Set up Streamlit page configuration
st.set_page_config(page_title="Sales_Dashboard", page_icon=":bar_chart:", layout="wide")

# Load data from Excel file
df = pd.read_excel(
    io='TRANSFER.xlsx',
    engine='openpyxl',
    sheet_name='transfer',
    usecols='A:F',  # Adjust columns as needed
    nrows=27458,
)

# Convert DATE column to datetime
df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

# Convert RSP, SECTION, and SIZE columns to string
df['RSP'] = df['RSP'].astype(str)
df['SECTION'] = df['SECTION'].astype(str)
df['SIZE'] = df['SIZE'].astype(str)

# Extract month and year for aggregation
df['Month'] = df['DATE'].dt.to_period('M').astype(str)  # 'YYYY-MM' format

# Sidebar - Filter selection
with st.sidebar:
    st.header("Filters")

    # Expandable sections
    with st.expander("Date Range"):
        min_date = df['DATE'].min()
        max_date = df['DATE'].max()
        start_date, end_date = st.date_input(
            "Select date range:",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

    with st.expander("RSP Selection"):
        search_rsp = st.text_input("Search RSP:", "")
        rsp_options = df["RSP"].unique()
        filtered_rsp_options = [rsp for rsp in rsp_options if search_rsp.lower() in rsp.lower()]
        select_all_rsp = st.checkbox("Select All RSP", value=len(filtered_rsp_options) == len(rsp_options))
        selected_rsp = st.multiselect(
            "Select the RSP:",
            options=filtered_rsp_options,
            default=filtered_rsp_options if select_all_rsp else [],
            key="rsp_select"
        )

    with st.expander("Section Selection"):
        search_section = st.text_input("Search Section:", "")
        section_options = df["SECTION"].unique()
        filtered_section_options = [section for section in section_options if search_section.lower() in section.lower()]
        select_all_section = st.checkbox("Select All Sections", value=len(filtered_section_options) == len(section_options))
        selected_sections = st.multiselect(
            "Select the Sections:",
            options=filtered_section_options,
            default=filtered_section_options if select_all_section else [],
            key="section_select"
        )

    with st.expander("Size Selection"):
        search_size = st.text_input("Search Size:", "")
        size_options = df["SIZE"].unique()
        filtered_size_options = [size for size in size_options if search_size.lower() in size.lower()]
        select_all_size = st.checkbox("Select All Sizes", value=len(filtered_size_options) == len(size_options))
        selected_sizes = st.multiselect(
            "Select the Sizes:",
            options=filtered_size_options,
            default=filtered_size_options if select_all_size else [],
            key="size_select"
        )

# Filter dataframe based on selected RSP, SECTION, SIZE, and date range
filtered_df = df[
    (df["RSP"].isin(selected_rsp)) & 
    (df["SECTION"].isin(selected_sections)) & 
    (df["SIZE"].isin(selected_sizes)) & 
    (df['DATE'] >= pd.Timestamp(start_date)) & 
    (df['DATE'] <= pd.Timestamp(end_date))
]

# Aggregate by RSP
rsp_sales = filtered_df.groupby('RSP').agg({
    'SALE QTY': 'sum'
}).reset_index()

# Aggregate by SECTION
section_sales = filtered_df.groupby('SECTION').agg({
    'SALE QTY': 'sum'
}).reset_index()

# Aggregate by SIZE
size_sales = filtered_df.groupby('SIZE').agg({
    'SALE QTY': 'sum'
}).reset_index()

# Monthly analysis for RSP
monthly_rsp_analysis = pd.pivot_table(
    filtered_df,
    values='SALE QTY',
    index='Month',
    columns='RSP',
    aggfunc='sum',
    fill_value=0
)

# Monthly analysis for SECTION
monthly_section_analysis = pd.pivot_table(
    filtered_df,
    values='SALE QTY',
    index='Month',
    columns='SECTION',
    aggfunc='sum',
    fill_value=0
)

# Monthly analysis for SIZE
monthly_size_analysis = pd.pivot_table(
    filtered_df,
    values='SALE QTY',
    index='Month',
    columns='SIZE',
    aggfunc='sum',
    fill_value=0
)

# Display the filtered DataFrame in the Streamlit app
st.dataframe(filtered_df)

# Plotting the bar chart with Plotly
fig_bar = px.bar(
    rsp_sales,
    x='RSP',
    y='SALE QTY',
    title='Sales Quantity by RSP',
    text='SALE QTY',  # Add data labels
)

# Customize layout to ensure labels are visible
fig_bar.update_layout(
    xaxis_title='RSP',
    yaxis_title='Sales Quantity',
    xaxis_tickangle=-45  # Adjust angle if needed for better visibility
)

# Update trace to show text labels on bars
fig_bar.update_traces(texttemplate='%{text:.0f}', textposition='outside')

# Display the bar chart
st.plotly_chart(fig_bar)

# Plotting the pie chart for RSP with Plotly
fig_pie_rsp = px.pie(
    rsp_sales,
    names='RSP',
    values='SALE QTY',
    title='Sales Quantity Distribution by RSP',
    hole=0.3  # Make it a donut chart if desired
)

# Customize layout for the pie chart
fig_pie_rsp.update_layout(
    showlegend=True,
    legend_title='RSP',
)

# Display the pie chart
st.plotly_chart(fig_pie_rsp)

# Plotting the pie chart for Sections with Plotly
fig_pie_section = px.pie(
    section_sales,
    names='SECTION',
    values='SALE QTY',
    title='Sales Quantity Distribution by Section',
    hole=0.3  # Make it a donut chart if desired
)

# Customize layout for the pie chart
fig_pie_section.update_layout(
    showlegend=True,
    legend_title='Section',
)

# Display the pie chart
st.plotly_chart(fig_pie_section)

# Plotting the pie chart for Sizes with Plotly
fig_pie_size = px.pie(
    size_sales,
    names='SIZE',
    values='SALE QTY',
    title='Sales Quantity Distribution by Size',
    hole=0.3  # Make it a donut chart if desired
)

# Customize layout for the pie chart
fig_pie_size.update_layout(
    showlegend=True,
    legend_title='Size',
)

# Display the pie chart
st.plotly_chart(fig_pie_size)

# Display combined monthly analysis in separate columns
st.subheader("Combined Monthly Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Monthly RSP Analysis")
    st.dataframe(monthly_rsp_analysis)

with col2:
    st.subheader("Monthly Section Analysis")
    st.dataframe(monthly_section_analysis)

with col3:
    st.subheader("Monthly Size Analysis")
    st.dataframe(monthly_size_analysis)

# Pivot table with hierarchical index
pivot_table = pd.pivot_table(
    filtered_df,
    values='SALE QTY',
    index=['SECTION', 'RSP', 'SIZE'],
    aggfunc='sum',
    fill_value=0
).reset_index()

# Display the pivot table in Streamlit app
st.subheader("Pivot Table Analysis")
st.dataframe(pivot_table)
