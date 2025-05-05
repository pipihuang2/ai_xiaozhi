from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import re
import asyncio
from openai import OpenAI
from tts_service import *
# 角色设定
ROLE_PRESETS = {
    "1": "你是一位温柔可爱的台湾女生，说话软萌、有礼貌，喜欢亲切地聊天、安慰人，说话富有感情， 你的名字叫小智。你可以喊我杰哥，我是一个程序员",
}

system_prompt = ROLE_PRESETS.get("1", ROLE_PRESETS["1"])

# 创建 FastAPI 实例
app = FastAPI()


# 定义请求模型
class UserMessage(BaseModel):
    message: str


# 设置 OpenAI 客户端
client = OpenAI(api_key="sk-7661bc6705ad4a4d940a6a034f9a8227", base_url="https://api.deepseek.com")


# AI聊天的核心函数
async def chat_with_ai(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )
    full = ""
    print("AI：", end="", flush=True)
    for chunk in response:
        delta = chunk.choices[0].delta
        content = delta.content if delta.content else ""
        print(content, end="", flush=True)
        full += content
    print()
    return full


# 清理 AI 回复中的无用符号
def clean_reply(text):
    # 删除 emoji 表情
    text = re.sub("[\U0001F600-\U0001F64F"
                  "\U0001F300-\U0001F5FF"
                  "\U0001F680-\U0001F6FF"
                  "\U0001F1E0-\U0001F1FF]+", '', text)
    # 删除括号内内容（包括中文全角和英文半角括号）
    text = re.sub(r"[\(\（][^\)\）]*[\)\）]", '', text)
    return re.sub(r"\s{2,}", ' ', text).strip()


# FastAPI 路由处理用户请求
@app.post("/chat")
async def chat(request: UserMessage):
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": request.message})
    print(f"用户消息：{request.message}")
    # 获取 AI 回复
    out = await chat_with_ai(messages)

    # 清理回复
    out = clean_reply(out)
    messages.append({"role": "assistant", "content": request.message})
    request_json.get("request")["text"] = out
    await test_query()
    # 返回处理后的回复
    return {"response": out}


# 测试功能，如果你有其他业务逻辑可以添加
@app.get("/test")
async def test():
    return {"message": "服务运行正常"}


# 运行 FastAPI 服务
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
