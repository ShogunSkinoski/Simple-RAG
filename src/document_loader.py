from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class DocumentLoader:
    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load(self, folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('.pdf'):
                pdf_path = os.path.join(folder_path, file)
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                chunked_docs = self.split_documents(documents)
                yield chunked_docs
    
    def split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        split_docs = text_splitter.split_documents(documents)
        return split_docs

