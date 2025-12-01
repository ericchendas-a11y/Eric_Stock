import streamlit as st
from google.generativeai import GenerativeModel # <<< 修正 Line 2
import yfinance as yf
import pandas as pd
import datetime

# --- 1. CONFIGURATION AND INITIALIZATION ---

# 設置 Streamlit 網頁標題與排版
st.set_page_config(page_title="台股 AI 投資儀表板", layout="wide")
# ... (中間省略部分程式碼)

# 嘗試從 Streamlit Secrets 讀取密鑰並初始化 Gemini 客戶端
try:
    # 這是讀取您在 Streamlit Cloud 裡設定的密鑰
    api_key = st.secrets["GEMINI_API_KEY"] 
    
    # ... (SYSTEM_PROMPT 定義，此處省略)
    
    # 使用我們上次修正成功的模型來初始化 (不需要前面的 genai.)
    client = GenerativeModel('gemini-pro', system_instruction=SYSTEM_PROMPT) # <<< 修正這裡

except KeyError:
# ... (後續錯誤處理程式碼)

# --- 1. CONFIGURATION AND INITIALIZATION ---

# ... (程式碼在 Line 27-28 的 except 區塊結束)
    except Exception as e:
    # 這裡必須縮排
    st.error(f"❌ Gemini 初始化失敗，請檢查 API Key 或模型名稱: {e}")
    st.stop() 

# ----------------------------------------------------
# 以下程式碼必須是零縮排，靠左對齊！
# ----------------------------------------------------

st.set_page_config(page_title="台股 AI 投資儀表板", layout="wide") # <<< Line 29: 必須靠最左邊
st.title("📊 台股 AI 投資顧問")                                 # 必須靠最左邊
st.caption("輸入台股代號 (例如：2330, 0050) 進行分析與歷史走勢圖查看。") # 必須靠最左邊

# ... (後續的 if st.button 判斷式也必須靠最左邊)

# System Instruction (AI 的大腦/人設)
SYSTEM_PROMPT = """你是一位專業、客觀且數據導向的「台股投資分析助理」。你的任務是協助使用者快速分析台灣上市櫃股票與 ETF。
回答須精簡扼要，並固定以【📊 股票/ETF 名稱 (代號)】、【💰 核心數據觀察】、【📈 優勢與機會】、【⚠️ 風險與隱憂】、【💡 分析師短評】的結構輸出。
請使用繁體中文。
免責聲明：本分析僅供參考，不代表投資建議，投資前請審慎評估。
"""

# 嘗試從 Streamlit Secrets 讀取密鑰並初始化 Gemini 客戶端
try:
    # 這是讀取您在 Streamlit Cloud 裡設定的密鑰
    api_key = st.secrets["GEMINI_API_KEY"] 
    # 使用我們上次修正成功的 gemini-pro 模型
    client = genai.GenerativeModel('gemini-pro', system_instruction=SYSTEM_PROMPT)
except KeyError:
    # 提示使用者設定密鑰
    st.error("❌ 錯誤：找不到 Gemini API 密鑰。請檢查 Streamlit Cloud 的 Secrets 設定。")
    st.stop() # 停止執行，避免錯誤
except Exception as e:
    # 處理其他初始化錯誤
    st.error(f"❌ Gemini 初始化失敗，請檢查 API Key 或模型名稱: {e}")
    st.stop()


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
        # 下載近六個月的股價資料
        data = yf.download(stock_code_yf, period="6mo", progress=False)
        
        if data.empty:
            st.warning(f"⚠️ 無法取得 {stock_code_yf} 的歷史股價，請檢查代號是否正確。")
            st.stop()
            
        # 4. GEMINI ANALYSIS 
        with st.spinner(f"AI 顧問正在分析 {stock_code_yf} ..."):
            # 傳遞給 Gemini 的提示詞
            prompt = f"請詳細分析台股代號 {stock_code_yf} (收盤價: {data['Close'].iloc[-1]:.2f}) 目前的投資價值、風險與機會。請遵循我們設定好的格式。"
            
            # 發送請求
            response = client.generate_content(prompt)
            
            # 顯示 AI 分析報告
            st.subheader(f"AI 分析報告 - {stock_code_yf}")
            st.markdown(response.text) 
            
    except Exception as e:
        st.error(f"分析時發生錯誤：請檢查代號是否正確。詳細錯誤: {e}")
        
    # 5. CHART DISPLAY
    if not data.empty:
        st.subheader("🗓 近六個月股價走勢")
        st.line_chart(data['Close'])

# 頁腳
st.sidebar.markdown("---")
st.sidebar.caption(f"部署於 Streamlit Cloud | 由 Gemini API 提供支援")
