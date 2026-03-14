import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

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
        # ExcelからのCSVはcp932(Shift-JIS)が多いバイ
        return pd.read_csv(file_name, encoding='cp932')
    except:
        return pd.read_csv(file_name, encoding='utf-8')

# --- 版元ドットコムの画像URLを生成する魔法 ---
def get_hanmoto_url(isbn_raw):
    if pd.isna(isbn_raw) or isbn_raw == "":
        return None
    # ハイフンを抜いて数字13桁だけにする
    isbn_clean = re.sub(r'[-ー]', '', str(isbn_raw))
    if len(isbn_clean) == 13:
        # 版元ドットコムの画像サーバーのルールに従うバイ
        return f"https://www.hanmoto.com/bd/img/{isbn_clean}.jpg"
    return None

df = load_data()

if df is not None:
    # データ整理
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
            # 無敵モードの検索
            mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            result = df[mask].head(100) # 100件に絞ると表示が早くなるバイ！
            
            st.write(f"検索結果: {len(df[mask])} 件（上位100件を表示）")
            
            for i, row in result.iterrows():
                # 本の名前と著者名を並べて表示
                title = row.get('書名', '無題')
                author = row.get('著者', '不明')
                
                with st.expander(f"📖 {title} （{author}）"):
                    c1, c2 = st.columns([1, 2])
                    
                    # 版元ドットコムのURLを生成
                    isbn13 = row.get('ISBN13')
                    cover_url = get_hanmoto_url(isbn13)
                    
                    if cover_url:
                        # 読み込みエラーを無視して表示を試みるバイ
                        c1.image(cover_url, use_container_width=True)
                    else:
                        c1.info("No Cover")
                    
                    c2.write(f"**分類:** {row['自校分類']} / {row['ジャンル']}")
                    c2.write(f"**所在:** {row.get('出版年', '不明')}")
                    c2.write(f"**ISBN13:** {row.get('ISBN13', 'なし')}")
