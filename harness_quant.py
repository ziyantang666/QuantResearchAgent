# harness.py
import re
from quant_agent import run_quant_agent
from quant_skills import SKILLS

# ==================== 测试集 ====================

TEST_CASES = [
    {"input": "AAPL 现在股价多少？", "expected": "价格"},
    {"input": "特斯拉最近走势怎么样？", "expected": "收盘价"},
    {"input": "NVDA 的 PE 是多少？", "expected": "PE"},
    {"input": "英伟达 20 日均线是多少？", "expected": "均线"},
    {"input": "苹果的波动率是多少？", "expected": "波动率"},
    {"input": "微软的夏普比率是多少？", "expected": "夏普比率"},
    {"input": "对 AAPL 做一个 10/30 日均线交叉回测", "expected": "回测"},
]

# ==================== 答案提取 ====================

def extract_answer(text: str) -> str:
    """从 Agent 回答中提取关键词"""
    # 去掉换行和多余空格
    text = text.replace("\n", " ").strip()
    # 提取数字（如果有）
    numbers = re.findall(r'\d+\.?\d*', text)
    if numbers:
        return numbers[-1]
    # 提取中文关键词
    keywords = ["价格", "收盘价", "均线", "波动率", "夏普", "回测", "PE", "ROE"]
    for kw in keywords:
        if kw in text:
            return kw
    return text[:20]  # 返回前20个字符

# ==================== Harness 主程序 ====================

def run_harness(verbose=True):
    correct = 0
    total = len(TEST_CASES)
    
    print("=" * 50)
    print(f"Quant Harness 测试开始，共 {total} 道题")
    print("=" * 50)
    
    for i, case in enumerate(TEST_CASES, 1):
        user_input = case["input"]
        expected = case["expected"]
        
        print(f"\n[{i}/{total}] {user_input}")
        print(f"  预期包含: {expected}")
        
        try:
            response = run_quant_agent(user_input, verbose=False)
            print(f"  Agent: {response[:100]}...")  # 只显示前100个字符
            
            # 判断是否包含预期关键词
            if expected in response:
                correct += 1
                print("  ✅")
            else:
                print(f"  ❌ 未包含预期关键词: {expected}")
                
        except Exception as e:
            print(f"  ❌ 出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"正确率: {correct}/{total} = {correct/total*100:.1f}%")
    print("=" * 50)

if __name__ == "__main__":
    run_harness(verbose=True)