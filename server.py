from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import asyncio

app = FastAPI()

# 假設這是一個處理語言模型請求的函式
async def process_request(user_input: str) -> str:
    await asyncio.sleep(1)  # 模擬延遲
    return f"模型回應：{user_input[::-1]}"  # 這裡應該替換為 LLM 推理

class RequestModel(BaseModel):
    input_text: str

@app.post("/chat")
async def chat(request: RequestModel):
    response = await process_request(request.input_text)
    return {"response": response}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = await process_request(data)
        await websocket.send_text(response)
