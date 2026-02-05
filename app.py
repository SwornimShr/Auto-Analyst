import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_csv_file, get_dataframe_summary, validate_dataframe
from agent import DataAnalysisAgent, normalize_query
from tracker import QueryTracker


# Page config
st.set_page_config(
    page_title="Auto-Analyst",
    page_icon="📊",
    layout="wide"
)

# Initialize tracker
tracker = QueryTracker()


def initialize_session_state():
    """Set up session state variables."""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False


def render_sidebar():
    """Render sidebar with stats and controls."""
    with st.sidebar:
        st.title("📊 Auto-Analyst")
        st.markdown("AI-powered CSV analysis using natural language")
        
        st.divider()
        
        # API Key input
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=st.secrets.get("GROQ_API_KEY", ""),
            help="Enter your Groq API key"
        )
        
        if api_key:
            st.success("API Key loaded ✓")
        
        st.divider()
        
        # Stats section
        st.subheader("Query Statistics")
        total = tracker.get_total_queries()
        success_rate = tracker.get_success_rate()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Queries", total)
        col2.metric("Success Rate", f"{success_rate:.1f}%")
        
        if st.button("Clear History"):
            tracker.clear_history()
            st.rerun()
        
        return api_key


def render_data_upload():
    """Handle CSV file upload and preview."""
    st.header("1️⃣ Upload Your Data")
    
    # Add custom styling for upload area
    st.markdown("""
        <style>
        [data-testid="stFileUploader"] {
            border: 3px dashed #4CAF50;
            border-radius: 10px;
            padding: 30px;
            background-color: #f8f9fa;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #45a049;
            background-color: #e8f5e9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Clear instructions
    st.markdown("""
    **📁 Upload your CSV file using one of these methods:**
    - Click the button below to browse files
    - **OR** drag and drop your file into the box below
    """)
    
    uploaded_file = st.file_uploader(
        "Drop your CSV file here or click to browse",
        type=['csv'],
        help="Drag and drop a CSV file into this area, or click 'Browse files' to select one",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        with st.spinner("Loading CSV..."):
            df = load_csv_file(uploaded_file)
            
            if df is not None:
                is_valid, error_msg = validate_dataframe(df)
                
                if is_valid:
                    st.session_state.df = df
                    st.session_state.data_loaded = True
                    st.success(f"✓ Loaded {len(df)} rows and {len(df.columns)} columns")
                    
                    # Show preview
                    with st.expander("📋 Data Preview", expanded=True):
                        st.dataframe(df.head(), use_container_width=True)
                    
                    # Show summary stats
                    with st.expander("📈 Summary Statistics"):
                        summary = get_dataframe_summary(df)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Rows", summary['num_rows'])
                        col2.metric("Columns", summary['num_columns'])
                        col3.metric("Memory (MB)", f"{summary['memory_usage']:.2f}")
                        
                        st.write("**Column Types:**")
                        dtype_df = pd.DataFrame({
                            'Column': summary['columns'],
                            'Type': [str(summary['dtypes'][col]) for col in summary['columns']],
                            'Missing': [summary['missing_values'][col] for col in summary['columns']]
                        })
                        st.dataframe(dtype_df, use_container_width=True)
                else:
                    st.error(f"Invalid dataframe: {error_msg}")
            else:
                st.error("Failed to load CSV. Check file encoding.")


def render_query_interface(api_key: str):
    """Render the query interface."""
    if not st.session_state.data_loaded:
        st.info("👆 Please upload a CSV file first")
        return
    
    st.header("2️⃣ Ask Questions")
    
    # Debug mode toggle (hidden in expander)
    with st.expander("🔧 Debug Options", expanded=False):
        debug_mode = st.checkbox("Show detailed output (for debugging)", value=False)
    
    # Initialize agent if needed
    if st.session_state.agent is None and api_key:
        with st.spinner("Initializing AI agent..."):
            agent = DataAnalysisAgent(api_key)
            agent.initialize_agent(st.session_state.df)
            st.session_state.agent = agent
    
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar")
        return
    
    # Add helpful query examples
    with st.expander("💡 Need help? Click for query examples", expanded=False):
        st.markdown("""
        **Try these queries** (copy and paste to start!):
        
        **🔰 Beginner (Always Work):**
        - `show all rows`
        - `show first 5 rows`
        - `calculate the average salary`
        - `count total number of rows`
        
        **📊 Filtering & Sorting:**
        - `show rows where salary > 80000`
        - `sort by salary descending and show first 5 rows`
        - `show rows where department equals Engineering`
        
        **📈 Analysis:**
        - `calculate average salary by department`
        - `show the row where salary is maximum`
        - `count employees in each department`
        
        **💡 Tips:**
        - Start with "show" or "calculate"
        - Use exact column names from the preview
        - Be specific with numbers (e.g., "first 5" not "some")
        - Keep queries simple for best results
        """)
    
    # Query input
    question = st.text_area(
        "Enter your question:",
        placeholder="e.g., What are the top 5 rows sorted by sales?",
        height=100
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_btn = st.button("🔍 Analyze", type="primary")
    
    if analyze_btn and question:
        # Show normalized query if it's different
        normalized = normalize_query(question)
        if normalized != question and len(normalized) > len(question) * 0.7:
            st.info(f"🔄 Interpreted as: *{normalized}*")
        
        with st.spinner("Analyzing..."):
            result = st.session_state.agent.query(question)
            
            # Log the query
            tracker.log_query(
                query=question,
                success=result['success'],
                error_msg=result.get('error')
            )
            
            # Display results
            if result['success']:
                st.success("✓ Analysis complete!")
                
                output = result['result']
                
                # Debug mode
                if debug_mode:
                    with st.expander("🔍 Debug Info", expanded=True):
                        st.write(f"**Result Type:** `{type(output).__name__}`")
                        st.write(f"**Result Value:** `{repr(output)}`")
                        if hasattr(output, '__len__'):
                            st.write(f"**Length:** {len(output)}")
                
                st.write("**Result:**")
                
                # Handle different output types
                if isinstance(output, pd.DataFrame):
                    st.dataframe(output, use_container_width=True)
                elif isinstance(output, pd.Series):
                    # Convert Series to DataFrame for better display
                    series_df = output.to_frame()
                    # If index has a name, use it; otherwise call it 'Index'
                    if series_df.index.name is None:
                        series_df.index.name = 'Category'
                    # If column has no name, use the series name or 'Value'
                    if series_df.columns[0] is None or series_df.columns[0] == 0:
                        series_df.columns = [output.name if output.name else 'Value']
                    st.dataframe(series_df, use_container_width=True)
                elif isinstance(output, (int, float)):
                    st.metric("Answer", output)
                elif isinstance(output, list):
                    st.write(output)
                elif isinstance(output, dict):
                    st.json(output)
                elif output is None or str(output).strip() == "":
                    st.warning("⚠️ The query completed but returned no visible output. Try rephrasing your question.")
                else:
                    # For string or other types
                    result_str = str(output).strip()
                    
                    # Check if this looks like a DataFrame string representation
                    # (has column names in first line and data rows)
                    lines = result_str.split('\n')
                    if len(lines) > 2 and any(col in lines[0] for col in ['employee_name', 'department', 'salary', 'age']):
                        # This is likely a DataFrame that got stringified
                        st.warning("⚠️ Result is showing as text. The data is correct but formatting failed.")
                        st.text(result_str)
                        st.info("💡 The query worked! Try enabling Debug Mode to see the raw data type.")
                    elif 'dtype:' in result_str and '\n' in result_str:
                        # Series string representation
                        st.text(result_str)
                        st.info("💡 Tip: The result is shown above. For better formatting, try rephrasing as 'show as a table' or 'display as dataframe'")
                    elif result_str:
                        st.write(result_str)
                    else:
                        st.warning("⚠️ The query completed but returned an empty result.")
            else:
                st.error(f"❌ Error: {result['error']}")
                
                # Show helpful suggestions based on error type
                if "parse" in result['error'].lower() or "format" in result['error'].lower():
                    st.info("💡 **Try these working queries instead:**\n- `show all rows`\n- `calculate average salary`\n- `show first 10 rows`")
                elif "column" in result['error'].lower():
                    st.info(f"💡 **Available columns:** {', '.join(st.session_state.df.columns.tolist())}")
                else:
                    st.info("💡 Try rephrasing with 'show', 'calculate', or 'display' at the start")


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Render sidebar and get API key
    api_key = render_sidebar()
    
    # Main content
    render_data_upload()
    
    st.divider()
    
    render_query_interface(api_key)
    
    # Recent queries section
    if tracker.get_total_queries() > 0:
        st.divider()
        with st.expander("📜 Recent Queries"):
            recent = tracker.get_recent_queries(5)
            for q in reversed(recent):
                status = "✅" if q['success'] else "❌"
                st.write(f"{status} {q['query']}")
                if not q['success']:
                    st.caption(f"Error: {q['error']}")


if __name__ == "__main__":
    main()
