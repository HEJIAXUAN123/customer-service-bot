import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 挂载静态文件目录（前端 HTML、CSS、JS）
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- 模型配置 ----------
# 使用阿里千问（默认）
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
CHAT_MODEL = "qwen-plus"
API_KEY_ENV = "DASHSCOPE_API_KEY"
# BASE_URL = "https://cloud.fastgpt.cn/api" # 注意：这里填你实际看到的接口基础地址
# CHAT_MODEL = "家护家电客服"
# API_KEY_ENV = "FASTGPT_API_KEY"

api_key = os.getenv(API_KEY_ENV) # 改从 FASTGPT_API_KEY 环境变量读取

# 如果想用 DeepSeek，改成下面三行：
# BASE_URL = "https://api.deepseek.com"
# CHAT_MODEL = "deepseek-chat"
# API_KEY_ENV = "DEEPSEEK_API_KEY"

api_key = os.getenv(API_KEY_ENV)
if not api_key:
    raise RuntimeError(f"没有读取到环境变量 {API_KEY_ENV}")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": req.message}],
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"出错啦：{str(e)}"}

@app.get("/")
async def root():
    return FileResponse("static/index.html")