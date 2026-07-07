import json
import re
import requests
import random
from datetime import datetime

# ==================== 1. 定义所有 Skill ====================

def calculator_impl(expression: str) -> str:
    """计算器：安全地计算数学表达式"""
    expression = re.sub(r'\s+', '', expression)
    if not re.match(r'^[\d+\-*/().]+$', expression):
        return "错误：表达式包含非法字符"
    try:
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "错误：除以零"
    except Exception:
        return "错误：无效的数学表达式"


def text_repeater_impl(text: str, times: str = "3") -> str:
    """文本重复器：把文字重复N遍"""
    try:
        n = int(times)
        if n > 20:
            return "错误：次数不能超过20"
        return " ".join([text] * n)
    except ValueError:
        return "错误：次数必须是数字"


def dice_roller_impl(sides: str = "6") -> str:
    """掷骰子：掷一个N面的骰子"""
    try:
        n = int(sides)
        if n < 2:
            return "错误：骰子面数至少为2"
        if n > 100:
            return "错误：骰子面数不能超过100"
        result = random.randint(1, n)
        return f"🎲 掷了 {n} 面骰子，结果是：{result}"
    except ValueError:
        return "错误：面数必须是数字"


def time_impl() -> str:
    """获取当前时间"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def word_counter_impl(text: str) -> str:
    """字数统计：统计一段文字的字数"""
    if not text:
        return "错误：文本为空"
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    total = len(text)
    return f"总字符数: {total}，中文字符: {chinese_chars}，英文单词: {english_words}"


# ==================== 2. Skill 注册表 ====================

SKILLS = [
    {
        "name": "calculator",
        "description": "执行数学计算。当你需要计算加减乘除、括号运算时，使用这个工具。",
        "parameters": [{"name": "expression", "type": "string", "description": "完整的数学表达式"}],
        "func": calculator_impl
    },
    {
        "name": "text_repeater",
        "description": "把一段文字重复多次。当用户说'重复'、'复读'、'说三遍'时使用。",
        "parameters": [
            {"name": "text", "type": "string", "description": "要重复的文字"},
            {"name": "times", "type": "string", "description": "重复次数，默认为3"}
        ],
        "func": text_repeater_impl
    },
    {
        "name": "dice_roller",
        "description": "掷骰子。当用户说'掷骰子'、'投骰子'时使用。",
        "parameters": [{"name": "sides", "type": "string", "description": "骰子的面数，默认为6"}],
        "func": dice_roller_impl
    },
    {
        "name": "get_time",
        "description": "获取当前日期和时间。当用户问'现在几点'、'今天几号'时使用。",
        "parameters": [],
        "func": time_impl
    },
    {
        "name": "word_counter",
        "description": "统计一段文字的字数和字符数。当用户说'统计字数'、'数一下'时使用。",
        "parameters": [{"name": "text", "type": "string", "description": "要统计的文字"}],
        "func": word_counter_impl
    }
]


# ==================== 3. Agent 核心引擎 ====================

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

def chat_with_llm(messages):
    payload = {
        "model": "qwen2.5:7b",
        "messages": messages,
        "temperature": 0.0,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload)
    return resp.json()["choices"][0]["message"]["content"]


def build_skill_description(skills):
    lines = []
    for s in skills:
        param_desc = ", ".join([f"{p['name']}: {p['type']}" for p in s["parameters"]])
        lines.append(f"- {s['name']}({param_desc}): {s['description']}")
    return "\n".join(lines)


def build_system_prompt(skills):
    skill_text = build_skill_description(skills)
    return f"""你是一个智能助手，可以使用工具来回答用户的问题。

可用工具如下：
{skill_text}

当用户的问题需要使用工具时，你必须严格按以下 JSON 格式返回：
{{"tool": "工具名称", "args": {{"参数名": "参数值"}}}}

如果工具不需要参数，args 写空对象：
{{"tool": "get_time", "args": {{}}}}

当不需要使用工具时，直接返回：
{{"answer": "你的回答"}}

不要输出任何多余的解释、标记或代码块。只输出纯 JSON。"""


def run_agent(user_input):
    system_prompt = build_system_prompt(SKILLS)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    raw = chat_with_llm(messages)
    print(f"[原始回复] {raw}")
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f"解析错误：模型返回了非 JSON 格式\n{raw}"
    
    if "answer" in data:
        return data["answer"]
    
    if "tool" in data:
        tool_name = data["tool"]
        args = data.get("args", {})
        
        for skill in SKILLS:
            if skill["name"] == tool_name:
                try:
                    result = skill["func"](**args)
                except Exception as e:
                    result = f"工具执行出错：{e}"
                
                # ========== 只改这一块 ==========
                final_messages = messages + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": f"工具返回结果：{result}。请用自然语言回答用户，只输出最终答案数字，不要重复算式。"}
                ]
                # ================================
                
                final_raw = chat_with_llm(final_messages)
                try:
                    final_data = json.loads(final_raw)
                    return final_data.get("answer", final_raw)
                except:
                    return final_raw
        
        return f"未找到工具: {tool_name}"
    
    return "模型未按预期返回"


# ==================== 4. 测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("多功能 Agent 测试")
    print("=" * 50)
    
    test_cases = [
        "123 + 456 等于多少？",
        "请把 '你好' 重复三遍",
        "掷一个骰子",
        "现在几点了？",
        "统计一下 '今天天气真好' 有多少个字"
    ]
    
    for user_input in test_cases:
        print("\n" + "-" * 40)
        print(f"用户: {user_input}")
        response = run_agent(user_input)
        print(f"Agent: {response}")