import asyncio
import speech_recognition as sr
from openai import OpenAI
import re
import uuid
import json
import gzip
import copy
import websockets
import io
from pydub import AudioSegment
from pydub.playback import play
# --- 角色设定（可自定义多个角色） ---
ROLE_PRESETS = {
    "1": "你是一位温柔可爱的台湾女生，说话软萌、有礼貌，喜欢亲切地聊天、安慰人，说话富有感情。你可以喊我杰哥，我是一个程序员",
    "2": "你是一个严谨高效的助手，逻辑清晰、回答准确，不开玩笑。",
    "3": "你是一个搞笑活泼的男孩子，说话幽默、会讲段子，喜欢打趣和逗人开心。"
}

# 初始化 OpenAI 客户端
client = OpenAI(api_key="sk-7661bc6705ad4a4d940a6a034f9a8227", base_url="https://api.deepseek.com")

# 初始化语音识别器
recognizer = sr.Recognizer()

# 字节跳动 TTS 配置
appid = "8394079928"
token = "M0CUGPoFeM-eWWpS_DG151hce7X5lQUL"
cluster = "volcano_tts"
voice_type = "zh_female_wanwanxiaohe_moon_bigtts"
api_url = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"
default_header = bytearray(b'\x11\x10\x11\x00')

request_json = {
    "app": {"appid": appid, "token": "access_token", "cluster": cluster},
    "user": {"uid": "123"},
    "audio": {
        "voice_type": voice_type,
        "encoding": "wav",  # 内存播放更稳定
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": "123",
        "text": "你好",
        "text_type": "plain",
        "operation": "submit"
    }
}


def clean_reply(text):
    # 删除 emoji 表情
    text = re.sub("[\U0001F600-\U0001F64F"
                  "\U0001F300-\U0001F5FF"
                  "\U0001F680-\U0001F6FF"
                  "\U0001F1E0-\U0001F1FF]+", '', text)
    # 删除括号内内容（包括中文全角和英文半角括号）
    text = re.sub(r"[\(\（][^\)\）]*[\)\）]", '', text)
    return re.sub(r"\s{2,}", ' ', text).strip()


def listen():
    with sr.Microphone() as source:
        print("🎤 请说话...")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="zh-CN")
            print(f"你：{text}")
            return text
        except Exception as e:
            print(f"语音识别失败: {e}")
            return None


def parse_response_to_memory(res, buffer: io.BytesIO):
    message_type = res[1] >> 4
    flag = res[1] & 0x0f
    header_size = res[0] & 0x0f
    payload = res[header_size * 4:]
    if message_type == 0xb:
        if flag == 0:
            return False
        seq = int.from_bytes(payload[:4], "big", signed=True)
        payload_size = int.from_bytes(payload[4:8], "big")
        payload = payload[8:]
        buffer.write(payload)
        return seq < 0
    elif message_type == 0xf:
        print("⚠️ 错误信息:", payload)
        return True
    return False


async def speak(text):
    payload_json = copy.deepcopy(request_json)
    payload_json["request"]["text"] = text
    payload_json["request"]["reqid"] = str(uuid.uuid4())
    payload_json["request"]["operation"] = "submit"
    payload_json["audio"]["voice_type"] = voice_type

    payload_bytes = gzip.compress(json.dumps(payload_json).encode())
    packet = bytearray(default_header)
    packet.extend(len(payload_bytes).to_bytes(4, 'big'))
    packet.extend(payload_bytes)

    header = {"Authorization": f"Bearer; {token}"}
    audio_buffer = io.BytesIO()

    async with websockets.connect(api_url, extra_headers=header, ping_interval=None) as ws:
        await ws.send(packet)
        while True:
            res = await ws.recv()
            if parse_response_to_memory(res, audio_buffer):
                break

    try:
        audio_buffer.seek(0)
        audio = AudioSegment.from_file(audio_buffer, format="wav")
        print("🎧 正在播放语音...")
        play(audio)  # ✅ 使用 ffplay 播放，不会崩溃
    except Exception as e:
        print(f"播放失败: {e}")


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


async def main():
    print("🧠 可用角色：")
    for k, v in ROLE_PRESETS.items():
        print(f"{k}. {v.split('，')[0]}")

    role_id = input("请选择角色编号（如 1）: ").strip()
    system_prompt = ROLE_PRESETS.get(role_id, ROLE_PRESETS["1"])
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        print("\n选择输入方式：1=文本  2=语音  0=退出")
        mode = input("你的选择: ").strip()

        if mode == "0":
            print("👋 再见！")
            break
        elif mode == "1":
            user_input = input("你：")
        elif mode == "2":
            user_input = listen()
            if not user_input:
                continue
        else:
            print("无效输入")
            continue

        if user_input.strip().lower() in ["退出", "stop"]:
            break

        messages.append({"role": "user", "content": user_input})
        if len(messages) > 20:
            messages = [messages[0]] + messages[-19:]

        reply = await chat_with_ai(messages)
        reply_clean = clean_reply(reply)
        messages.append({"role": "assistant", "content": reply_clean})

        await speak(reply_clean)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
