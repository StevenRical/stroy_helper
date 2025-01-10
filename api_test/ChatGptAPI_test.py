from openai import OpenAI

# 
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-xzZ12OC2jzJQ71VUQZFA6AccFEX1CDrsxDMneC20HFrTXp9e",
    base_url="https://api.chatanywhere.tech/v1"
    # base_url="https://api.chatanywhere.org/v1"
)

# 定义请求的内容
def chat_with_gpt(prompt):
    response = client.completions.create(model="gpt-3.5-turbo",  # 或者你可以使用gpt-3.5  gpt-4模型
    prompt=prompt,
    max_tokens=150,  # 设置返回的最大token数
    temperature=0.7,  # 控制回答的随机性，0.7是一个常见的值
    top_p=1.0,  # 采样温度
    frequency_penalty=0.0,
    presence_penalty=0.0)

    # 获取并返回响应的文本
    return response.choices[0].text.strip()

# 示例使用
user_input = "告诉我今天的天气怎么样？"
response = chat_with_gpt(user_input)

print("ChatGPT的回答:", response)
