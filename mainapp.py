
import openpyxl
import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm

# Page Configuration
st.set_page_config(
    page_title='EDA App',
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("### Exploratory Data Analysis App")
st.divider()

# Function to Load Data
@st.cache_data(experimental_allow_widgets=True)
def load_data(file_path, file_type, sheet_name=None, header_row=None):
    try:
        if file_type == 'Excel':
            data = pd.read_excel(file_path, header=header_row, sheet_name=sheet_name, engine='openpyxl')
        elif file_type == 'CSV':
            data = pd.read_csv(file_path)
        return data
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Function to Get Pygwalker Renderer
@st.cache_resource
def get_pygwalker_renderer(data) -> StreamlitRenderer:
    config = {
        "theme": "light",
        "defaultAggregated": True,
        "geoms": ["auto"],
        "stack": "stack",
        "showActions": False,
        "interactiveScale": False,
        "sorted": "none",
        "size": {
            "mode": "auto",
            "width": "auto",
            "height": "auto"
        },
        "format": {}
    }

    return StreamlitRenderer(data, config=config)

# UI Components
col1, col2 = st.columns([1.3, 4])

# File Upload and Selection in col1
with col1:
    file_type = st.selectbox("**Choose file type 📑**", ["CSV", "Excel"])
    st.markdown("")
    uploaded_file = st.file_uploader("**Upload file 📤**")

    if uploaded_file:
        file_path = uploaded_file

        if file_type == 'excel':
            sheet_name = st.selectbox("*Which sheet name in the file should be read?*", pd.ExcelFile(file_path).sheet_names)
            header_row = st.number_input("*Which row contains the column names?*", 0, 100, 0)
        else:
            sheet_name = None
            header_row = None

        data = load_data(file_path, file_type, sheet_name, header_row)
        if data is not None:
            data.columns = data.columns.str.replace('_', ' ').str.title()
            data = data.reset_index()

            init_streamlit_comm()

# Insights and Visualization in col1
with col1:
    if uploaded_file and data is not None:
        st.divider()
        
        selected_insight = st.radio("**More insights 🔍**", [
            "Field Data Types",
            "Data Summary",
            "Value Distribution"
        ])

        if selected_insight == 'Field Data Types':
            st.markdown("**Field Data Types**")
            field_descriptions = data.dtypes.reset_index().rename(columns={'index': 'Field Name', 0: 'Field Type'}).sort_values(by='Field Type', ascending=False).reset_index(drop=True)
            st.dataframe(field_descriptions, use_container_width=True, hide_index=True)
        
        elif selected_insight == 'Data Summary':
            st.markdown("**Data Summary**")
            summary_statistics = pd.DataFrame(data.describe(include='all').round(2).fillna(''))
            null_counts = pd.DataFrame(data.isnull().sum()).rename(columns={0: 'Count Null'}).T
            summary_statistics = pd.concat([null_counts, summary_statistics]).copy()
            st.dataframe(summary_statistics, use_container_width=True)
        
        elif selected_insight == 'Value Distribution':
            st.markdown("**Value Distribution**")
            field_to_investigate = st.selectbox("Select Field", data.select_dtypes('object').columns)
            st.markdown("")
            value_counts = data[field_to_investigate].value_counts().reset_index().rename(columns={'index': 'Value', field_to_investigate: 'Count'}).reset_index(drop=True)
            st.dataframe(value_counts, use_container_width=True, hide_index=True)

# Visualization in col2
with col2:
    if uploaded_file and data is not None:
        try:
            renderer = get_pygwalker_renderer(data)
            renderer.explorer()
        except Exception as e:
            st.error(f"Error occurred: {e}")

st.markdown("")
st.markdown("👨🏾‍💻 by [thebugged](https://github.com/thebugged)")