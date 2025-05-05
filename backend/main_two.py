import requests

url = "http://127.0.0.1:8000/chat"

while True:
    # 获取用户输入
    user_input = input("请输入消息（输入 'exit' 退出）：")

    # 如果用户输入 'exit'，则退出循环
    if user_input.lower() == "exit":
        print("退出聊天。")
        break

    # 构建请求数据
    data = {
        "message": user_input,
    }

    # 发送 POST 请求到 FastAPI 服务器
    response = requests.post(url, json=data)

    # 打印服务器的响应内容
    if response.status_code == 200:
        print("AI 回复：", response.json()["response"])
    else:
        print(f"请求失败，状态码：{response.status_code}")
