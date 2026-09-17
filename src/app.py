import streamlit as st
import json
import os
import sys
import re

# Ensure src directory is in sys.path for Streamlit Cloud deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from database import (
    init_mysql_database, 
    init_sqlite_database, 
    init_csv_database, 
    get_response,
    transcribe_audio
)
import pandas as pd
import plotly.express as px
from logging_utils import setup_logging

load_dotenv()

# Page Configuration & Custom CSS
st.set_page_config(
    page_title="QueryAI • Text-to-SQL Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Seamless ChatGPT / Claude Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Badges */
    .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.84rem;
        font-weight: 500;
        color: #e5e7eb;
    }
    .db-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.84rem;
        font-weight: 500;
    }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 24px 20px 12px 20px;
        max-width: 760px;
        margin: 0 auto;
    }
    .hero-icon {
        font-size: 2.5rem;
        display: inline-block;
        margin-bottom: 6px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #9ca3af;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* UNIFIED PROMPT BAR: Merge chat input & microphone into ONE seamless container */
    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) {
        display: flex !important;
        align-items: center !important;
        background: #212121 !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 28px !important;
        padding: 2px 10px 2px 4px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        margin-top: 10px !important;
    }

    /* Remove isolated chat input border so it joins the mic button seamlessly */
    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Make the mic button look like an integrated chatbar icon */
    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        color: #9ca3af !important;
        font-size: 1.15rem !important;
        padding: 4px 8px !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) button[kind="secondary"]:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

if 'logging_initialized' not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True

def get_server_api_key():
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

# Session State Initialization
if 'visualizations' not in st.session_state:
    st.session_state.visualizations = {}
if 'sql_history' not in st.session_state:
    st.session_state.sql_history = {}
if 'chat_history_data' not in st.session_state:
    st.session_state.chat_history_data = []
if 'db' not in st.session_state:
    demo_db_path = "data/demo.db"
    if os.path.exists(demo_db_path):
        st.session_state.db = init_sqlite_database(demo_db_path)
        st.session_state.current_db = "student_db"
        st.session_state.db_type = "🎓 Student DB"
        st.session_state.source_mode = "🎓 Student DB (Instant Demo)"
    else:
        st.session_state.db = None
        st.session_state.current_db = None
        st.session_state.db_type = None
        st.session_state.source_mode = "🎓 Student DB (Instant Demo)"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pending_voice_prompt' not in st.session_state:
    st.session_state.pending_voice_prompt = None

def reset_chat():
    st.session_state.chat_history = []
    st.session_state.visualizations = {}
    st.session_state.sql_history = {}
    st.rerun()

def process_user_prompt(prompt):
    if not prompt or not prompt.strip():
        return

    if prompt.strip().lower() in ["clear", "reset", "new chat", "cls"]:
        reset_chat()
        return

    server_key = get_server_api_key()
    user_key = st.session_state.get("custom_groq_key", "").strip()
    active_key = user_key or server_key

    if not active_key:
        st.error("⚠️ No Groq API Key found. Configure it in ⚙️ Settings.")
        return

    if not st.session_state.db:
        st.warning("⚠️ Please select or connect a database in the sidebar first!")
        return

    st.session_state.chat_history.append(HumanMessage(content=prompt))
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Analyzing schema, generating SQL & fetching results..."):
            model_to_use = st.session_state.get("selected_model", "openai/gpt-oss-20b")
            response, query_result, is_visualization_requested, sanitized_query = get_response(
                prompt, 
                st.session_state.db, 
                st.session_state.chat_history,
                st.session_state.current_db or "student_db",
                model_name=model_to_use,
                api_key=active_key
            )
            
            if sanitized_query:
                with st.expander("⚡ View Generated SQL", expanded=False):
                    st.code(sanitized_query, language="sql")
            
            st.markdown(response)

            viz_data = None
            if is_visualization_requested and query_result and isinstance(query_result, list) and len(query_result) > 0:
                try:
                    df = pd.DataFrame(query_result)
                    if len(df.columns) >= 2:
                        if "pie" in prompt.lower():
                            fig = px.pie(df, names=df.columns[0], values=df.columns[1], title="Data Breakdown", template="plotly_dark")
                            chart_type = "pie"
                        else:
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1], title="Data Comparison", template="plotly_dark")
                            chart_type = "bar"
                        
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True, key=f"viz_{datetime.now().timestamp()}")
                        viz_data = {
                            "type": chart_type,
                            "columns": df.columns.tolist(),
                            "data": df.to_dict('list')
                        }
                    else:
                        st.info("💡 Single column result; chart omitted.")
                except Exception as e:
                    st.error(f"Visualization error: {str(e)}")

            msg_index = len(st.session_state.chat_history)
            st.session_state.visualizations[msg_index] = viz_data
            st.session_state.sql_history[msg_index] = sanitized_query
            
            history_entry = {
                'timestamp': datetime.now().strftime("%H:%M"),
                'database': st.session_state.current_db,
                'query': prompt,
                'response': response,
                'sql': sanitized_query,
                'visualization': viz_data
            }
            st.session_state.chat_history_data.append(history_entry)

    st.session_state.chat_history.append(AIMessage(content=response))

