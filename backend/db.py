
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

class Database:
    def __init__(self):
        self.conn = None

    def get_connection(self, db_name):
        self.conn = psycopg2.connect(
            dbname=db_name,
            user="postgres",  # Replace with your PostgreSQL username
            password="password",  # Remove if using passwordless authentication
            host="localhost",
            port="5432"
        )
        return self.conn

    def release_connection(self, conn):  # ✅ FIX: Only one argument needed
        if conn:
            conn.close()

# Create an instance of Database
fetch_data_from_db = Database()
