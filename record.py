import streamlit as st
import pandas as pd
from pykakasi import kakasi
from supabase import create_client


url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)


# 調整さんアップロード
st.write("調整さんからcsvファイルをダウンロードし、それをアップロードしてください。")
uploaded_file = st.file_uploader("CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(
        uploaded_file,
        header=2
    )

    names = list(df.columns[1:])  # 「日程」を除く
    kks = kakasi()

    # リストをあいうえお順に並び替え
    names = sorted(
        names,
        key=lambda x: kks.convert(x)[0]["hira"]
    )

    # リストに「その他」を追加
    names.append("その他")

    # 入力させる
    maisulist = list(i for i in range(1,26))

    person1 = st.selectbox("勝った人", names)
    if person1 == "その他":
        person1 = st.text_input("名前を入力してください", key="name1")
    person2 = st.selectbox("負けた人", names)
    if person2 == "その他":
        person2 = st.text_input("名前を入力してください", key="name2")
    maisu = st.selectbox("枚数差", maisulist)
    match_date = st.date_input("試合日")

    # 登録
    if st.button("記録"):
        if person1 == person2:
            st.write("登録できません。")
        else:
            supabase.table("match_record").insert({
                "date":match_date.isoformat(),
                "winner":person1,
                "loser":person2,
                "score(maisusa)":maisu
            }).execute()
            st.write("正常に記録しました。")

