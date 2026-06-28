import streamlit as st
import pandas as pd
from pykakasi import kakasi

st.write("調整さんからcsvファイルをダウンロードし、それをアップロードしてください。")
uploaded_file = st.file_uploader("CSV", type="csv")


if uploaded_file:
    df = pd.read_csv(
        uploaded_file,
        header=2
    )

    names = list(df.columns[1:])  # 「日程」を除く
    kks = kakasi()

    names = sorted(
        names,
        key=lambda x: kks.convert(x)[0]["hira"]
    )

    #print(names)
    maisulist = list(i for i in range(1,26))

    person1 = st.selectbox("勝った人", names)
    person2 = st.selectbox("負けた人", names)
    maisu = st.selectbox("枚数差", maisulist)


    kks = kakasi()

    names = ["佐藤", "青木", "鈴木"]

    names = sorted(
        names,
        key=lambda x: kks.convert(x)[0]["hira"]
    )

    print(names)

    if st.button("記録"):
        st.write("正常に記録しました。")