# quant_agent.py
import json
import requests
from quant_skills import *
from datetime import datetime

# ==================== 1. Quant Skills 注册表 ====================

QUANT_SKILLS = [
    {
        "name": "get_stock_price",
        "description": "获取股票当前价格。用户说'股价'、'现在价格'时使用。",
        "parameters": [{"name": "symbol", "type": "string", "description": "股票代码，如 AAPL"}],
        "func": get_stock_price_impl
    },
    {
        "name": "get_stock_history",
        "description": "获取股票历史价格。用户说'历史价格'、'最近走势'时使用。",
        "parameters": [
            {"name": "symbol", "type": "string", "description": "股票代码"},
            {"name": "period", "type": "string", "description": "周期: 1d, 5d, 1mo, 3mo, 6mo, 1y, 默认1mo"}
        ],
        "func": get_stock_history_impl
    },
    {
        "name": "get_financials",
        "description": "获取股票财务指标。用户说'财务'、'PE'、'ROE'时使用。",
        "parameters": [{"name": "symbol", "type": "string", "description": "股票代码"}],
        "func": get_financials_impl
    },
    {
        "name": "calc_moving_average",
        "description": "计算移动平均线。用户说'均线'、'MA'时使用。",
        "parameters": [
            {"name": "symbol", "type": "string", "description": "股票代码"},
            {"name": "window", "type": "string", "description": "周期天数，默认20"}
        ],
        "func": calc_moving_average_impl
    },
    {
        "name": "calc_volatility",
        "description": "计算波动率。用户说'波动率'、'风险'时使用。",
        "parameters": [
            {"name": "symbol", "type": "string", "description": "股票代码"},
            {"name": "window", "type": "string", "description": "周期天数，默认30"}
        ],
        "func": calc_volatility_impl
    },
    {
        "name": "calc_sharpe",
        "description": "计算夏普比率。用户说'夏普'、'sharpe'时使用。",
        "parameters": [
            {"name": "symbol", "type": "string", "description": "股票代码"},
            {"name": "risk_free", "type": "string", "description": "无风险利率，默认0.03"}
        ],
        "func": calc_sharpe_impl
    },
    {
        "name": "backtest_ma_strategy",
        "description": "均线交叉策略回测。用户说'回测'、'均线策略'时使用。",
        "parameters": [
            {"name": "symbol", "type": "string", "description": "股票代码"},
            {"name": "short_ma", "type": "string", "description": "短期均线天数，默认10"},
            {"name": "long_ma", "type": "string", "description": "长期均线天数，默认30"}
        ],
        "func": backtest_ma_strategy_impl
    }
]

# ==================== 2. Agent 引擎（同上） ====================

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

def chat_with_llm(messages, model="qwen2.5:7b"):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload)
    return resp.json()["choices"][0]["message"]["content"]

def build_skill_description(skills):
    lines = []
    for s in skills:
        param_desc = ", ".join([f"{p['name']}: {p['type']}" for p in s.get("parameters", [])])
        lines.append(f"- {s['name']}({param_desc}): {s['description']}")
    return "\n".join(lines)

def build_system_prompt(skills):
    skill_text = build_skill_description(skills)
    return f"""你是一个量化研究助手，可以使用以下工具来分析股票和金融市场数据：

{skill_text}

当用户的问题需要使用工具时，你必须严格按以下 JSON 格式返回：
{{"tool": "工具名称", "args": {{"参数名": "参数值"}}}}

如果工具不需要参数，args 写空对象：
{{"tool": "get_time", "args": {{}}}}

当不需要使用工具时，直接返回：
{{"answer": "你的回答"}}

不要输出任何多余的解释、标记或代码块。只输出纯 JSON。"""

def run_quant_agent(user_input, verbose=True):
    system_prompt = build_system_prompt(QUANT_SKILLS)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    raw = chat_with_llm(messages)
    if verbose:
        print(f"[原始回复] {raw}")
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f"解析错误：{raw}"
    
    if "answer" in data:
        return data["answer"]
    
    if "tool" in data:
        tool_name = data["tool"]
        args = data.get("args", {})
        
        for skill in QUANT_SKILLS:
            if skill["name"] == tool_name:
                try:
                    result = skill["func"](**args)
                    # ===== 直接返回工具结果，不经过第二轮 =====
                    return result
                except Exception as e:
                    return f"工具执行出错：{e}"
        
        return f"未找到工具: {tool_name}"
    
    return "模型未按预期返回"
# ==================== 3. 交互式运行 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Quant Research Agent 已启动")
    print("可用功能：股价查询、历史走势、财务指标、均线、波动率、夏普比率、均线策略回测")
    print("输入 'exit' 退出")
    print("=" * 60)
    
    while True:
        user_input = input("\n📊 你: ")
        if user_input.lower() == 'exit':
            break
        response = run_quant_agent(user_input, verbose=True)
        print(f"\n🤖 Agent: {response}")