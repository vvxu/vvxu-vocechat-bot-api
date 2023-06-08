# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, BackgroundTasks
from models import *
from mod.voce_bot import *
# from mod.mongo_model import *
import time


app = FastAPI()


@app.get("/")
async def index():
    return "你好"


# 验证连接
@app.get("/voce_api")
async def get_voce_api():
    return {"status": "OK"}


# 连接
@app.post("/voce_api")
async def post_voce_api(data: VoceMsg, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_handler, data)
    return {"status": "OK"}


#     
async def run_handler(data):
    print(f"执行到31 {time.time()}")
    handler = MessageHandler(data)
    print(f"执行到32 {time.time()}")
    handler.handle()
