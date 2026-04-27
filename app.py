import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 挂载前端静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== FastGPT 配置 ==========
BASE_URL = "https://cloud.fastgpt.cn/api"          # FastGPT API 前缀
CHAT_MODEL = "家护家电客服"                         # 可以保持原名，不一定影响
API_KEY_ENV = "FASTGPT_API_KEY"                    # 环境变量名，与 Railway Variables 中一致
KNOWLEDGE_ID = "69ef013009b67baf60900678"                      # ← 替换成你找到的那串ID

# 读取环境变量（确保在 Railway Variables 中添加了 FASTGPT_API_KEY）
api_key = os.getenv(API_KEY_ENV)
if not api_key:
    raise RuntimeError(f"未找到环境变量 {API_KEY_ENV}，请在 Railway 的 Variables 中添加。")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

# ========== 请求体模型 ==========
class ChatRequest(BaseModel):
    message: str

# ========== 聊天接口 ==========
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是专业的家护家电客服，请基于产品资料诚恳回答。如果不知道，如实说不知道。"
                },
                {"role": "user", "content": req.message}
            ],
            temperature=0.3,
            # 关键：绑定你的知识库
            extra_body={
                "datasets": [KNOWLEDGE_ID]   # 列表里放你的知识库ID
            }
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"出错啦：{str(e)}"}

# ========== 根路径返回前端页面 ==========
@app.get("/")
async def root():
    return FileResponse("static/index.html")