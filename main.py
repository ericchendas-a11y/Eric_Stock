import streamlit as st
from google.generativeai import GenerativeModel
import yfinance as yf
import pandas as pd
import datetime

# --- 1. CONFIGURATION AND INITIALIZATION ---

# 設定 Streamlit 網頁標題與排版 (必須是零縮排)
st.set_page_config(page_title="台股 AI 投資儀表板", layout="wide")
st.title("📊 台股 AI 投資顧問")
st.caption("輸入台股代號 (例如：2330.TW, 0050.TW) 進行深度分析。")

# 初始化 data 變數，避免 NameError
data = None

# System Instruction (AI 的大腦/人設 - 整合主動比較邏輯)
SYSTEM_PROMPT = """你是一位專業、客觀且數據導向的「台股投資分析助理」。你的任務是協助使用者快速分析台灣上市櫃股票與 ETF。
請絕對嚴格遵守以下規則：
1. 數據來源：所有分析必須獨家使用使用者提供的「當前收盤價」，嚴禁對該價格的正確性或歷史數據進行評論、質疑或警告。
2. 分析核心：你的職責是基於該價格計算和評估，不要顯示任何關於「價格過時」或「價格錯誤」的警告。
3. 新增任務：在完成主要分析報告後，你必須主動從市場中挑選 2 檔與主要標的（股票或 ETF）類型最相似、最具競爭力的標的，並針對這 3 檔標的進行一次綜合比較分析。
4. 格式要求：
    * 第一部分：必須以【📊...】、【💰...】、【📈...】、【⚠️...】、【💡...】的結構輸出主要標的的分析報告。
    * 第二部分：必須在第一部分結束後，獨立標註 【🆚 競爭標的綜合比較】 作為標題。內容需包含一張表格，比較 3 檔標的。對於主要標的，使用提供的最新收盤價；**對於挑選的 2 檔比較標的，必須利用你的即時搜索功能查出其最新的收盤價**，然後進行分析比較（比較類型、規模、費用率、近一年績效、和當前股價）。
請使用繁體中文。
免責聲明：本分析僅供參考，不代表投資建議，投資前請審慎評估。
"""

# 嘗試從 Streamlit Secrets 讀取密鑰並初始化 Gemini 客戶端
try:
    api_key = st.secrets["GEMINI_API_KEY"] 
    # 使用 gemini-2.5-flash，這是我們最終確認可用的模型名稱
    client = GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

except KeyError:
    st.error("❌ 錯誤：找不到 Gemini API 密鑰。請檢查 Streamlit Cloud 的 Secrets 設定。")
    st.stop()
except Exception as e:
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
        # Fetch data for charting (last 1 year) - Changed from 6mo to 1y
        data = yf.download(stock_code_yf, period="1y", progress=False)

        # 檢查數據是否為空
        if data.empty:
            st.warning(f"⚠️ 無法取得 {stock_code_yf} 的歷史股價，可能代號有誤或資料不完整。")
            st.stop()

        # ----------------------------------------------------
        # CHARTING AND STATS LOGIC (Re-added)
        # ----------------------------------------------------
        
        # 確保 'Close' 是浮點數，用於計算
        price_data = data['Close'].astype(float)
        
        # 計算統計數據
        max_price = round(price_data.max(), 2) # <<< 修正：使用 round() 強制轉換為純 Python float
        min_price = round(price_data.min(), 2) # <<< 修正：使用 round() 強制轉換為純 Python float
        avg_price = round(price_data.mean(), 2) # <<< 修正：使用 round() 強制轉換為純 Python float

        st.markdown("---")
        st.subheader("🗓 近一年股價走勢與統計")
        
        # 顯示統計 Metric
        col_max, col_min, col_avg = st.columns(3)
        col_max.metric("📈 最高價", f"{max_price:.2f} TWD")
        col_min.metric("📉 最低價", f"{min_price:.2f} TWD")
        col_avg.metric("💲 平均價", f"{avg_price:.2f} TWD")
        
        # 準備繪圖數據 (將日期索引轉換為欄位，解決先前 KeyError)
        data_for_chart = data.reset_index()
        data_for_chart.rename(columns={'Date': 'Date'}, inplace=True) # 確保欄位名稱為 'Date'

        # 繪製曲線圖
        st.line_chart(data_for_chart, x='Date', y='Close', use_container_width=True)
        st.markdown("---") # 分隔線
        
        # ----------------------------------------------------
        
        # 4. GEMINI ANALYSIS 
        with st.spinner(f"AI 顧問正在分析 {stock_code_yf} 並尋找競爭標的..."):
            
            # 傳遞給 Gemini 的提示詞 (修正 float 轉換問題)
            # 這裡的 current_price 也必須確保是 float
            current_price = float(data['Close'].iloc[-1]) 
            prompt = f"請詳細分析台股代號 {stock_code_yf}。當前最新收盤價是 {current_price:.2f}。所有分析務必以此價格為唯一基準進行評估。請遵循我們設定好的格式，並執行比較任務。"
            
            # 發送請求 - AI 會在這次呼叫中完成主要分析和比較兩項任務
            response = client.generate_content(prompt)
            
            # 顯示 AI 分析報告（包含報告和比較兩部分）
            st.subheader(f"AI 深度分析 - {stock_code_yf}")
            st.markdown(response.text)
            
    except Exception as e:
        # 捕獲 yfinance 或 API 呼叫錯誤
        st.error(f"分析時發生錯誤：請檢查代號是否正確。詳細錯誤: {e}")


# 頁腳區塊 (Footer) - 必須在所有 if/try 之外，零縮排執行
st.sidebar.markdown("---")
st.sidebar.caption(f"部署於 Streamlit Cloud | 由 Gemini API 提供支援")
