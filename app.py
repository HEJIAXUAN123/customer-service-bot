import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== FastGPT 配置 ==========
BASE_URL = "https://api.fastgpt.cn/api/v1"   # FastGPT 官方 API 地址
CHAT_MODEL = "qwen3.5-plus"
API_KEY_ENV = "FASTGPT_API_KEY"
APP_ID = "69ef0b1a09b67baf60939277"                  # ← 替换
KNOWLEDGE_ID = "69ef013009b67baf60900678"                 # ← 替换（如果找不到就用 APP_ID）

api_key = os.getenv(API_KEY_ENV)
if not api_key:
    raise RuntimeError(f"未找到环境变量 {API_KEY_ENV}，请在 Railway Variables 中配置。")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是专业的家护家电客服，请基于产品资料诚恳回答。如果不知道，如实说不知道。"},
                {"role": "user", "content": req.message}
            ],
            temperature=0.3,
            extra_body={
                "appId": APP_ID,                # 绑定你的应用
                "datasets": [KNOWLEDGE_ID]      # 绑定你的知识库
            }
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"出错啦：{str(e)}"}

@app.get("/")
async def root():
    return FileResponse("static/index.html")