from typing import AsyncGenerator
from src.document_loader import DocumentLoader
from src.qa_chain import QAChain
from src.vector_store import VectorStore
import mysql.connector
from mysql.connector import Error
class RAGSystem:
    def __init__(self, folder_path, persist_directory="vector_store_db"):
        self.folder_path = folder_path
        self.persist_directory = persist_directory
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore(persist_directory)
        self.qa_chain = None
        self._initialize()

    def _initialize(self):
        if self.vector_store.is_empty():
            self._load_and_store_documents()
        self._setup_qa_chain()

    def _load_and_store_documents(self):
        docs = []
        for chunked_docs in self.document_loader.load(self.folder_path):
            docs.extend(chunked_docs)
        self.vector_store.create_vector_store(docs)
    
    def update_documents(self, folder_path: str = ""):
        if folder_path:
            self.folder_path = folder_path
        self._load_and_store_documents()
        self._setup_qa_chain()
    
    def update_user_documents(self):
        mysql_connection = mysql.connector.connect(
            host='localhost',
            database='dev',
            user = 'shogunskinoski',
            password = 'nevarlanteneke123.'
        )
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute("SELECT * FROM addresses")
        records = mysql_cursor.fetchall()
        for record in records:
            print(record)

    def clear_documents(self):
        self.vector_store.delete()
        self.qa_chain = None

    def _setup_qa_chain(self):
        self.qa_chain = QAChain(self.vector_store.get_retriever())

    async def aquery(self, question: str) -> AsyncGenerator[str, None]:
        if not self.qa_chain:
            raise ValueError("QA chain not set up. There might be an issue with initialization.")
        async for token in self.qa_chain.ainvoke(question):
            yield token
