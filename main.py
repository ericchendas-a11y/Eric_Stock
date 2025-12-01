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
