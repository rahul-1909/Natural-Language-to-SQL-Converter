from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from k_shot_examples import get_k_shot_examples
import logging
from sqlalchemy.sql import text
import re


def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

def sanitize_query(query: str) -> str:
    """Enhanced SQL sanitization with precise extraction"""
    # Extract SQL code blocks
    code_match = re.search(r"```sql(.*?)```", query, re.DOTALL | re.IGNORECASE)
    if code_match:
        query = code_match.group(1).strip()

    # Find complete SQL statements
    sql_pattern = r"""
        (?:^|\s)(?P<sql>
        (SELECT|INSERT|UPDATE|DELETE|ALTER|CREATE|DROP|TRUNCATE|CALL|EXPLAIN)\b
        .*?
        ;)
    """.strip()
    matches = re.search(sql_pattern, query, re.DOTALL | re.IGNORECASE | re.VERBOSE)
    
    if matches:
        query = matches.group("sql").strip()
    
    # Original cleaning steps
    query = query.replace("\\_", "_").replace("\\", "")
    query = "\n".join(line.strip() for line in query.splitlines() if line.strip())
    query = re.sub(r"[ \t]+", " ", query)
    
    # Semicolon handling
    query = query.rstrip(';').strip() + ';'
    
    # Remove leading non-SQL characters
    query = re.sub(r'^[^A-Z]*', '', query, flags=re.IGNORECASE)
    
    # HTML entities replacement
    html_entities = {
        "&lt;": "<", "&gt;": ">", "&amp;": "&",
        "&quot;": '"', "&#39;": "'"
    }
    for entity, char in html_entities.items():
        query = query.replace(entity, char)

    return query

def get_sql_chain(db, k_shot_examples):
    template = """Based on the schema below, write a SQL query. Schema:
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only SQL. Do not include explanations. Examples: {examples}
    
    Question: {question}
    SQL Query:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    
    return (
        RunnablePassthrough.assign(
            schema=lambda _: db.get_table_info(),
            examples=lambda _: "\n".join([f"Q: {e['question']}\nSQL: {e['sql']}" for e in k_shot_examples])
        )
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list, database_name: str):
    k_shot_examples = get_k_shot_examples(database_name)
    sql_chain = get_sql_chain(db, k_shot_examples)
    
    # Generate SQL query
    query = sql_chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })
    
    # Sanitize the query
    sanitized_query = sanitize_query(query)
    logging.info(f"Generated Query: {query}")
    logging.info(f"Sanitized Query: {sanitized_query}")
    
    # Execute the sanitized query
    try:
        with db._engine.connect() as conn:
            result = conn.execute(text(sanitized_query))
            
            # Handle different query types
            query_type = sanitized_query.strip().upper().split()[0]
            if query_type == "SELECT":
                query_result = result.fetchall()
            else:
                conn.commit()
                query_result = {
                    "operation": query_type,
                    "rowcount": result.rowcount,
                    "status": "success"
                }
    
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return f"An error occurred while executing the query: {str(e)}", None, None
    
    # Generate natural language response
    template = """Answer based on the SQL response. Generate a natural language response suitable for the question asked.
    
    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    Response: {response}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    
    chain = (
        RunnablePassthrough.assign(
            schema=lambda _: db.get_table_info(),
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    natural_response = chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
        "query": sanitized_query,
        "response": query_result,
    })
    
    # Determine if visualization is requested
    is_visualization_requested = any(
        keyword in user_query.lower()
        for keyword in ["visualize", "chart", "pie", "bar", "graph", "plot"]
    )
    
    return natural_response, query_result, is_visualization_requested