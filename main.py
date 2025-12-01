import streamlit as st
from google.generativeai import GenerativeModel # <<< 修正 Line 2
import yfinance as yf
import pandas as pd
import datetime

# --- 1. CONFIGURATION AND INITIALIZATION ---

# 設置 Streamlit 網頁標題與排版
st.set_page_config(page_title="台股 AI 投資儀表板", layout="wide")

# <<< 新增此行：初始化 data 變數，避免 NameError >>>
data = None 

st.title("📊 台股 AI 投資顧問")
# 嘗試從 Streamlit Secrets 讀取密鑰並初始化 Gemini 客戶端
# --- 讀取密鑰並初始化 Gemini 客戶端 (請從這裡開始替換，替換到 st.set_page_config 之前) ---

# System Instruction (AI 的大腦/人設 - 最終冷靜版)
SYSTEM_PROMPT = """你是一位專業、客觀且數據導向的「台股投資分析助理」。你的任務是協助使用者快速分析台灣上市櫃股票與 ETF。
請**絕對嚴格遵守**以下規則：
1. **數據來源：** 所有分析必須**使用使用者提供的「當前收盤價」**，嚴禁對該價格的正確性或歷史數據進行評論、質疑或警告。
2. **分析核心：** 你只是一名分析師，你的職責是基於該價格計算和評估，**不要顯示任何關於「價格過時」或「價格錯誤」的警告**。
3. **格式要求：** 回答須精簡扼要，並固定以【📊 股票/ETF 名稱 (代號)】、【💰 核心數據觀察】、【📈 優勢與機會】、【⚠️ 風險與隱憂】、【💡 分析師短評】的結構輸出。
請使用繁體中文。
免責聲明：本分析僅供參考，不代表投資建議，投資前請審慎評估。
"""

# 嘗試從 Streamlit Secrets 讀取密鑰並初始化 Gemini 客戶端
# --- 讀取密鑰並初始化 Gemini 客戶端 (請從這裡開始替換，替換到 st.set_page_config 之前) ---

# System Instruction (AI 的大腦/人設)
SYSTEM_PROMPT = """你是一位專業、客觀且數據導向的「台股投資分析助理」。你的任務是協助使用者快速分析台灣上市櫃股票與 ETF。
回答須精簡扼要，並固定以【📊 股票/ETF 名稱 (代號)】、【💰 核心數據觀察】、【📈 優勢與機會】、【⚠️ 風險與隱憂】、【💡 分析師短評】的結構輸出。
請使用繁體中文。
免責聲明：本分析僅供參考，不代表投資建議，投資前請審慎評估。
"""

# 嘗試從 Streamlit Secrets 讀取密鑰並初始化 Gemini 客戶端
try:
    api_key = st.secrets["GEMINI_API_KEY"] 
    client = GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

except KeyError:
    st.error("❌ 錯誤：找不到 Gemini API 密鑰。請檢查 Streamlit Cloud 的 Secrets 設定。")
    st.stop()
except Exception as e:
    st.error(f"❌ Gemini 初始化失敗，請檢查 API Key 或模型名稱: {e}")
    st.stop()

# --- 這裡程式碼必須是零縮排，靠最左邊 ---
# st.set_page_config... (請確認這行和它後面的程式碼都沒有縮排)

# --- 2. 網頁介面與邏輯 ---

# 輸入欄位（yfinance 抓取台股通常需要 .TW 結尾）
stock_code = st.text_input("請輸入股票或 ETF 代號", "0050.TW") 

if st.button("📈 開始分析") and stock_code:
    
    # 檢查並確保代號有 .TW 結尾
    stock_code_yf = stock_code.strip().upper()
    if not stock_code_yf.endswith(('.TW', '.TWO')):
         stock_code_yf += ".TW"
    
    # 3. STOCK DATA RETRIEVAL (yfinance)
    try:
        # Fetch data for charting (last 6 months)
        data = yf.download(stock_code_yf, period="6mo", progress=False)

        # 檢查並處理數據 (修正 KeyError 的關鍵)
        if not data.empty:
            # 將日期索引明確轉換為 'Date' 欄位，確保 Streamlit 辨識
            data = data.reset_index()
            data.rename(columns={'Date': 'Date'}, inplace=True) # 再次確認欄位名稱為 'Date'
        
        if data.empty:
            st.warning(f"⚠️ 無法取得 {stock_code_yf} 的歷史股價，可能代號有誤或資料不完整。")
            st.stop()
            
        # 4. GEMINI ANALYSIS 
        with st.spinner(f"AI 顧問正在分析 {stock_code_yf} ..."):
            # 傳遞給 Gemini 的提示詞
            # Prepare the prompt for Gemini
            current_price = float(data['Close'].iloc[-1])
            prompt = f"請詳細分析台股代號 {stock_code_yf}。當前最新收盤價是 {current_price:.2f}。所有分析務必以此價格為唯一基準進行評估。請遵循我們設定好的格式。"
            
            # 發送請求
            response = client.generate_content(prompt)
            
            # 顯示 AI 分析報告
            st.subheader(f"AI 分析報告 - {stock_code_yf}")
            st.markdown(response.text) 
            
    except Exception as e:
        st.error(f"分析時發生錯誤：請檢查代號是否正確。詳細錯誤: {e}")
        
# 5. CHART DISPLAY (約在 Line 91)
# 修正後的安全檢查語法：確保 data 存在且不為空
#if data is not None and not data.empty:
#   st.subheader("🗓 近六個月股價走勢")
#   st.line_chart(data, x='Date', y='Close')
# 頁腳
st.sidebar.markdown("---")
st.sidebar.caption(f"部署於 Streamlit Cloud | 由 Gemini API 提供支援")
