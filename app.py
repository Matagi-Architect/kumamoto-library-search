import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import re # ハイフンを消すための正規表現バイ！

st.set_page_config(page_title="MTL 南稜高校図書館", layout="wide")

st.title("📚 MTL: Mattari Tosho-can Library")
st.write("「君の作戦、バックアップします。やりたいことがある君へ。」")

@st.cache_data
def load_data():
    file_name = 'Kumamoto_Library_Master_2026.csv'
    if not os.path.exists(file_name):
        st.error(f"エラー：{file_name} が見つからないバイ。")
        return None
    try:
        return pd.read_csv(file_name, encoding='cp932')
    except:
        return pd.read_csv(file_name, encoding='utf-8')

# 書影を取得する魔法（ハイフン除去対応版）
def get_book_cover(isbn_raw):
    if pd.isna(isbn_raw) or isbn_raw == "":
        return None
    
    # ハイフンを取り除いて数字だけにする魔法
    isbn_clean = re.sub(r'[-ー]', '', str(isbn_raw))
    
    # Open Library API（Googleより表紙が出やすい場合があるバイ）
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_clean}&format=json&jscmd=data"
    try:
        res = requests.get(url).json()
        key = f"ISBN:{isbn_clean}"
        if key in res and 'cover' in res[key]:
            return res[key]['cover']['medium']
    except:
        pass
    
    # Open Libraryで見つからなければGoogle Books APIへ
    url_g = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}"
    try:
        res_g = requests.get(url_g).json()
        return res_g['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    except:
        return None

df = load_data()

if df is not None:
    # データ整理（ジャンル分け）
    df['NDC_main'] = df['自校分類'].astype(str).str[0]
    ndc_labels = {'0':'0 総記','1':'1 哲学','2':'2 歴史','3':'3 社会科学','4':'4 自然科学',
                  '5':'5 技術','6':'6 産業','7':'7 芸術','8':'8 言語','9':'9 文学','E':'E 絵本'}
    df['ジャンル'] = df['NDC_main'].map(ndc_labels).fillna('その他')

    col1, col2 = st.columns([1, 1.2])

    with col2:
        st.subheader("📊 蔵書の健康診断")
        fig = px.pie(df, names='ジャンル', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textinfo='percent+label', hovertemplate='%{label}<br>%{value}冊')
        
        # グラフクリックを検知
        selected_genre = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        clicked_label = None
        if selected_genre and "selection" in selected_genre and "points" in selected_genre["selection"]:
             if len(selected_genre["selection"]["points"]) > 0:
                 clicked_label = selected_genre["selection"]["points"][0]["label"]

    with col1:
        st.subheader("🔍 MTL 蔵書検索")
        initial_query = clicked_label if clicked_label else ""
        search_query = st.text_input("キーワード入力 / グラフから選択", value=initial_query)

        if search_query:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            result = df[mask].head(30) # 30件まで表示
            
            st.write(f"検索結果: {len(df[mask])} 件（上位30件を表示）")
            
            for i, row in result.iterrows():
                with st.expander(f"📖 {row['書名']} ({row.get('著者名', '不明')})"):
                    c1, c2 = st.columns([1, 2])
                    # ISBN13を優先、なければISBNを使う
                    isbn_to_use = row.get('ISBN13') if pd.notna(row.get('ISBN13')) else row.get('ISBN')
                    
                    cover_url = get_book_cover(isbn_to_use)
                    if cover_url:
                        c1.image(cover_url)
                    else:
                        c1.image("https://via.placeholder.com/128x192.png?text=No+Image")
                    
                    c2.write(f"**分類:** {row['自校分類']} / {row['ジャンル']}")
                    c2.write(f"**ISBN13:** {row.get('ISBN13', 'なし')}")
                    c2.write(f"**配架場所:** {row.get('配架場所', '不明')}")
