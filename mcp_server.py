from dotenv import load_dotenv
import os
import psycopg2
from loguru import logger
from mcp.server.fastmcp import FastMCP

load_dotenv() 

DATABASE_URL = os.getenv("DATABASE_URL")

mcp = FastMCP("Demo")

@mcp.tool()
def query_data(sql: str) -> str:
    logger.info(f"Executing SQL query: {sql}")
    try:
        # connessione tramite la stringa completa
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        with conn.cursor() as cur:
            cur.execute(sql)
            try:
                rows = cur.fetchall()
                return "\n".join(str(row) for row in rows)
            except psycopg2.ProgrammingError:
                conn.commit()
                return "Query executed successfully (no rows returned)."
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

@mcp.prompt()
def example_prompt(code: str) -> str:
    return f"Please review this code:\n\n{code}"

if __name__ == "__main__":
    print("Starting server...")
    # Initialize and run the server over stdio transport
    mcp.run(transport="stdio")
