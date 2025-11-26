import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_db_connection():

    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'client_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn

        # Perform database operations here

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")

    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Connection closed.")