import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 挂载前端页面
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- 阿里千问配置 ----------
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
CHAT_MODEL = "qwen-plus"
API_KEY_ENV = "DASHSCOPE_API_KEY"

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
                {"role": "system", "content": "你是专业的家护家电客服，请基于产品资料诚恳回答。"},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"出错啦：{str(e)}"}

@app.get("/")
async def root():
    return FileResponse("static/index.html")