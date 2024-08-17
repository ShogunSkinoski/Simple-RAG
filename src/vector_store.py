from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import shutil
import os

class VectorStore:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings()
        self.vector_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
    
    def create_vector_store(self, documents):
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vector_store.persist()
    
    def get_retriever(self):
        if self.is_empty():
            raise ValueError("Vector store is empty. Call create_vector_store() first.")
        return self.vector_store.as_retriever()
    
    def is_empty(self):
        return self.vector_store._collection.count() == 0
    
    def delete(self):
        shutil.rmtree(self.persist_directory, ignore_errors=True)
        os.makedirs(self.persist_directory)
        self.vector_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)