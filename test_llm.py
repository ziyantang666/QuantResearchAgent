# 先测试 Ollama 是否正常工作
from openai import OpenAI

# 连接本地 Ollama 服务（Ollama 默认端口是 11434）
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 本地服务不需要真实key，但参数必须填
)

# 调用本地模型
response = client.chat.completions.create(
    model="llama3.2:1b",
    messages=[
        {"role": "user", "content": "你好，请用一句话介绍你自己"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)