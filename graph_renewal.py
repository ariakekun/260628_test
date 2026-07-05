import streamlit as st
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime
from supabase import create_client
from matplotlib import font_manager

# フォント設定
font_path = "fonts/ipaexg.ttf"
font_manager.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "IPAexGothic"


# アプリ開始
st.title("練習記録確認アプリ")

tab1, tab2, tab3 = st.tabs(["会員試合数", "対戦履歴", "各人データ"])

## データの読み込み

# supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 試合記録
match_record = []
startnumber = 0
step = 1000

while True:
    res = (
        supabase.table("match_record")
        .select("*")
        .range(startnumber, startnumber + step - 1)
        .execute()
    )

    batch = res.data

    if not batch:
        break

    match_record.extend(batch)
    startnumber += step


# st.write(len(match_record))

# 漣メンバー

member = (
    supabase
    .table("namelist_sazanami")
    .select("*")
    .execute()
)

## 各ページの表示を作る
# 1ページ目
# 会員の試合数をグラフで表示する


# 現在の年を取得
current_year = datetime.datetime.now().year
# 2024年から現在までのリスト
year_list = list(i for i in range(2024, current_year+1))

with tab1:
    # Streamlitのセレクトボックスで年を選択
    selected_year = st.selectbox('年を選択', year_list, index=year_list.index(current_year))

    # 選択した年に対応するデータをフィルタリング
    filtered_record = [i for i in match_record if int(i["date"].split("-")[0]) == selected_year]
    
    # メンバーごとに名前が何回出てくるかを数えて辞書（名前と試合数）にする
    n_match_dict = []
    for i in member.data:
        person_record = [j for j in filtered_record if (j["winner"] == i["name"]) or (j["loser"] == i["name"])]
        name = i["name"]
        n_match = len(person_record)
        n_match_dict.append({
            "name": name,
            "n_match": n_match
        })
    
    #st.write(n_match_dict)

    
    # 棒グラフを作る

    # 試合数が多い順に並び替える
    sorted_n_match = sorted(
        n_match_dict,
        key = lambda x: x["n_match"],
        reverse = True
    )

    # 名前と試合数を辞書から取り出す
    names = [i["name"] for i in n_match_dict]
    n_matches = [i["n_match"] for i in n_match_dict]

    height = len(member.data)*0.5
    fig, ax = plt.subplots(figsize=(10,height))
    
    # 横棒グラフを描く
    bars = ax.barh(names, n_matches)
    ax.invert_yaxis()

    # ラベルの設定
    ax.set_xlabel("試合数")
    #ax.set_ylabel("名前")
    ax.set_title("会員試合数")

    # 目盛の設定
    ax.xaxis.set_ticks_position('bottom')
    ax2 = ax.twiny()  # 上に追加のx軸を作成
    ax2.xaxis.set_ticks_position('top')  # 上に目盛りを設定
    ax2.set_xlim(ax.get_xlim())  # 上側のx軸を下側のx軸と一致させる
    ax.grid(True, axis='x', linestyle='--', alpha=0.6)  # x軸方向にグリッド線を引く

    
    st.pyplot(fig)

    sorted_n_match_df = pd.DataFrame(sorted_n_match)
    sorted_n_match_df.columns = ["名前","試合数"]

    st.write(sorted_n_match_df)


# 2ページ目（対戦履歴表示）
with tab2:
    # 入力欄
    p1 = st.text_input("対戦履歴を知りたい人の名前を漢字（空白なし）で入力してください。")
    p2 = st.text_input("相手の名前を漢字（空白なし）で入力してください。")

    # ボタンが押されたら
    if st.button("対戦履歴を表示"):
        # まずp1で辞書をfilterする
        p1_record = [i for i in match_record if i["winner"] == p1 or i["loser"] == p1]
        # 次にp2で辞書をfilterする
        p1_and_p2_record = [i for i in p1_record if i["winner"] == p2 or i["loser"] == p2]
        # 日付、勝敗、枚数 の辞書を作る
        new_p1p2_record = []
        for i in p1_and_p2_record:
            date = i["date"]
            if p1 == i["winner"]:
                result = "○"
            else:
                result = "×"
            score = i["score(maisusa)"]
            new_p1p2_record.append({
                "date":date,
                "result":result,
                "score":score
            })
        result = pd.DataFrame(new_p1p2_record)
        result.columns = ["日付", "勝敗", "枚数差"]
        st.write(result)

# 3ページ目（各人データ）
with tab3:
    person = st.text_input("調べたい人の名前を漢字（空白なし）で入力してください。")

    # 表示期間の設定
    min_date = datetime.date(2024, 1, 1)
    max_date = datetime.date.today()
    date_result = st.slider('表示期間を指定してください。', value=(min_date, max_date), format='YYYY-MM-DD', min_value=min_date, max_value=max_date)
    st.write('開始日は：', date_result[0])
    st.write('終了日は：', date_result[1])


    if st.button("表示"):
        # 入力内容から辞書をフィルター
        # 入力期間でフィルター
        start = date_result[0]
        end = date_result[1]
        filtered_by_date = [
            i for i in match_record
            if start <= datetime.datetime.strptime(i["date"], "%Y-%m-%d").date() <= end
        ]
        # 人でフィルター
        filtered_by_date_and_person = [
            i for i in filtered_by_date
            if i["winner"] == person
            or i["loser"] == person]
        
        
        ################ 月毎の積み上げ棒グラフを作る ###################
        # 月の一覧を作る
        start_month = pd.Timestamp(start).replace(day=1) 
        end_month = pd.Timestamp(end).replace(day=1)

        months = pd.date_range(
            start = start_month,
            end = end_month,
            freq = "MS" # Month
        ).strftime("%Y-%m")
        
        # フィルターしたデータから月ごとに試合数を集計する（試合した月のみ）
        df_filtered_tab3 = pd.DataFrame(filtered_by_date_and_person)
        df_filtered_tab3["date"] = pd.to_datetime(df_filtered_tab3["date"])
        df_filtered_tab3["month"] = df_filtered_tab3["date"].dt.strftime("%Y-%m")
        monthly = df_filtered_tab3.groupby("month").size().reindex(months, fill_value=0)
        
        # 累計
        cumulative = monthly.cumsum()

        # グラフ
        fig, ax = plt.subplots()

        ax.plot(cumulative.index, cumulative.values, ".-")

        ax.set_title("累計試合数")

        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig)

        ################ 勝敗数と勝率 ################
        win = 0
        lose = 0
        for i in filtered_by_date_and_person:
            if i["winner"] == person:
                win += 1
            else:
                lose += 1
        win_rate = (win/(win+lose))
        st.subheader("指定した期間の勝率：%.3f" %(win_rate))
        st.subheader("%d勝%d敗" %(win, lose))

        ################ 試合記録の表示 ################

        filtered_by_date_and_person_for_display = []
        for i in filtered_by_date_and_person:
            date = i["date"]
            score = i["score(maisusa)"]
            if i["winner"] == person:
                result_tab3 = "○"
                opponent = i["loser"]
            else:
                result_tab3 = "×"
                opponent = i["winner"]
            filtered_by_date_and_person_for_display.append({
                "date":date,
                "result":result_tab3,
                "score":score,
                "opponent":opponent
            })
        filtered_by_date_and_person_for_display_df = pd.DataFrame(filtered_by_date_and_person_for_display)
        st.write(filtered_by_date_and_person_for_display_df)


