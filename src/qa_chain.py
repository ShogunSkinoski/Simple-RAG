from langchain.chains import RetrievalQA
from langchain_anthropic import ChatAnthropic
from langchain.callbacks.base import AsyncCallbackHandler
from typing import Any, Dict, List, AsyncGenerator
import asyncio

class StreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self):
        self.tokens = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.tokens.put(token)

    async def on_llm_end(self, *args, **kwargs) -> None:
        await self.tokens.put("[DONE]")

class QAChain:
    def __init__(self, retriever, model_name='claude-3-opus-20240229'):
        self.retriever = retriever
        self.callback_handler = StreamingCallbackHandler()
        self.llm = ChatAnthropic(model=model_name, streaming=True, callbacks=[self.callback_handler])
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever
        )
    
    async def ainvoke(self, question: str) -> AsyncGenerator[str, None]:
        task = asyncio.create_task(self.qa_chain.ainvoke({"query": question}))
        try:
            while True:
                try:
                    token = await asyncio.wait_for(self.callback_handler.tokens.get(), timeout=1.0)
                    if token == "[DONE]":
                        break
                    yield token
                except asyncio.TimeoutError:
                    if task.done():
                        break
        finally:
            if not task.done():
                task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error in QA chain: {str(e)}")
                yield f"[ERROR: {str(e)}]"
        
        yield "[DONE]"