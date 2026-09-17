import os
import re
import sqlite3
import logging
import pandas as pd
from sqlalchemy.sql import text
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from k_shot_examples import get_k_shot_examples

DEFAULT_MODEL = "openai/gpt-oss-20b"


def init_mysql_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)


def init_sqlite_database(db_path: str = "data/demo.db") -> SQLDatabase:
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    abs_path = os.path.abspath(db_path).replace(os.sep, "/")
    return SQLDatabase.from_uri(f"sqlite:///{abs_path}")


def init_csv_database(df: pd.DataFrame, table_name: str = "uploaded_data") -> SQLDatabase:
    clean_name = re.sub(r'\W+', '_', table_name).strip('_') or "uploaded_data"
    os.makedirs("data", exist_ok=True)
    db_path = os.path.abspath(f"data/{clean_name}.db").replace(os.sep, "/")
    conn = sqlite3.connect(db_path)
    df.to_sql(clean_name, conn, if_exists="replace", index=False)
    conn.close()
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def sanitize_query(query: str) -> str:
    """Enhanced SQL sanitization with precise extraction"""
    code_match = re.search(r"```(?:sql)?(.*?)```", query,
                           re.DOTALL | re.IGNORECASE)
    if code_match:
        query = code_match.group(1).strip()

    sql_pattern = r"""
        (?:^|\s)(?P<sql>
        (SELECT|INSERT|UPDATE|DELETE|ALTER|CREATE|DROP|TRUNCATE|CALL|EXPLAIN|SHOW|PRAGMA)\b
        .*?
        (?:;|$))
    """.strip()
    matches = re.search(sql_pattern, query, re.DOTALL |
                        re.IGNORECASE | re.VERBOSE)
    if matches:
        query = matches.group("sql").strip()

    query = query.replace("\\_", "_").replace("\\", "")
    query = "\n".join(line.strip()
                      for line in query.splitlines() if line.strip())
    query = re.sub(r"[ \t]+", " ", query)
    query = query.rstrip(';').strip() + ';'
    query = re.sub(r'^[^A-Z]*', '', query, flags=re.IGNORECASE)

    html_entities = {
        "&lt;": "<", "&gt;": ">", "&amp;": "&",
        "&quot;": '"', "&#39;": "'"
    }
    for entity, char in html_entities.items():
        query = query.replace(entity, char)

    return query


def get_llm(model_name: str = None, api_key: str = None) -> ChatGroq:
    model = model_name or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    key = api_key or os.getenv("GROQ_API_KEY")
    return ChatGroq(model=model, temperature=0, api_key=key)


def get_sql_chain(db: SQLDatabase, k_shot_examples: list, model_name: str = None, api_key: str = None):
    dialect = getattr(db, "dialect", "sql").upper()
    template = f"""You are a {dialect} expert. Given the database schema and conversation history below, write a syntactically correct {dialect} query to answer the user's question.
Schema:
<SCHEMA>
{{schema}}
</SCHEMA>

Conversation History:
{{chat_history}}

Few-shot Examples:
{{examples}}

Instructions:
- Write ONLY a single executable {dialect} query terminated with a semicolon (;).
- Do NOT wrap it in markdown code fences or backticks.
- Do NOT include explanations, greetings, or conversational remarks.

Question: {{question}}
SQL Query:"""

    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm(model_name, api_key)

    examples_formatted = "\n".join([f"Q: {e['question']}\nSQL: {e['sql']}" for e in k_shot_examples]
                                   ) if k_shot_examples else "None provided. Use the schema."

    return (
        RunnablePassthrough.assign(
            schema=lambda _: db.get_table_info(),
            examples=lambda _: examples_formatted
        )
        | prompt
        | llm
        | StrOutputParser()
    )


def get_response(user_query: str, db: SQLDatabase, chat_history: list, database_name: str, model_name: str = None, api_key: str = None):
    try:
        k_shot_examples = get_k_shot_examples(database_name)
        sql_chain = get_sql_chain(db, k_shot_examples, model_name, api_key)

        # 1. Generate SQL query
        raw_query = sql_chain.invoke({
            "question": user_query,
            "chat_history": chat_history,
        })

        # 2. Sanitize query
        sanitized_query = sanitize_query(raw_query)
        logging.info(f"Generated Query: {raw_query}")
        logging.info(f"Sanitized Query: {sanitized_query}")

        # 3. Execute query
        with db._engine.connect() as conn:
            result = conn.execute(text(sanitized_query))
            query_type = sanitized_query.strip().upper().split()[0]

            if query_type in ("SELECT", "SHOW", "EXPLAIN", "PRAGMA"):
                keys = result.keys()
                query_result = [dict(zip(keys, row))
                                for row in result.fetchall()]
            else:
                conn.commit()
                query_result = {
                    "operation": query_type,
                    "rowcount": result.rowcount,
                    "status": "success"
                }

        # 4. Generate Natural Language Response
        template = """Answer the user's question based on the executed SQL query and its results.
Conversation History: {chat_history}
Question: {question}
Executed SQL: {query}
Database Result: {response}

Provide a clear, helpful, conversational explanation of the result."""

        prompt = ChatPromptTemplate.from_template(template)
        llm = get_llm(model_name, api_key)
        chain = prompt | llm | StrOutputParser()

        natural_response = chain.invoke({
            "question": user_query,
            "chat_history": chat_history,
            "query": sanitized_query,
            "response": str(query_result),
        })

        is_visualization_requested = any(
            keyword in user_query.lower()
            for keyword in ["visualize", "chart", "pie", "bar", "graph", "plot"]
        )

        return natural_response, query_result, is_visualization_requested

    except Exception as e:
        logging.error(f"Error in get_response: {e}")
        return f"⚠️ Error: {str(e)}", None, False
