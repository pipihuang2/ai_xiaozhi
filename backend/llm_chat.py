import re
from openai import OpenAI

ROLE_PRESETS = {
    "1": "你是一位温柔可爱的台湾女生，说话软萌、有礼貌，喜欢亲切地聊天、安慰人，说话富有感情。你可以喊我杰哥，我是一个程序员",
}
system_prompt = ROLE_PRESETS.get("1", ROLE_PRESETS["1"])

#这个是给模型进行人物设定
messages = [{"role": "system", "content": system_prompt}]


client = OpenAI(api_key="sk-7661bc6705ad4a4d940a6a034f9a8227", base_url="https://api.deepseek.com")

def chat_with_ai(messages):
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

#这个是用来删除回复中的复杂符号之类的
def clean_reply(text):
    # 删除 emoji 表情
    text = re.sub("[\U0001F600-\U0001F64F"
                  "\U0001F300-\U0001F5FF"
                  "\U0001F680-\U0001F6FF"
                  "\U0001F1E0-\U0001F1FF]+", '', text)
    # 删除括号内内容（包括中文全角和英文半角括号）
    text = re.sub(r"[\(\（][^\)\）]*[\)\）]", '', text)
    return re.sub(r"\s{2,}", ' ', text).strip()


if __name__ == '__main__':
    from tts_service import *
    loop = asyncio.get_event_loop()
    ROLE_PRESETS = {
        "1": "你是一位温柔可爱的台湾女生，说话软萌、有礼貌，喜欢亲切地聊天、安慰人，说话富有感情,你的名字叫小智。你可以喊我杰哥，我是一个程序员",
    }
    system_prompt = ROLE_PRESETS.get("1", ROLE_PRESETS["1"])

    # 这个是给模型进行人物设定
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": "你好呀"})
    print(messages)
    out = chat_with_ai(messages)
    out = clean_reply(out)
    request_json.get("request")["text"] = out
    loop.run_until_complete(test_query())
    print(out)