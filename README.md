# DeepSeek_localized_deployment
 DeepSeek本地化部屬
# LLM 多人遠端部署指南

本指南介紹如何在本地部署大型語言模型（LLM），並提供多人遠端存取，包含 API 伺服器與 Web 使用者介面。

## 1. 環境與基礎架構準備

### 1.1 選擇部署框架

你可以選擇適合的推理框架，例如：

- **FastAPI**（高效能 API）
- **Flask/Django**（傳統 Web 框架）
- **Text Generation Inference (TGI)**（適用於 Hugging Face Transformer）
- **vLLM**（高效能推理）

### 1.2 安裝必要軟體

```bash
pip install fastapi uvicorn transformers torch
```

## 2. 構建後端 API

### 2.1 建立 FastAPI 伺服器

建立 `server.py` 並加入以下內容：

```python
from fastapi import FastAPI, HTTPException
from transformers import pipeline

app = FastAPI()
generator = pipeline("text-generation", model="你的模型名稱")

@app.post("/generate")
async def generate_text(prompt: str, max_length: int = 200):
    try:
        result = generator(prompt, max_length=max_length)
        return {"response": result[0]["generated_text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

啟動 API：

```bash
python server.py
```

## 3. 建立多人使用者管理機制

### 3.1 新增 Token 驗證

```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/generate")
async def generate_text(prompt: str, token: str = Depends(oauth2_scheme)):
    if token != "你的安全Token":  # 在正式環境應使用 JWT
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"response": generator(prompt)}
```

### 3.2 使用 WebSocket 進行即時推理（適用於多人並行）

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            result = generator(data, max_length=200)
            await websocket.send_text(result[0]["generated_text"])
    except WebSocketDisconnect:
        pass
```

## 4. 開發前端 UI

### 4.1 使用 HTML + JavaScript 呼叫 API

建立 `index.html`：

```html
<html>
<body>
    <h1>LLM Chat</h1>
    <textarea id="prompt"></textarea>
    <button onclick="generate()">送出</button>
    <p id="response"></p>
    <script>
        async function generate() {
            let prompt = document.getElementById("prompt").value;
            let response = await fetch("/generate", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({prompt})
            });
            let data = await response.json();
            document.getElementById("response").innerText = data.response;
        }
    </script>
</body>
</html>
```

### 4.2 使用 WebSocket

```html
<script>
    let ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
        document.getElementById("response").innerText = event.data;
    };
    function sendMessage() {
        ws.send(document.getElementById("prompt").value);
    }
</script>
```

## 5. 佈署與多使用者並發

### 5.1 使用 Gunicorn 佈署 FastAPI

```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000
```

### 5.2 設定 Nginx 反向代理

- 安裝 Nginx：
  ```bash
  sudo apt install nginx
  ```
- 配置 `/etc/nginx/sites-available/llm`
  ```nginx
  server {
      listen 80;
      server_name your_domain_or_ip;

      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }
  }
  ```
- 啟動 Nginx：
  ```bash
  sudo ln -s /etc/nginx/sites-available/llm /etc/nginx/sites-enabled/
  sudo systemctl restart nginx
  ```

## 6. 擴展功能

如果需要擴展功能，可考慮：

- **資料庫管理**（MySQL / PostgreSQL）：存儲對話記錄。
- **Redis 緩存**：提高 API 響應速度。
- **WebSocket + Celery**：處理長時間推理的請求。

## 7. 結論

本指南讓你能夠：

- **本地部署 LLM API**
- **提供 Web UI 讓多人同時遠端存取**
- **確保安全性（Token 或 WebSocket）**
- **透過 Nginx 進行流量管理，提高性能**

進一步優化可考慮：

- **使用 vLLM 來提高推理速度**
- **前端美化，支援多聊天室**
- **加入使用者驗證，限制 API 使用者數量**

這樣，你的多人遠端 LLM 服務就可以順利運行了！🚀

