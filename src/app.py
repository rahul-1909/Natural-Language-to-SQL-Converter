import streamlit as st
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from database import init_mysql_database, init_sqlite_database, init_csv_database, get_response
import pandas as pd
import plotly.express as px
from logging_utils import setup_logging

load_dotenv()

# Page Configuration & Custom CSS
st.set_page_config(
    page_title="QueryAI • Natural Language SQL Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional UI Styling
st.markdown("""
<style>
    /* Metric / Pill badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        background: rgba(33, 150, 243, 0.15);
        color: #64b5f6;
        border: 1px solid rgba(33, 150, 243, 0.3);
        margin-bottom: 12px;
    }
    .status-badge.connected {
        background: rgba(76, 175, 80, 0.15);
        color: #81c784;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    /* Suggestion cards */
    div.stButton > button.suggest-btn {
        width: 100%;
        text-align: left;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 10px 14px;
        font-size: 0.88rem;
        transition: all 0.2s ease;
    }
    /* Clear button style */
    div.stButton > button.new-chat-btn {
        border-radius: 8px;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

if 'logging_initialized' not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True

# Helper to safely retrieve server secret


def get_server_api_key():
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    return os.getenv("GROQ_API_KEY", "")


# Session State Initialization
if 'visualizations' not in st.session_state:
    st.session_state.visualizations = {}
if 'chat_history_data' not in st.session_state:
    st.session_state.chat_history_data = []
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'chat'
if 'db' not in st.session_state:
    demo_db_path = "data/demo.db"
    if os.path.exists(demo_db_path):
        st.session_state.db = init_sqlite_database(demo_db_path)
        st.session_state.current_db = "student_db"
        st.session_state.db_type = "🌟 Instant Demo"
    else:
        st.session_state.db = None
        st.session_state.current_db = None
        st.session_state.db_type = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="👋 **Hello! I'm your AI SQL Analyst.** Ask any question in plain English, or click one of the quick suggestions below to query the database and generate charts.")
    ]


def reset_chat():
    st.session_state.chat_history = [
        AIMessage(
            content="👋 **New conversation started.** Connect a database or choose a sample question below!")
    ]
    st.session_state.visualizations = {}
    st.rerun()


def process_user_prompt(prompt):
    # Intercept accidental "clear" or "reset" queries
    if prompt.strip().lower() in ["clear", "reset", "new chat", "cls"]:
        reset_chat()
        return

    server_key = get_server_api_key()
    user_key = st.session_state.get("custom_groq_key", "").strip()
    active_key = user_key or server_key

    if not active_key:
        st.error("⚠️ No Groq API Key found. Please add a key in the sidebar.")
        return

    if not st.session_state.db:
        st.warning("⚠️ Please connect to a database in the sidebar first!")
        return

    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema, generating SQL, and querying database..."):
            model_to_use = st.session_state.get(
                "selected_model", "openai/gpt-oss-20b")
            response, query_result, is_visualization_requested = get_response(
                prompt,
                st.session_state.db,
                st.session_state.chat_history,
                st.session_state.current_db or "student_db",
                model_name=model_to_use,
                api_key=active_key
            )
            st.markdown(response)

            viz_data = None
            if is_visualization_requested and query_result and isinstance(query_result, list) and len(query_result) > 0:
                try:
                    df = pd.DataFrame(query_result)
                    if len(df.columns) >= 2:
                        if "pie" in prompt.lower():
                            fig = px.pie(
                                df, names=df.columns[0], values=df.columns[1], title="Data Breakdown")
                            chart_type = "pie"
                        else:
                            fig = px.bar(
                                df, x=df.columns[0], y=df.columns[1], title="Data Comparison")
                            chart_type = "bar"

                        st.plotly_chart(fig, use_container_width=True,
                                        key=f"viz_{datetime.now().timestamp()}")
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

            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'database': st.session_state.current_db,
                'query': prompt,
                'response': response,
                'visualization': viz_data
            }
            st.session_state.chat_history_data.append(history_entry)

    st.session_state.chat_history.append(AIMessage(content=response))


def handle_sidebar():
    st.markdown("### ⚡ **QueryAI Studio**")

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    st.markdown("---")
    st.subheader("🔐 AI Credentials")

    server_key = get_server_api_key()
    if server_key:
        st.success("🟢 Server API Key Active (Secure)")
        with st.expander("Use Custom API Key (Optional)"):
            custom_key = st.text_input(
                "Groq API Key", type="password", placeholder="gsk_...", key="custom_groq_key")
    else:
        custom_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...",
                                   key="custom_groq_key", help="Free key from console.groq.com")

    model_options = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b"
    ]
    st.session_state.selected_model = st.selectbox(
        "LLM Model", model_options, index=0)

    st.markdown("---")
    st.subheader("🗄️ Data Connection")
    conn_mode = st.radio(
        "Source:",
        ["🌟 Instant Demo", "📁 Upload CSV / SQLite", "🔌 Remote MySQL"],
        index=0
    )

    if conn_mode == "🌟 Instant Demo":
        st.caption(
            "Pre-loaded SQLite database with students, courses, marks, t_shirts, discounts.")
        sub_db = st.selectbox("Sample Domain:", ["student_db", "clothing"])
        if st.button("Connect Demo", use_container_width=True):
            st.session_state.db = init_sqlite_database("data/demo.db")
            st.session_state.current_db = sub_db
            st.session_state.db_type = "🌟 Instant Demo"
            st.success(f"Connected to Demo ({sub_db})!")
            st.rerun()

    elif conn_mode == "📁 Upload CSV / SQLite":
        uploaded_file = st.file_uploader(
            "Upload CSV or SQLite (.db)", type=["csv", "db", "sqlite"])
        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(3), use_container_width=True)
                table_name = uploaded_file.name.rsplit(".", 1)[0]
                if st.button(f"Load `{table_name}`", use_container_width=True):
                    st.session_state.db = init_csv_database(df, table_name)
                    st.session_state.current_db = table_name
                    st.session_state.db_type = f"CSV: {table_name}"
                    st.success(f"Loaded `{table_name}` table!")
                    st.rerun()
            else:
                with open(f"data/{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.db = init_sqlite_database(
                    f"data/{uploaded_file.name}")
                st.session_state.current_db = uploaded_file.name
                st.session_state.db_type = f"SQLite: {uploaded_file.name}"
                st.success(f"Connected to `{uploaded_file.name}`!")
                st.rerun()

    elif conn_mode == "🔌 Remote MySQL":
        host = st.text_input("Host", value="localhost")
        port = st.text_input("Port", value="3306")
        user = st.text_input("User", value="root")
        password = st.text_input("Password", type="password", value="root")
        database = st.selectbox("Database", ["student_db", "clothing"])

        if st.button("Connect MySQL", use_container_width=True):
            try:
                db = init_mysql_database(user, password, host, port, database)
                st.session_state.db = db
                st.session_state.current_db = database
                st.session_state.db_type = f"MySQL: {database}"
                st.success(f"Connected to `{database}`!")
                st.rerun()
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

    st.markdown("---")
    # Schema Viewer in sidebar
    if st.session_state.db:
        with st.expander("🔍 Inspect Schema"):
            st.caption(f"**Engine:** `{st.session_state.db.dialect}`")
            tables = st.session_state.db.get_usable_table_names()
            st.write("**Tables:**", tables)

    # History toggle
    if st.session_state.view_mode == 'chat':
        if st.button("📜 View Query History", use_container_width=True):
            st.session_state.view_mode = 'history'
            st.rerun()
    else:
        if st.button("💬 Back to Chat", use_container_width=True):
            st.session_state.view_mode = 'chat'
            st.rerun()


def show_chat():
    # Top Header
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        status_text = st.session_state.get(
            "db_type") or "No database connected"
        st.markdown(
            f'<div class="status-badge connected">● {status_text}</div>', unsafe_allow_html=True)
    with header_col2:
        if st.button("➕ New Chat", key="top_new_chat"):
            reset_chat()

    # Chat Messages
    for i, message in enumerate(st.session_state.chat_history):
        if isinstance(message, AIMessage):
            with st.chat_message("assistant", avatar="⚡"):
                st.markdown(message.content)
                viz_data = st.session_state.visualizations.get(i)
                if viz_data:
                    try:
                        df = pd.DataFrame(viz_data['data'])
                        if viz_data['type'] == "pie":
                            fig = px.pie(
                                df, names=df.columns[0], values=df.columns[1])
                        else:
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                        st.plotly_chart(
                            fig, use_container_width=True, key=f"chat_viz_{i}")
                    except Exception as e:
                        st.error(f"Visualization error: {str(e)}")
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    # Prompt Suggestion Chips
    st.markdown("##### 💡 Suggested Prompts:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎓 Students enrolled in 2021", use_container_width=True):
            process_user_prompt("List all students enrolled in 2021.")
    with col2:
        if st.button("📊 Average marks per course (Chart)", use_container_width=True):
            process_user_prompt(
                "Show average marks for each course as a bar chart.")
    with col3:
        if st.button("👕 T-shirts stock by brand (Chart)", use_container_width=True):
            process_user_prompt(
                "Show total stock of t-shirts by brand as a bar chart.")

    prompt = st.chat_input(
        "Ask a question in plain English (e.g. 'Which student has the highest average marks?')...")
    if prompt:
        process_user_prompt(prompt)


def show_history():
    st.subheader("📜 Query History")
    if st.button("💬 Back to Chat"):
        st.session_state.view_mode = 'chat'
        st.rerun()

    history = st.session_state.chat_history_data
    if not history:
        st.info("No past queries recorded in this session.")
        return
    for item in reversed(history):
        with st.expander(f"[{item.get('timestamp', '')[:19]}] {item.get('query', '')}"):
            st.markdown(f"**Database:** `{item.get('database', '')}`")
            st.markdown(f"**Answer:** {item.get('response', '')}")
            if item.get('visualization'):
                df = pd.DataFrame(item['visualization']['data'])
                if item['visualization']['type'] == "pie":
                    st.plotly_chart(
                        px.pie(df, names=df.columns[0], values=df.columns[1]), use_container_width=True)
                else:
                    st.plotly_chart(
                        px.bar(df, x=df.columns[0], y=df.columns[1]), use_container_width=True)


def main():
    with st.sidebar:
        handle_sidebar()

    if st.session_state.view_mode == 'chat':
        show_chat()
    else:
        show_history()


if __name__ == "__main__":
    main()
