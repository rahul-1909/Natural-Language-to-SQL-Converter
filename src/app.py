import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from database import init_mysql_database, init_sqlite_database, init_csv_database, get_response
import pandas as pd
import plotly.express as px
from logging_utils import setup_logging

load_dotenv()

if 'logging_initialized' not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True

# Session State Initialization
if 'visualizations' not in st.session_state:
    st.session_state.visualizations = {}
if 'chat_history_data' not in st.session_state:
    st.session_state.chat_history_data = []
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'chat'
if 'db' not in st.session_state:
    # Auto-initialize Instant Demo SQLite DB on first load
    demo_db_path = "data/demo.db"
    if os.path.exists(demo_db_path):
        st.session_state.db = init_sqlite_database(demo_db_path)
        st.session_state.current_db = "student_db"
        st.session_state.db_type = "demo"
    else:
        st.session_state.db = None
        st.session_state.current_db = None
if 'suggested_prompt' not in st.session_state:
    st.session_state.suggested_prompt = None


def manage_chat_history(action, data=None):
    history_file = "chat_history.json"
    if action == "save":
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    elif action == "load":
        if not os.path.exists(history_file):
            return []
        with open(history_file, 'r') as f:
            return json.load(f)
    return None


def process_user_prompt(prompt):
    if not st.session_state.db:
        st.warning(
            "⚠️ Please connect to a database or select Instant Demo in the sidebar!")
        return

    groq_key = st.session_state.get(
        "groq_api_key") or os.getenv("GROQ_API_KEY")
    if not groq_key:
        st.error(
            "⚠️ Please enter your Groq API Key in the sidebar (Free from console.groq.com).")
        return

    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema, generating SQL, and querying database..."):
            response, query_result, is_visualization_requested = get_response(
                prompt,
                st.session_state.db,
                st.session_state.chat_history,
                st.session_state.current_db or "student_db",
                model_name=st.session_state.get(
                    "selected_model", "openai/gpt-oss-20b"),
                api_key=groq_key
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
            manage_chat_history("save", st.session_state.chat_history_data)

    st.session_state.chat_history.append(AIMessage(content=response))


def handle_sidebar_content():
    st.title("🤖 SQL Assistant")

    st.subheader("🔑 AI Configuration")
    api_key_input = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Get a free key from console.groq.com"
    )
    st.session_state.groq_api_key = api_key_input

    model_options = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b"
    ]
    st.session_state.selected_model = st.selectbox(
        "Model", model_options, index=0)

    st.markdown("---")
    st.subheader("🗄️ Database Connection")
    conn_mode = st.radio(
        "Choose Data Source:",
        ["🌟 Instant Demo (Zero Setup)",
         "📁 Upload CSV / SQLite", "🔌 Remote MySQL"],
        index=0
    )

    if conn_mode == "🌟 Instant Demo (Zero Setup)":
        st.info(
            "Pre-loaded with `students`, `courses`, `marks`, `t_shirts`, and `discounts` tables.")
        sub_db = st.selectbox("Demo Domain:", ["student_db", "clothing"])
        if st.button("Load Demo Database", use_container_width=True):
            st.session_state.db = init_sqlite_database("data/demo.db")
            st.session_state.current_db = sub_db
            st.success(f"Connected to Demo ({sub_db})!")

    elif conn_mode == "📁 Upload CSV / SQLite":
        uploaded_file = st.file_uploader(
            "Upload CSV or SQLite (.db) file", type=["csv", "db", "sqlite"])
        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(3), use_container_width=True)
                table_name = uploaded_file.name.rsplit(".", 1)[0]
                if st.button(f"Connect to `{table_name}`", use_container_width=True):
                    st.session_state.db = init_csv_database(df, table_name)
                    st.session_state.current_db = table_name
                    st.success(f"Connected to uploaded `{table_name}` table!")
            else:
                with open(f"data/{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.db = init_sqlite_database(
                    f"data/{uploaded_file.name}")
                st.session_state.current_db = uploaded_file.name
                st.success(f"Connected to `{uploaded_file.name}`!")

    elif conn_mode == "🔌 Remote MySQL":
        host = st.text_input("Host", value="localhost")
        port = st.text_input("Port", value="3306")
        user = st.text_input("User", value="root")
        password = st.text_input("Password", type="password", value="root")
        database = st.selectbox("Database", ["student_db", "clothing"])

        if st.button("Connect to MySQL", use_container_width=True):
            with st.spinner("Connecting..."):
                try:
                    db = init_mysql_database(
                        user, password, host, port, database)
                    st.session_state.db = db
                    st.session_state.current_db = database
                    st.success(f"Connected to `{database}` on MySQL!")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")

    st.markdown("---")
    if st.session_state.view_mode == 'chat':
        if st.button("📜 View History", use_container_width=True):
            st.session_state.view_mode = 'history'
            st.rerun()
    else:
        if st.button("💬 Back to Chat", use_container_width=True):
            st.session_state.view_mode = 'chat'
            st.rerun()


def show_chat_interface():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(
                content="Hello! I'm your AI SQL assistant. Ask me anything about the connected database or click a suggestion below!"),
        ]
        st.session_state.chat_history_data = manage_chat_history("load")

    # Display Chat Messages
    for i, message in enumerate(st.session_state.chat_history):
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
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

    # Clickable Prompt Suggestions
    st.markdown("##### 💡 Suggested Questions:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎓 Students enrolled in 2021", use_container_width=True):
            process_user_prompt("List all students enrolled in 2021.")
    with col2:
        if st.button("📊 Average marks per course (Bar Chart)", use_container_width=True):
            process_user_prompt(
                "Show average marks for each course as a bar chart.")
    with col3:
        if st.button("👕 T-shirts stock by brand (Bar Chart)", use_container_width=True):
            process_user_prompt(
                "Show total stock of t-shirts by brand as a bar chart.")

    prompt = st.chat_input(
        "Ask a question (e.g. 'Which student scored the highest marks in Machine Learning?')...")
    if prompt:
        process_user_prompt(prompt)


def show_history_interface():
    st.subheader("📜 Query History")
    history = st.session_state.chat_history_data
    if not history:
        st.info("No past queries recorded.")
        return
    for item in reversed(history):
        with st.expander(f"[{item.get('timestamp', '')[:19]}] {item.get('query', '')} ({item.get('database', '')})"):
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
    st.set_page_config(page_title="AI SQL Assistant",
                       page_icon="🤖", layout="wide")
    with st.sidebar:
        handle_sidebar_content()

    if st.session_state.view_mode == 'chat':
        show_chat_interface()
    else:
        show_history_interface()


if __name__ == "__main__":
    main()