def render_sidebar():
    st.markdown("### ⚡ **QueryAI**")
    st.caption("AI Relational Database Copilot")
    
    if st.button("➕  New Chat", use_container_width=True):
        reset_chat()
    
    st.markdown("---")
    
    # 1. VISIBLE RADIO SELECTION (No dropdown hiding features!)
    st.markdown("##### 📦 Active Data Engine")
    source_options = [
        "🎓 Student DB (Instant Demo)",
        "👕 Clothing DB (Instant Demo)",
        "📁 Upload CSV / SQLite",
        "🔌 Remote MySQL Server"
    ]
    
    current_index = 0
    if st.session_state.get("source_mode") in source_options:
        current_index = source_options.index(st.session_state["source_mode"])
        
    chosen_source = st.radio(
        "Choose Data Source:",
        source_options,
        index=current_index,
        label_visibility="collapsed"
    )
    
    if chosen_source != st.session_state.get("source_mode"):
        st.session_state.source_mode = chosen_source
        if chosen_source == "🎓 Student DB (Instant Demo)":
            st.session_state.db = init_sqlite_database("data/demo.db")
            st.session_state.current_db = "student_db"
            st.session_state.db_type = "🎓 Student DB"
            reset_chat()
        elif chosen_source == "👕 Clothing DB (Instant Demo)":
            st.session_state.db = init_sqlite_database("data/demo.db")
            st.session_state.current_db = "clothing"
            st.session_state.db_type = "👕 Clothing DB"
            reset_chat()
        elif chosen_source == "📁 Upload CSV / SQLite":
            st.session_state.db_type = "📁 Custom Upload"
        elif chosen_source == "🔌 Remote MySQL Server":
            st.session_state.db_type = "🔌 MySQL"

    # Contextual controls for Upload or MySQL
    if chosen_source == "🎓 Student DB (Instant Demo)":
        st.caption("🟢 Pre-loaded with `students`, `courses`, and `marks`.")

    elif chosen_source == "👕 Clothing DB (Instant Demo)":
        st.caption("🟢 Pre-loaded with `t_shirts` and `discounts`.")

    elif chosen_source == "📁 Upload CSV / SQLite":
        st.caption("Drag & drop any CSV or SQLite database:")
        uploaded_file = st.file_uploader("Upload dataset", type=["csv", "db", "sqlite"], label_visibility="collapsed")
        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(2), use_container_width=True)
                t_name = uploaded_file.name.rsplit(".", 1)[0]
                if st.button(f"Load `{t_name}` Table", use_container_width=True):
                    st.session_state.db = init_csv_database(df, t_name)
                    st.session_state.current_db = t_name
                    st.session_state.db_type = f"CSV: {t_name}"
                    st.success(f"Connected to `{t_name}`!")
                    reset_chat()
            else:
                with open(f"data/{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.db = init_sqlite_database(f"data/{uploaded_file.name}")
                st.session_state.current_db = uploaded_file.name
                st.session_state.db_type = f"SQLite: {uploaded_file.name}"
                st.success(f"Connected to `{uploaded_file.name}`!")
                reset_chat()

    elif chosen_source == "🔌 Remote MySQL Server":
        host = st.text_input("Host", value="localhost")
        port = st.text_input("Port", value="3306")
        user = st.text_input("User", value="root")
        pwd = st.text_input("Password", type="password", value="root")
        db_name = st.selectbox("Database", ["student_db", "clothing"])
        if st.button("Connect MySQL", use_container_width=True):
            try:
                st.session_state.db = init_mysql_database(user, pwd, host, port, db_name)
                st.session_state.current_db = db_name
                st.session_state.db_type = f"MySQL: {db_name}"
                st.success(f"Connected to `{db_name}`!")
                reset_chat()
            except Exception as e:
                st.error(f"Connection failed: {e}")

    # Schema inspector
    if st.session_state.db:
        with st.expander("🔍 View Table Schema"):
            tables = st.session_state.db.get_usable_table_names()
            st.write("**Tables:**", tables)

    st.markdown("---")
    
    # Recent Chats list
    st.markdown("##### 💬 Recent Conversations")
    history = st.session_state.chat_history_data
    if history:
        for i, item in enumerate(reversed(history[-5:])):
            q_text = item.get('query', 'Query')
            if len(q_text) > 26:
                q_text = q_text[:23] + "..."
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.caption(f"💬 {q_text}")
            with col_b:
                st.caption(f"{item.get('timestamp', '')}")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history_data = []
            reset_chat()
    else:
        st.caption("No past conversations yet.")

    # Settings popover for LLM & API key
    st.markdown("<br>", unsafe_allow_html=True)
    with st.popover("⚙️ LLM & Settings", use_container_width=True):
        st.markdown("#### 🤖 Model & API Configuration")
        model_options = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
        st.session_state.selected_model = st.selectbox("Active LLM:", model_options, index=0)
        
        s_key = get_server_api_key()
        if s_key:
            st.success("🟢 Cloud API Key Active (Secure)")
            st.caption("Your master key is safely stored on the cloud server.")
            st.text_input("Custom API Key (Optional Override)", type="password", placeholder="gsk_...", key="custom_groq_key")
        else:
            st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="custom_groq_key", help="Free key from console.groq.com")

