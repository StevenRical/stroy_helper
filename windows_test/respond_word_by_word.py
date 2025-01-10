import tkinter as tk
from openai import OpenAI
import os

# 环境变量中获取 API 密钥
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("未在环境变量中找到 API 密钥，请设置 OPENAI_API_KEY。")

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=openai_api_key,
    base_url="https://api.chatanywhere.tech/v1"
)

# 模型选择
MODEL = "gpt-3.5-turbo"

# 实现逐字输出，同时判断增量数据是否有效
def gpt_streaming_character_by_character(messages):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True  # 流式传输
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content is not None:  # 判断属性和内容是否存在
            content = delta.content
            for char in content:
                print(char, end="", flush=True)
    

if __name__ == '__main__':
    messages = [{'role': 'user','content': '鲁迅和周树人的关系'},]
    # 流式调用
    gpt_streaming_character_by_character(messages)