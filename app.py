import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. ページの設定：MTL専用のタイトル
st.set_page_config(page_title="MTL 南稜高校図書館 検索アプリ", layout="wide")

st.title("📚 Welcome to MTL: Mattari Tosho-can Library")
st.subheader("南稜高校図書館 蔵書検索 & 虹色診断")
st.write("「君の作戦、バックアップします。やりたいことがある君へ。」")

# 2. データの読み込み（CSV対応版バイ！）
@st.cache_data
def load_data():
    # ファイル名をCSVに変更
    file_name = 'Kumamoto_Library_Master_2026.csv' 
    if not os.path.exists(file_name):
        st.error(f"エラー：{file_name} が見つからないバイ。GitHubにアップしてね！")
        return None
    
    # 日本語の文字化けを防ぐために、2パターンの読み込みを試すバイ
    try:
        # まずは一般的なShift-JIS（Excelで作ったCSVは大体これ）
        return pd.read_csv(file_name, encoding='cp932')
    except:
        # ダメならUTF-8（MacやGoogleで作ったCSV）
        return pd.read_csv(file_name, encoding='utf-8')

# ここでデータを読み込む（この1行は絶対必要バイ！）
df = load_data()

if df is not None:
    # --- 虹色のためのデータ整理 ---
    # 自校分類（NDC）の先頭1桁を抽出。E（絵本）なども文字列として扱う
    df['NDC_main'] = df['自校分類'].astype(str).str[0]
    
    ndc_labels = {
        '0': '0 総記', '1': '1 哲学', '2': '2 歴史', '3': '3 社会科学',
        '4': '4 自然科学', '5': '5 技術', '6': '6 産業', '7': '7 芸術',
        '8': '8 言語', '9': '9 文学', 'E': 'E 絵本'
    }
    df['ジャンル'] = df['NDC_main'].map(ndc_labels).fillna('その他')

    # --- 画面を左右に分割 ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🔍 蔵書を検索")
        search_query = st.text_input("本の大まかな名前やキーワードを入力")
        
        if search_query:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            result = df[mask]
            st.success(f"🔍 '{search_query}' の結果: {len(result)} 件見つかったバイ！")
            st.dataframe(result)
        else:
            st.info("キーワードを入れると、一瞬で探し出すバイ。")

    with col2:
        st.markdown("### 🌈 MTL 蔵書構成（虹色診断）")
        # 虹色の円グラフ（ドーナツ型）
        fig = px.pie(df, names='ジャンル', 
                     hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

# 3. 西川監督へのメッセージ
st.divider()
st.caption("Est. 2023 / Re-mix 2025 - MTL Digital Project / 企画・設計：西川監督")
