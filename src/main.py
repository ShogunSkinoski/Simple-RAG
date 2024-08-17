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

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_rag_system():
    return rag_system

@app.get("/")
def read_root():
    return FileResponse("static/sse_demo.html")

@app.get("/query")
async def query(request: Request, question: str, rag_system: RAGSystem = Depends(get_rag_system)):
    async def event_generator():
        try:
            logger.info(f"Starting query: {question}")
            async for token in rag_system.aquery(question):
                if await request.is_disconnected():
                    logger.warning("Client disconnected")
                    break
                if token == "[DONE]":
                    yield f"data: {json.dumps({'response': '[DONE]'})}\n\n"
                    logger.info("Query completed")
                else:
                    yield f"data: {json.dumps({'response': token})}\n\n"
        except Exception as e:
            logger.error(f"Error during query: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    rag_system.update_user_documents()