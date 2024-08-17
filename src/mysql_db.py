import mysql.connector
from mysql.connector import Error

class MySQLDB:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self, host: str, database: str, user: str, password: str):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.connection.cursor()
        except Error as e:
            raise e

    def execute(self, query: str):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            raise e

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
        return False
    
class AccountAggregator:
    def __init__(self, db: MySQLDB):
        if not db.connection is None:
            raise ValueError("Database connection is required.")
        
        self.db = db
    
    def get_accounts(self):
        ök b