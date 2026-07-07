# agent_with_tool.py
import json
import re
import requests

# ---------- 定义工具（Skill） ----------
def calculator(expression: str) -> str:
    """
    计算器工具：输入数学表达式，返回计算结果
    例如：calculator("1 + 2") 返回 "3"
    """
    try:
        # 安全起见，只允许数字和运算符
        if not re.match(r'^[\d+\-*/().\s]+$', expression):
            return "错误：表达式包含非法字符"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"

# 工具列表（Agent 可以使用的工具清单）
TOOLS = [
    {
        "name": "calculator",
        "description": "执行数学计算，参数是一个完整的数学表达式，如 '1 + 2' 或 '3 * (4 + 5)'，不要用逗号分隔",
        "function": calculator
    }
]

# ---------- 连接本地模型 ----------
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

def chat_with_llm(messages):
    """调用本地 Ollama 模型"""
    payload = {
        "model": "qwen2.5:7b",
        "messages": messages,
        "temperature": 0.1,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# ---------- 核心：Agent 的思考 + 决策 + 执行 ----------
def run_agent(user_input):
    """
    Agent 主流程：
    1. 把用户输入 + 可用工具清单发给 LLM
    2. LLM 决定要不要调用工具，以及调用哪个
    3. 执行工具调用
    4. 把结果返回给用户
    """
    
    # 1. 构建系统提示词：告诉 LLM 它有哪些工具可用
    tool_descriptions = "\n".join([
        f"- {tool['name']}: {tool['description']}" 
        for tool in TOOLS
    ])
    
    system_prompt = f"""你是一个智能助手，可以使用以下工具来帮助用户：
{tool_descriptions}

如果用户的问题需要用到工具，请按以下格式回复：
TOOL: [工具名称]
ARGS: [参数]

如果不需要工具，请直接回答用户的问题。"""

    # 2. 把用户消息和系统提示一起发给 LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    # 3. 获取 LLM 的响应
    llm_response = chat_with_llm(messages)
    print(f"[Agent 思考] {llm_response}")  # 调试用
    
    # 4. 解析 LLM 的响应，判断是否要调用工具
    if "TOOL:" in llm_response and "ARGS:" in llm_response:
        # 提取工具名称和参数
        tool_name = llm_response.split("TOOL:")[1].split("ARGS:")[0].strip()
        tool_args = llm_response.split("ARGS:")[1].strip()
        
        print(f"[Agent 决策] 调用工具: {tool_name}, 参数: {tool_args}")
        
        # 5. 执行工具
        for tool in TOOLS:
            if tool["name"] == tool_name:
                result = tool["function"](tool_args)
                print(f"[工具执行结果] {result}")
                
                # 6. 把工具执行结果打包，发给 LLM 生成最终回复
                final_messages = messages + [
                    {"role": "assistant", "content": llm_response},
                    {"role": "tool", "content": f"工具 {tool_name} 返回的结果是：{result}"}
                ]
                final_response = chat_with_llm(final_messages)
                return final_response
    
    # 不需要工具的情况，直接返回 LLM 的原始回答
    return llm_response

# ---------- 测试 ----------
if __name__ == "__main__":
    print("=" * 40)
    print("Agent 测试：数学计算")
    print("=" * 40)
    
    test_input = "请问 123 + 456 等于多少？"
    print(f"用户: {test_input}")
    
    response = run_agent(test_input)
    print(f"Agent: {response}")
