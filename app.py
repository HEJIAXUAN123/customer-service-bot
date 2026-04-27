import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== ⚠️ 已根据 FastGPT 标准 API 配置 ==========
BASE_URL = "https://api.fastgpt.cn/api/v1"  # 这是 FastGPT 官方 API 基础地址
CHAT_MODEL = "qwen3.5-plus"                 # 从你的配置里确认的模型名
API_KEY_ENV = "FASTGPT_API_KEY"
KNOWLEDGE_ID = "69ef013009b67baf60900678"                # ← 替换成真实ID

api_key = os.getenv(API_KEY_ENV)
if not api_key:
    raise RuntimeError(f"未找到环境变量 {API_KEY_ENV}")

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
                "datasets": [KNOWLEDGE_ID] # 关键：绑定知识库
            }
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"出错啦：{str(e)}"}

@app.get("/")
async def root():
    return FileResponse("static/index.html")