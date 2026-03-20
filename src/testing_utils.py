# testing_utils.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_database
from test_examples import test_cases
import time
from test_database import test_get_response, TestDatabaseWrapper

def testing_interface():
    """Main testing interface with separate page layout"""
    st.set_page_config(page_title="SQL Model Testing", layout="wide")
    
    # Initialize session state variables
    if 'test_results' not in st.session_state:
        st.session_state.test_results = None
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = None
    
    # Sidebar for database connection
    with st.sidebar:
        st.title("Database Configuration")
        db_host = st.text_input("Host", value="localhost")
        db_port = st.text_input("Port", value="3306")
        db_user = st.text_input("Username", value="root")
        db_pass = st.text_input("Password", type="password", value="root")
        db_name = st.selectbox("Database", ["student_db", "employees", "clothing"])
        
        if st.button("🔗 Connect to Database"):
            with st.spinner("Connecting..."):
                try:
                    st.session_state.db_conn = init_database(
                        db_user, db_pass, db_host, db_port, db_name
                    )
                    st.success("Connected successfully!")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
    
    # Main testing interface
    st.title("SQL Model Evaluation Suite")
    
    if st.session_state.db_conn:
        if st.button("🏃♂️ Run Full Test Suite", use_container_width=True):
            with st.spinner("Executing test cases..."):
                st.session_state.test_results = run_automated_tests(
                    st.session_state.db_conn
                )
                st.rerun()
                
    if st.session_state.test_results:
        show_test_results(st.session_state.test_results)

def run_automated_tests(db_connection):
    """Execute all test cases and return results"""
    results = {
        'total': 0,
        'correct': 0,
        'incorrect': 0,
        'details': [],
        'execution_time': time.time()
    }
    
    for db_name, cases in test_cases.items():
        for case in cases:
            test_result = process_test_case(db_connection, db_name, case)
            results['details'].append(test_result)
            results['total'] += 1
            
            if test_result['status'] == 'incorrect':
                results['incorrect'] += 1
            else:
                results['correct'] += 1
                
    results['execution_time'] = round(time.time() - results['execution_time'], 2)
    return results

def process_test_case(db_connection, db_name, test_case):
    result = {
        'database': db_name,
        'question': test_case['question'],
        'expected_sql': test_case['sql'],
        'generated_sql': '',
        'status': 'correct',  # Default to correct
        'error': None
    }
    
    # Define critical error patterns that should be treated as incorrect
    CRITICAL_ERRORS = [
        "sql_mode=only_full_group_by",
        "HAVING clause is not in GROUP BY",
        "nonaggregated column",
        "functionally dependent on columns in GROUP BY",
        "incompatible with sql_mode"
    ]
    
    try:
        # Generate and execute SQL
        generated_sql, _, error = test_get_response(db_connection, test_case['question'], db_name)
        result['generated_sql'] = generated_sql

        # Check for any generation errors
        if error:
            raise Exception(error)
            
        # Execute the generated query
        with TestDatabaseWrapper(db_connection) as wrapper:
            wrapper.execute_test_query(generated_sql)
            
    except Exception as e:
        error_str = str(e)
        # Check if it's a critical error
        if any(pattern in error_str for pattern in CRITICAL_ERRORS):
            result.update({
                'status': 'incorrect',
                'error': error_str
            })
        
    return result

def show_test_results(results):
    """Display test results with visualizations"""
    # Summary Metrics
    st.subheader(f"Test Results ({results['execution_time']}s)")
    
    cols = st.columns(3)
    cols[0].metric("Total Cases", results['total'])
    cols[1].metric("Correct", results['correct'])
    cols[2].metric("Incorrect", results['incorrect'])
    
    # Visualization
    plot_data = pd.DataFrame({
        'Category': ['Correct', 'Incorrect'],
        'Count': [results['correct'], results['incorrect']]
    })
    
    fig = px.bar(plot_data, x='Category', y='Count', color='Category',
                color_discrete_map={
                    'Correct': '#2ecc71',
                    'Incorrect': '#e74c3c'
                },
                title="Test Results Summary")
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Results
    with st.expander("📋 Detailed Test Results"):
        for idx, test in enumerate(results['details']):
            status_color = '🟢' if test['status'] == 'correct' else '🔴'
            
            st.markdown(f"### {status_color} Test {idx+1}: {test['question']}")
            st.caption(f"Database: {test['database']}")
            
            cols = st.columns(2)
            with cols[0]:
                st.code(f"Expected SQL:\n{test['expected_sql']}", language='sql')
            with cols[1]:
                st.code(f"Generated SQL:\n{test['generated_sql']}", language='sql')
            
            if test['status'] == 'incorrect':
                st.error(f"**Error:** {test['error']}")
            else:
                st.success("Query executed successfully")
            
            st.divider()

if __name__ == "__main__":
    testing_interface()