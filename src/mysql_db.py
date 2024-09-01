import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
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

    def execute(self, query: str, params: tuple = None):
        try:
            self.cursor.execute(query, params)
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
    
class TransactionAggregator:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.db = MySQLDB()
        self.db.connect(host, database, user, password)
    
    def get_transactions(self, account_id, limit = 10):
        query = """SELECT Id, Amount, Description, TransactionType FROM transactions WHERE AccountId = %s LIMIT %s"""
        return self.db.execute(query, (account_id, limit))

    def get_receipts(self, transaction_id, limit = 10):
        query = """SELECT Id FROM receipts WHERE TransactionId = %s LIMIT %s"""
        return self.db.execute(query, (transaction_id, limit))
    
    def get_receipt_items(self, receipt_id, limit = 10):
        query = """SELECT ItemName, ItemDescription, Quantity, Unit, UnitPrice, TotalPrice, Category, GeneralCategory FROM receiptitems WHERE ReceiptId = %s LIMIT %s"""
        return self.db.execute(query, (receipt_id, limit))
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        return False

class Transaction(BaseModel):
    id: str
    amount: float
    description: str
    transaction_type: str
    
class ReceiptItem(BaseModel):
    item_name: str
    item_description: str
    quantity: int
    unit: str
    unit_price: float
    total_price: float
    category: str
    general_category: str

class Receipt(BaseModel):
    id: str
    transaction_id: str
    receipt_items: list[ReceiptItem]

with TransactionAggregator("localhost", 'dev', 'shogunskinoski', 'nevarlanteneke123.') as ta:
    transactions = ta.get_transactions("7c73b4b1-0551-48ad-b176-879f69c167b4", 10)
    for transaction in transactions:
        transaction_id = transaction[0]
        receipt_ids = ta.get_receipts(transaction_id)
        for receipt_id in receipt_ids:
            receipt_items = ta.get_receipt_items(receipt_id[0])
            receipt_items_objects = [
                ReceiptItem(
                    item_name=item[0],
                    item_description=item[1],
                    quantity=item[2],
                    unit=item[3],
                    unit_price=item[4],
                    total_price=item[5],
                    category=item[6],
                    general_category=item[7]
                ) for item in receipt_items
            ]
            receipt = Receipt(
                id=receipt_id[0],
                transaction_id=transaction_id,
                receipt_items=receipt_items_objects
            )
            print(receipt)