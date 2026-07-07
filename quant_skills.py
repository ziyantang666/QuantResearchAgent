# quant_skills.py
import re
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# ==================== 1. 数据获取 Skill ====================

def get_stock_price_impl(symbol: str) -> str:
    """获取股票当前价格"""
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(period="1d")
        if data.empty:
            return f"错误：找不到股票 {symbol}"
        price = data["Close"].iloc[-1]
        return f"{symbol.upper()} 最新价格: ${price:.2f}"
    except Exception as e:
        return f"获取价格失败: {e}"

def get_stock_history_impl(symbol: str, period: str = "1mo") -> str:
    """获取股票历史价格，返回最近几天的收盘价"""
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(period=period)
        if data.empty:
            return f"错误：找不到股票 {symbol}"
        # 返回最近5天的收盘价
        recent = data["Close"].tail(5)
        result = f"{symbol.upper()} 最近5天收盘价:\n"
        for date, price in recent.items():
            result += f"  {date.strftime('%Y-%m-%d')}: ${price:.2f}\n"
        return result
    except Exception as e:
        return f"获取历史数据失败: {e}"

def get_financials_impl(symbol: str) -> str:
    """获取股票财务指标"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        pe = info.get("trailingPE", "N/A")
        pb = info.get("priceToBook", "N/A")
        roe = info.get("returnOnEquity", "N/A")
        if roe != "N/A":
            roe = f"{roe * 100:.2f}%"
        market_cap = info.get("marketCap", "N/A")
        if market_cap != "N/A":
            market_cap = f"${market_cap / 1e9:.2f}B"
        return f"""{symbol.upper()} 财务指标:
  PE: {pe}
  PB: {pb}
  ROE: {roe}
  市值: {market_cap}"""
    except Exception as e:
        return f"获取财务数据失败: {e}"

# ==================== 2. 因子计算 Skill ====================

def calc_moving_average_impl(symbol: str, window: str = "20") -> str:
    """计算移动平均线"""
    try:
        window = int(window)
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(period=f"{window+10}d")
        if data.empty:
            return f"错误：找不到股票 {symbol}"
        ma = data["Close"].rolling(window=window).mean().iloc[-1]
        current = data["Close"].iloc[-1]
        return f"""{symbol.upper()} {window}日均线: ${ma:.2f}
当前价格: ${current:.2f}
价格相对均线: {((current/ma - 1) * 100):.2f}%"""
    except Exception as e:
        return f"计算均线失败: {e}"

def calc_volatility_impl(symbol: str, window: str = "30") -> str:
    """计算年化波动率"""
    # 处理空字符串或无效值
    if not window or window.strip() == "":
        window = "30"
    try:
        window = int(window)
    except ValueError:
        return f"错误：窗口期 '{window}' 不是有效数字"
    
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(period=f"{window+10}d")
        if data.empty:
            return f"错误：找不到股票 {symbol}"
        returns = data["Close"].pct_change().dropna()
        if len(returns) < window:
            return f"数据不足，需要至少 {window} 个交易日"
        # 年化波动率 = 日波动率 * sqrt(252)
        daily_vol = returns.iloc[-window:].std()
        annual_vol = daily_vol * (252 ** 0.5)
        return f"""{symbol.upper()} 波动率分析:
  周期: {window}个交易日
  日波动率: {daily_vol:.2%}
  年化波动率: {annual_vol:.2%}"""
    except Exception as e:
        return f"计算波动率失败: {e}"

def calc_sharpe_impl(symbol: str, risk_free: str = "0.03") -> str:
    """计算夏普比率"""
    try:
        risk_free = float(risk_free)
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(period="1y")
        if data.empty:
            return f"错误：找不到股票 {symbol}"
        returns = data["Close"].pct_change().dropna()
        if len(returns) < 10:
            return "数据不足"
        avg_return = returns.mean() * 252
        vol = returns.std() * (252 ** 0.5)
        sharpe = (avg_return - risk_free) / vol if vol > 0 else 0
        return f"""{symbol.upper()} 夏普比率分析:
  年化收益率: {avg_return:.2%}
  年化波动率: {vol:.2%}
  夏普比率: {sharpe:.2f}
  评级: {'优秀' if sharpe > 1.5 else '良好' if sharpe > 0.8 else '一般' if sharpe > 0.3 else '较差'}"""
    except Exception as e:
        return f"计算夏普比率失败: {e}"

# ==================== 3. 回测类 Skill（简化版） ====================

def backtest_ma_strategy_impl(symbol: str, short_ma: str = "10", long_ma: str = "30") -> str:
    """均线交叉策略回测"""
    try:
        short = int(short_ma)
        long = int(long_ma)
        if short >= long:
            return "错误：短期均线必须小于长期均线"
        
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(period="1y")
        if data.empty:
            return f"错误：找不到股票 {symbol}"
        
        # 计算均线
        data['MA_short'] = data['Close'].rolling(window=short).mean()
        data['MA_long'] = data['Close'].rolling(window=long).mean()
        
        # 生成信号：短期上穿长期 = 买入
        data['Signal'] = 0
        data.loc[data['MA_short'] > data['MA_long'], 'Signal'] = 1
        data['Position'] = data['Signal'].diff()
        
        # 统计交易
        buys = len(data[data['Position'] == 1])
        sells = len(data[data['Position'] == -1])
        total_trades = buys + sells
        
        # 计算收益
        start_price = data['Close'].iloc[long]
        end_price = data['Close'].iloc[-1]
        total_return = (end_price - start_price) / start_price
        
        return f"""{symbol.upper()} 均线交叉策略回测 ({short}日 / {long}日):
  回测期间: {data.index[long].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}
  总收益: {total_return:.2%}
  买入信号: {buys}次, 卖出信号: {sells}次
  当前持仓: {'买入' if data['MA_short'].iloc[-1] > data['MA_long'].iloc[-1] else '空仓'}"""
    except Exception as e:
        return f"回测失败: {e}"
    
    # 在 quant_skills.py 末尾添加（让 harness 能导入）
SKILLS = [
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