def render_main():
    # Top Bar Header
    top_col1, top_col2 = st.columns([4, 2])
    with top_col1:
        cur_db = st.session_state.get("db_type") or "No Database"
        cur_model = st.session_state.get("selected_model", "openai/gpt-oss-20b").split("/")[-1]
        st.markdown(f'<div style="display:flex; gap:8px; align-items:center;"><span class="model-badge">⚡ {cur_model}</span><span class="db-badge">📦 {cur_db}</span></div>', unsafe_allow_html=True)
    
    with top_col2:
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            with st.popover("🔍 Schema"):
                if st.session_state.db:
                    st.write("**Active Tables:**")
                    st.write(st.session_state.db.get_usable_table_names())
                else:
                    st.write("No database connected.")
        with btn_c2:
            if st.button("➕ Clear", use_container_width=True):
                reset_chat()

    st.markdown("<hr style='margin:10px 0; border:none; border-top:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    # Empty State: Dynamic Suggestions Based on Active Data Source!
    if not st.session_state.chat_history:
        current_db_id = st.session_state.get("current_db", "student_db")
        source_mode = st.session_state.get("source_mode", "")
        
        st.markdown("""
        <div class="hero-container">
            <div class="hero-icon">⚡</div>
            <div class="hero-title">What would you like to analyze?</div>
            <div class="hero-subtitle">Ask questions in natural language, speak with the mic in the chatbar, or click a suggestion below.</div>
        </div>
        """, unsafe_allow_html=True)

        card_c1, card_c2 = st.columns(2)
        
        # 1. STUDENT DB SUGGESTIONS
        if "Student" in source_mode or current_db_id == "student_db":
            with card_c1:
                if st.button("🎓 **Students Enrolled in 2021**\n\nList all students who enrolled in year 2021", use_container_width=True):
                    process_user_prompt("List all students enrolled in 2021.")
                if st.button("📚 **All Available Courses**\n\nList all courses offered with their course IDs", use_container_width=True):
                    process_user_prompt("List all courses with their course IDs.")
            with card_c2:
                if st.button("📊 **Average Marks per Course (Chart)**\n\nCalculate average student marks per course and plot as bar chart", use_container_width=True):
                    process_user_prompt("Show average marks for each course as a bar chart.")
                if st.button("🏆 **Top Scorers in Machine Learning**\n\nFind names of students who scored more than 90 in Machine Learning", use_container_width=True):
                    process_user_prompt("List all students who scored above 90 in Machine Learning.")

        # 2. CLOTHING DB SUGGESTIONS
        elif "Clothing" in source_mode or current_db_id == "clothing":
            with card_c1:
                if st.button("👕 **T-Shirts Stock by Brand (Chart)**\n\nShow total stock quantity per brand as a bar chart", use_container_width=True):
                    process_user_prompt("Show total stock of t-shirts by brand as a bar chart.")
                if st.button("🎨 **Available Colors**\n\nList all unique colors of t-shirts currently in stock", use_container_width=True):
                    process_user_prompt("List all available colors of t-shirts.")
            with card_c2:
                if st.button("🏷️ **Highest Brand Discount**\n\nFind which clothing brand offers the highest maximum discount", use_container_width=True):
                    process_user_prompt("Which brand offers the highest discount?")
                if st.button("💰 **Discounted Revenue Potential**\n\nCalculate total revenue if all stock is sold at discounted price", use_container_width=True):
                    process_user_prompt("What is the total revenue if all stock of each t-shirt is sold at discounted price?")

        # 3. CSV / SQLITE UPLOADED DATASET SUGGESTIONS
        elif "Upload" in source_mode or "CSV" in str(st.session_state.get("db_type")):
            table_name = st.session_state.get("current_db", "dataset")
            with card_c1:
                if st.button(f"📋 **Preview `{table_name}`**\n\nDisplay the first 5 records from this uploaded table", use_container_width=True):
                    process_user_prompt(f"Show the first 5 rows from {table_name}.")
                if st.button(f"🔢 **Total Records Count**\n\nCount the total number of rows in this dataset", use_container_width=True):
                    process_user_prompt(f"How many total records are in {table_name}?")
            with card_c2:
                if st.button(f"📊 **Column Breakdown (Chart)**\n\nShow count of records grouped by first categorical column as a bar chart", use_container_width=True):
                    process_user_prompt(f"Show the distribution of records in {table_name} as a bar chart.")
                if st.button(f"🔍 **Summary Overview**\n\nProvide descriptive summary of numeric columns", use_container_width=True):
                    process_user_prompt(f"Summarize the key columns in {table_name}.")

        # 4. REMOTE MYSQL SUGGESTIONS
        else:
            with card_c1:
                if st.button("🗄️ **List Database Tables**\n\nShow all available tables in this remote MySQL database", use_container_width=True):
                    process_user_prompt("SHOW TABLES;")
            with card_c2:
                if st.button("📊 **Inspect Table Row Counts**\n\nCount total records in the primary table", use_container_width=True):
                    process_user_prompt("Count the total records in each table.")
    
    else:
        # Render Chat Stream
        for i, message in enumerate(st.session_state.chat_history):
            if isinstance(message, AIMessage):
                with st.chat_message("assistant", avatar="⚡"):
                    sql = st.session_state.sql_history.get(i)
                    if sql:
                        with st.expander("⚡ View Generated SQL", expanded=False):
                            st.code(sql, language="sql")
                    
                    st.markdown(message.content)
                    
                    viz_data = st.session_state.visualizations.get(i)
                    if viz_data:
                        try:
                            df = pd.DataFrame(viz_data['data'])
                            if viz_data['type'] == "pie":
                                fig = px.pie(df, names=df.columns[0], values=df.columns[1], template="plotly_dark")
                            else:
                                fig = px.bar(df, x=df.columns[0], y=df.columns[1], template="plotly_dark")
                            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                            st.plotly_chart(fig, use_container_width=True, key=f"chat_viz_{i}")
                        except Exception as e:
                            st.error(f"Visualization error: {str(e)}")
                            
            elif isinstance(message, HumanMessage):
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message.content)

    # UNIFIED CHAT INPUT BAR: Text input + Microphone in ONE visual container
    prompt_col, mic_col = st.columns([11, 1])
    
    with prompt_col:
        prompt = st.chat_input("Ask a question in plain English (e.g. 'Show average marks per course as a bar chart')...")

    with mic_col:
        with st.popover("🎙️", help="Click to speak your question"):
            st.markdown("##### 🎙️ Speak your question")
            st.caption("Groq Whisper will transcribe and auto-run:")
            audio_val = st.audio_input("Record audio", label_visibility="collapsed")
            if audio_val:
                s_key = get_server_api_key()
                u_key = st.session_state.get("custom_groq_key", "").strip()
                active_key = u_key or s_key
                if active_key:
                    with st.spinner("Transcribing with Groq Whisper..."):
                        transcription = transcribe_audio(audio_val.read(), active_key)
                        if transcription:
                            st.session_state.pending_voice_prompt = transcription
                            st.rerun()

    # If voice was recorded, process immediately
    if st.session_state.pending_voice_prompt:
        voice_query = st.session_state.pending_voice_prompt
        st.session_state.pending_voice_prompt = None
        process_user_prompt(voice_query)
    elif prompt:
        process_user_prompt(prompt)

def main():
    with st.sidebar:
        render_sidebar()
    render_main()

if __name__ == "__main__":
    main()
