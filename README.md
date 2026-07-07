# Quant Research Agent

基于 Ollama + Qwen2.5-7B 的本地量化研究助手，通过自然语言对话完成股票数据查询、技术指标计算和策略回测。

## 功能列表

| 功能 | 说明 | 示例问题 |
|------|------|----------|
| 股价查询 | 获取当前股价 | AAPL 现在股价多少？ |
| 历史走势 | 获取最近收盘价 | 特斯拉最近走势怎么样？ |
| 财务指标 | 获取 PE/PB/ROE/市值 | NVDA 的 PE 和 ROE 是多少？ |
| 移动平均线 | 计算 N 日均线 | 英伟达 20 日均线是多少？ |
| 波动率 | 计算年化波动率 | 苹果的波动率是多少？ |
| 夏普比率 | 计算风险调整后收益 | 微软的夏普比率是多少？ |
| 均线回测 | 均线交叉策略回测 | 对 AAPL 做 10/30 日均线交叉回测 |

## 快速开始

### 1. 安装 Ollama 并下载模型

```bash
ollama pull qwen2.5:7b
```

### 2. 安装依赖

```bash
pip install yfinance pandas requests
```

### 3. 启动 Agent

```bash
python quant_agent.py
```

### 4. 开始提问

输入自然语言问题，例如：

```
📊 你: AAPL 现在股价多少？
🤖 Agent: AAPL 最新价格: $288.26
```

输入 `exit` 退出。

## 项目结构

```
QuantResearchAgent/
├── quant_agent.py          # Agent 主程序
├── quant_skills.py         # 7 个量化 Skill
├── harness_quant.py        # 自动化测试
└── README.md               # 项目说明
```

## 技术栈

- Ollama + Qwen2.5-7B（本地模型）
- yfinance（美股数据）
- Python 3.12 + requests + pandas

## 运行测试

```bash
python harness_quant.py
```