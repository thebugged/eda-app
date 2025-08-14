import os
import io
import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm

# page configuration
st.set_page_config(
    page_title='EDA App',
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="auto"
)
st.header("Exploratory Data Analysis App")

# function to convert excel to CSV format
def excel_to_csv(file_path, sheet_name=None, header_row=None):
    """Convert Excel file to CSV format using pandas"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, engine='openpyxl')
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return pd.read_csv(csv_buffer)
    except Exception as e:
        st.error(f"Error converting Excel to CSV: {e}")
        return None

# function to load data
@st.cache_data
def load_data(file_path, file_type, sheet_name=None, header_row=None):
    try:
        if file_type == 'Excel':
            data = excel_to_csv(file_path, sheet_name=sheet_name, header_row=header_row)
        elif file_type == 'CSV':
            data = pd.read_csv(file_path)
        return data
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

@st.cache_resource
def get_pygwalker_renderer(data) -> StreamlitRenderer:
    return StreamlitRenderer(data, appearance="light")

# Initialize session state
if 'clear_data' not in st.session_state:
    st.session_state.clear_data = False

# UI Components
col1, col2 = st.columns([1.3, 4])

# file upload and selection in col1
with col1:
    
    st.markdown("**Choose a data file**")
    
    file_type = st.selectbox("File type", ["CSV", "Excel"], label_visibility="collapsed")
    
    if file_type == "CSV":
        allowed_types = ["csv"]
    else:
        allowed_types = ["xlsx", "xls"]
    
    uploaded_file = st.file_uploader(
        "Upload file",
        type=allowed_types,
        help=f"Drag and drop file here. Limit 200MB per file • {', '.join([t.upper() for t in allowed_types])}",
        label_visibility="collapsed",
        key="file_uploader" if not st.session_state.clear_data else None
    )
    
    st.markdown("")
    st.markdown("Get sample data [here](https://www.stats.govt.nz/large-datasets/csv-files-for-download)")
    
    # Clear button
    if uploaded_file:
        st.markdown("")
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.clear_data = True
            st.rerun()
    
    # Reset the clear_data flag
    if st.session_state.clear_data:
        st.session_state.clear_data = False
        uploaded_file = None
    
    if uploaded_file:
        file_path = uploaded_file
        
        if file_type == 'Excel':
            try:
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')
                sheet_name = st.selectbox("*Which sheet name in the file should be read?*", excel_file.sheet_names)
                header_row = st.number_input("*Which row contains the column names?*", 0, 100, 0)
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                sheet_name = None
                header_row = None
        else:
            sheet_name = None
            header_row = None
        
        data = load_data(file_path, file_type, sheet_name, header_row)
        
        if data is not None:
            data.columns = data.columns.str.replace('_', ' ').str.title()
            data = data.reset_index(drop=True)
            init_streamlit_comm()
    else:
        data = None

# insights and visualization in col1
with col1:
    if data is not None and isinstance(data, pd.DataFrame):
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
            if len(data.select_dtypes('object').columns) > 0:
                field_to_investigate = st.selectbox("Select Field", data.select_dtypes('object').columns)
                st.markdown("")
                value_counts = data[field_to_investigate].value_counts().reset_index().rename(columns={'index': 'Value', field_to_investigate: 'Count'}).reset_index(drop=True)
                st.dataframe(value_counts, use_container_width=True, hide_index=True)
            else:
                st.write("No categorical fields available for distribution analysis.")

# visualization in col2
with col2:
    if data is not None and isinstance(data, pd.DataFrame):
        try:
            renderer = get_pygwalker_renderer(data)
            renderer.explorer()
        except Exception as e:
            st.error(f"Error occurred: {e}")
    else:
        st.markdown("")
        st.markdown("")
        st.info("Please upload a data file to see analysis results here")
        

        st.markdown("**How to use:**")
        st.markdown("""
        1. Choose your file type (CSV or Excel) from the dropdown on the left
        2. Upload a data file using the file uploader
        3. Once loaded, explore your data with interactive visualizations
        4. Use the insights panel to view data types, summary statistics, and value distributions
        5. Create custom charts and analyses using the visualization tools
        """)