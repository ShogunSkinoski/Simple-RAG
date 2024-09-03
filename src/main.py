import io
import os
import re
import cv2
from fastapi import FastAPI, Depends, Request, File, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import uvicorn
from rag_system import RAGSystem
from dotenv import load_dotenv
import json
import logging
from ocr import OCR
from models import *
from langchain_anthropic import ChatAnthropic
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import ValidationError

from src.models import ReceiptAnalysisResponse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
ocr = OCR(lang='en') 
app = FastAPI()
pdf_path = "data"
rag_system = RAGSystem(pdf_path)
chat_model = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))

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

def salvage_data(raw_data):
    try:
        return ReceiptAnalysisResponse(**raw_data)
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        salvaged_data = {}
        for field in ReceiptAnalysisResponse.__fields__:
            if field in raw_data:
                if field == 'receipt' and isinstance(raw_data[field], dict):
                    salvaged_receipt = {}
                    for receipt_field in Receipt.__fields__:
                        if receipt_field in raw_data[field]:
                            if receipt_field == 'items' and isinstance(raw_data[field][receipt_field], list):
                                salvaged_items = []
                                for item in raw_data[field][receipt_field]:
                                    try:
                                        salvaged_items.append(Item(**item))
                                    except ValidationError:
                                        pass
                                salvaged_receipt['items'] = salvaged_items
                            else:
                                salvaged_receipt[receipt_field] = raw_data[field][receipt_field]
                    salvaged_data['receipt'] = Receipt(**salvaged_receipt)
                else:
                    salvaged_data[field] = raw_data[field]
        return ReceiptAnalysisResponse(**salvaged_data)

@app.post("/receipt-analysis", response_model=ReceiptAnalysisResponse)
async def receipt_analysis(image: UploadFile = File(...)):
    try:
        if not image.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return {"error": "Only JPG and PNG files are supported"}

        contents = await image.read()
        image_stream = io.BytesIO(contents)
        image_np = np.frombuffer(image_stream.getvalue(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            return {"error": "Failed to decode the image"}

        extracted_text = ocr.get_receipt_info(image)
        
        parser = PydanticOutputParser(pydantic_object=ReceiptAnalysisResponse)

        prompt = ChatPromptTemplate.from_template(
            """Analyze the following text extracted from a receipt and format it into a JSON structure. Include educated guesses for missing information where appropriate. Return ONLY the JSON output without any additional text or explanation. 
                For the following fields, if the information is not explicitly provided, make an educated guess based on the context:
            - description (of the transaction)
            - country (of the merchant)
            - city (of the merchant)
            - itemDescription (for each item)
            - category (for each item)
            - generalCategory (for each item)
            please provide only in Turkish 
            Extracted text:
            {text}

            {format_instructions}"""
        )

        formatted_prompt = prompt.format(
            text=extracted_text,
            format_instructions=parser.get_format_instructions()
        )

        output = chat_model.predict(formatted_prompt)
        
        def extract_json(text):
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return match.group()
            return text

        try:
            json_output = extract_json(output)
            parsed_output = parser.parse(json_output)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            try:
                raw_data = json.loads(json_output)
                parsed_output = salvage_data(raw_data)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from LLM output")
                return {"error": "Failed to process the receipt"}

        return parsed_output
    
    except Exception as e:
        logger.error(f"Error during receipt analysis: {str(e)}", exc_info=True)
        return {"error": f"An error occurred during processing: {str(e)}"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)