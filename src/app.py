import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from database import init_database, get_response
import pandas as pd
import plotly.express as px
from logging_utils import setup_logging

if 'logging_initialized' not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True
load_dotenv()

# Session State Initialization
if 'visualizations' not in st.session_state:
    st.session_state.visualizations = {}
if 'chat_history_data' not in st.session_state:
    st.session_state.chat_history_data = []
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'chat'

# Chat History Management
def manage_chat_history(action, data=None):
    """Manage shared chat history using JSON file"""
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
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response, query_result, is_visualization_requested = get_response(
            prompt, 
            st.session_state.db, 
            st.session_state.chat_history,
            st.session_state.current_db
        )
        st.markdown(response)

        viz_data = None
        if is_visualization_requested and query_result:
            try:
                df = pd.DataFrame(query_result)
                if "pie" in prompt.lower():
                    fig = px.pie(df, names=df.columns[0], values=df.columns[1])
                    chart_type = "pie"
                else:
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                    chart_type = "bar"
                
                st.plotly_chart(fig, use_container_width=True, key=f"viz_{datetime.now().timestamp()}")
                
                # Store visualization data
                viz_data = {
                    "type": chart_type,
                    "columns": df.columns.tolist(),
                    "data": df.to_dict('list')
                }
            except Exception as e:
                st.error(f"Visualization error: {str(e)}")

        msg_index = len(st.session_state.chat_history)
        st.session_state.visualizations[msg_index] = viz_data
        
        # Save to shared history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'database': st.session_state.current_db,
            'query': prompt,
            'response': response,
            'visualization': viz_data
        }
        st.session_state.chat_history_data.append(history_entry)
        
    st.session_state.chat_history.append(AIMessage(content=response))


def handle_sidebar_content():
    st.title("Database Chat Assistant")
    
    if st.session_state.view_mode == 'chat':
        if st.button("📜 View History"):
            st.session_state.view_mode = 'history'
            st.rerun()

    st.subheader("Database Settings")
    host = st.text_input("Host", value="localhost")
    port = st.text_input("Port", value="3306")
    user = st.text_input("User", value="root")
    password = st.text_input("Password", type="password", value="root")
    database = st.selectbox("Database", ["student_db", "clothing"])
    
    if st.button("Connect"):
        with st.spinner("Connecting..."):
            try:
                db = init_database(user, password, host, port, database)
                st.session_state.db = db
                st.session_state.current_db = database
                st.success(f"Connected to {database}!")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")


def show_chat_interface():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello! I'm your SQL assistant. Ask me anything about the database."),
        ]
        # Load saved history on first run
        st.session_state.chat_history_data = manage_chat_history("load")

    for i, message in enumerate(st.session_state.chat_history):
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
                viz_data = st.session_state.visualizations.get(i)
                if viz_data:
                    try:
                        df = pd.DataFrame(viz_data['data'])
                        if viz_data['type'] == "pie":
                            fig = px.pie(df, names=df.columns[0], values=df.columns[1])
                        else:
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                        # Add unique key using index
                        st.plotly_chart(fig, use_container_width=True, key=f"chat_viz_{i}")
                    except Exception as e:
                        st.error(f"Visualization error: {str(e)}")
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    with st.sidebar:
        handle_sidebar_content()

    if prompt := st.chat_input("Type your question..."):
        process_user_prompt(prompt)
        # Save history after each interaction
        manage_chat_history("save", st.session_state.chat_history_data)
        st.rerun()


def show_history_view():
    st.markdown("""
        <div style='text-align: center; font-weight: bold; font-size: 36px; color: white; margin-bottom: 30px;'>
            CHAT HISTORY
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("← Back to Chat"):
            st.session_state.view_mode = 'chat'
            st.rerun()
    
    if not st.session_state.chat_history_data:
        st.info("No chat history available")
    else:
        for idx, entry in enumerate(reversed(st.session_state.chat_history_data)):
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.caption(datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M'))
                with col2:
                    st.markdown(f"**Database:** `{entry.get('database', 'Unknown')}`")
                    st.markdown(f"**Query:** {entry['query']}")
                    st.markdown(f"**Response:** {entry['response']}")
                    
                    viz_data = entry.get('visualization')
                    if viz_data:
                        try:
                            df = pd.DataFrame(viz_data['data'])
                            if viz_data['type'] == "pie":
                                fig = px.pie(df, names=df.columns[0], values=df.columns[1])
                            else:
                                fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                            # Add unique key using timestamp and index
                            st.plotly_chart(fig, use_container_width=True, 
                                         key=f"hist_viz_{entry['timestamp']}_{idx}")
                        except Exception as e:
                            st.error(f"Could not recreate visualization: {str(e)}")
                st.divider()

    with st.sidebar:
        handle_sidebar_content()

# Chat Page
def chat_page():
    st.markdown("""
        <div style='text-align: center; font-weight: bold; font-size: 56px; color: white; margin-bottom: 30px;'>
            DATABASE CHAT ASSISTANT
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.view_mode == 'history':
        show_history_view()
    else:
        show_chat_interface()

# Main App Flow
def main():
    st.set_page_config(
        page_title="Database Query Bot",
        page_icon="�",
        layout="centered"
    )
    
    chat_page()

if __name__ == "__main__":
    main()