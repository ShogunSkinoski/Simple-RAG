from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from rag_system import RAGSystem
from dotenv import load_dotenv
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()
pdf_path = "data"
rag_system = RAGSystem(pdf_path)
rag_system.update_user_documents()