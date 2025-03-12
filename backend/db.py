
# import psycopg2

# def get_connection():
#     return psycopg2.connect(
#         dbname="mydatabase",
#         user="postgres",
#         password="password",
#         host="localhost",  # Example: 'localhost' or an IP address
#         port="5432"    # Default PostgreSQL port is 5432
#     )

import psycopg2
import os

class Database:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        DATABASE_URL = os.getenv("DATABASE_URL")  # Ensure this is set in Render
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in environment variables")

        self.conn = psycopg2.connect(DATABASE_URL, sslmode="require")  # Enforce SSL
        return self.conn

    def release_connection(self, conn):
        if conn:
            conn.close()

fetch_data_from_db = Database()

