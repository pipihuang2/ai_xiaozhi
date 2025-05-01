import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import re
from xiaozhi import test_submit,request_json
import asyncio


# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-7661bc6705ad4a4d940a6a034f9a8227",  # 替换为你的 API 密钥
    base_url="https://api.deepseek.com"  # DeepSeek 的 API 基础地址
)

# 初始化 TTS (Text-to-Speech) 引擎
engine = pyttsx3.init()

# 设置语音属性（可选）
engine.setProperty("rate", 150)  # 语速
engine.setProperty("volume", 0.9)  # 音量

# 初始化语音识别
recognizer = sr.Recognizer()

# 初始消息列表
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("AI 助手已启动，使用语音或文本输入。说 '退出' 或 '停止' 结束对话。\n")





def remove_emoji_soft(text):
    # 只匹配真正的 emoji（不匹配中文、标点、装饰符）
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # 常规表情
        "\U0001F300-\U0001F5FF"  # 天气/动物/物体
        "\U0001F680-\U0001F6FF"  # 交通工具
        "\U0001F1E0-\U0001F1FF"  # 国旗
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)



def speak(text):
    """将文本转化为语音输出"""
    engine.say(text)
    engine.runAndWait()


def listen():
    """从麦克风捕获语音输入"""
    with sr.Microphone() as source:
        print("请说话...")
        try:
            recognizer.adjust_for_ambient_noise(source)  # 调整噪声
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="zh-CN")  # 语音转文本
            print(f"你: {text}")
            return text
        except sr.WaitTimeoutError:
            print("未检测到语音输入，请重试。")
        except sr.UnknownValueError:
            print("无法识别语音，请重试。")
        except sr.RequestError as e:
            print(f"语音识别服务出错: {e}")
        return None


while True:
    # 选择语音或文本输入
    print("\n选择输入方式：1. 键盘输入 2. 语音输入")
    input_mode = input("输入 1 或 2: ").strip()

    if input_mode == "1":
        user_input = input("你: ")
    elif input_mode == "2":
        user_input = listen()
        if not user_input:
            continue
    else:
        print("无效选择，请重试！")
        continue

    # 检查退出指令
    if user_input.lower() in ["退出", "停止", "exit", "quit"]:
        print("对话已结束。再见！")
        speak("对话已结束，再见！")
        break

    # 将用户输入加入消息历史
    messages.append({"role": "user", "content": user_input})

    try:
        # 调用 API 获取流式回复
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        print("AI: ", end="", flush=True)
        assistant_reply = ""  # 用于存储完整回复

        # 逐步接收生成的内容
        for chunk in response:
            delta = chunk.choices[0].delta
            content = delta.content if delta.content else ""  # 确保 content 不为空
            assistant_reply += content
            print(content, end="", flush=True)

        print("\n")  # 生成结束后换行

        # 语音输出生成的回复
        if assistant_reply.strip():
            print('我是assistant_reply2', assistant_reply)
            assistant_reply=remove_emoji_soft(assistant_reply)
            print('我是assistant_reply', assistant_reply)
            request_json.get("request")["text"] = assistant_reply
            await test_submit()
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(test_submit())

            messages.append({"role": "assistant", "content": assistant_reply})
        else:
            print("AI 没有生成有效的内容，请检查输入或模型状态。\n")
            speak("我无法生成有效的内容，请再试一次。")

    except Exception as e:
        print(f"出错了: {e}")
        speak("发生错误，请稍后再试。")
