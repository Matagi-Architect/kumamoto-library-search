import streamlit as st
import pandas as pd
import os

# ページの設定
st.set_page_config(page_title="熊本県立高校 全県横断検索", layout="wide")

st.title("🚀 熊本県立高校 全県横断検索プロトタイプ")
st.write("GitHub + Streamlit Cloud で 24時間稼働中！")

# データの読み込み
@st.cache_data
def load_data():
    # Excelを読み込むための道具(openpyxl)が足りないと言われないよう、engineを指定
    file_name = 'Kumamoto_Library_Master_2026.xlsx'
    
    # ファイルが存在するか確認
    if not os.path.exists(file_name):
        st.error(f"エラー：{file_name} が見つからないバイ。GitHubに同じ名前でアップされているか確認してね。")
        return None
        
    # engine='openpyxl' を指定して読み込む
    return pd.read_excel(file_name, engine='openpyxl')

try:
    df = load_data()

    if df is not None:
        # 検索窓
        search_query = st.text_input("本の大まかな名前やキーワードを入れてね（例：夏目漱石、AI）")

        if search_query:
            # 全カラムを対象に検索（大文字小文字を区別しない）
            mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            result = df[mask]
            
            st.write(f"🔍 '{search_query}' の検索結果: {len(result)} 件見つかったバイ！")
            st.dataframe(result)
        else:
            st.write("↑ 上のボックスに文字を入れると、全県の蔵書から一瞬で探し出すバイ。")

except Exception as e:
    st.error(f"何かがおかしいバイ：{e}")
