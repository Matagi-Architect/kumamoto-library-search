import streamlit as st
import pandas as pd

# 1. データの読み込み（君が作ったあのExcelを指定）
@st.cache_data
def load_data():
    # パスは君のドライブの状況に合わせて調整してくれ
    df = pd.read_excel('/content/drive/MyDrive/Kumamoto_Library_Master_2026.xlsx')
    return df

st.title("🚀 熊本県立高校 全県横断検索プロトタイプ")
st.write("「ZIP配布」から「Web共有」へ。情報のマタギ・西川による実装。")

df = load_data()

# 2. 検索窓の設置
query = st.text_input("本、著者、または学校名を入力してくれ", "")

# 3. 検索ロジック（さっきの find_book をWeb用にリミックス）
if query:
    # 大文字小文字を区別せず、部分一致で検索
    mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)
    result = df[mask]

    st.write(f"🔍 {len(result)} 件の「知」が見つかったぞ。")
    st.dataframe(result) # きれいな表で表示
else:
    st.write("検索ワードを待っている...")
