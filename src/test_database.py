from langchain_community.utilities import SQLDatabase
from sqlalchemy.sql import text
import re
import logging

class TestDatabaseWrapper:
    def __init__(self, db: SQLDatabase):
        self.db = db
        self.connection = self.db._engine.connect()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def execute_test_query(self, sql: str):
        """Execute query and return results with proper connection management"""
        try:
            result = self.connection.execute(text(sql))
            
            # Handle different query types
            query_type = sql.strip().upper().split()[0]
            if query_type == "SELECT":
                return result.fetchall()
            else:
                self.connection.commit()
                return {
                    "rowcount": result.rowcount,
                    "status": "success"
                }
        except Exception as e:
            logging.error(f"Query execution failed: {str(e)}")
            raise e

def test_get_response(db: SQLDatabase, user_query: str, database_name: str):
    """Modified version of get_response for testing purposes"""
    from database import get_sql_chain, get_k_shot_examples, sanitize_query
    
    k_shot_examples = get_k_shot_examples(database_name)
    sql_chain = get_sql_chain(db, k_shot_examples)
    
    # Generate SQL query
    raw_query = sql_chain.invoke({
        "question": user_query,
        "chat_history": []
    })
    
    # Sanitize the query
    sanitized_query = sanitize_query(raw_query)
    logging.info(f"Test Generated SQL: {sanitized_query}")
    
    # Execute with persistent connection
    with TestDatabaseWrapper(db) as wrapper:
        try:
            result = wrapper.execute_test_query(sanitized_query)
            return sanitized_query, result, None
        except Exception as e:
            return sanitized_query, None, str(e)

def test_extract_sql(response: str) -> str:
    """Enhanced SQL extraction for testing"""
    # First try code block extraction
    code_match = re.search(r"```sql\n(.*?)\n```", response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    
    # Then look for complete SQL statements
    sql_pattern = r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|CALL|EXPLAIN)\b.*?;"
    matches = re.findall(sql_pattern, response, re.DOTALL | re.IGNORECASE)
    return matches[-1].strip() if matches else ""