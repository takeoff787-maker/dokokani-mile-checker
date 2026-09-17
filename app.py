import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="どこかにマイル 条件クリア空港 判定アプリ", page_icon="✈️", layout="wide")
st.title("✈️ どこかにマイル 条件クリア空港 判定アプリ")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 検索条件")
    default_start = datetime.now() + timedelta(days=4)
    start_date = st.date_input("出発日", default_start)
    start_time = st.time_input("出発時間", datetime.strptime("09:00", "%H:%M").time())
    
    end_date = st.date_input("帰着日", default_start + timedelta(days=1))
    end_time = st.time_input("帰着時間", datetime.strptime("18:00", "%H:%M").time())
    
    st.subheader("🚗 車両条件（タイムズカー希望車種）")
    times_car_models = st.multiselect(
        "希望車種（一次判定用）",
        ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア", "ヴォクシー", "フィット/ヤリス等"],
        default=["C-HR", "CX-30", "MAZDA3", "ヤリスクロス"]
    )
    
    search_btn = st.button("🔍 条件に合う候補地を一括確認", type="primary")

# --- 空港＆店舗情報データベース ---
AIRPORT_DB = [
    {
        "code": "CTS", "name": "新千歳空港", "region": "北海道", "type": "times",
        "models": ["C-HR", "CX-30", "ヤリスクロス", "ノア", "ヴォクシー", "フィット"],
        "note": "空港内および周辺ステーション複数あり。人気車種の配備数多め。"
    },
    {
        "code": "HKD", "name": "函館空港", "region": "北海道", "type": "times",
        "models": ["ヤリスクロス", "フィット", "ノート", "スイフト"],
        "note": "空港直結ステーションあり。SUV枠はヤリスクロス中心。"
    },
    {
        "code": "AOJ", "name": "青森空港", "region": "東北", "type": "rental",
        "models": ["タイムズカー非対応（レンタカー店舗あり）"],
        "note": "⚠️ タイムズカーシェアのステーションはありません。dカーシェアやタイムズカーレンタルをご利用ください。"
    },
    {
        "code": "KMQ", "name": "小松空港", "region": "北陸", "type": "times",
        "models": ["CX-30", "ヤリスクロス", "フィット", "ソリオ"],
        "note": "小松空港駐車場ステーションあり。"
    },
    {
        "code": "HIJ", "name": "広島空港", "region": "中国", "type": "times",
        "models": ["MAZDA3", "CX-30", "ヤリスクロス", "ノア"],
        "note": "広島空港前ステーションあり。マツダ車（MAZDA3, CX-30）の配備多数。"
    },
    {
        "code": "TKM", "name": "高松空港", "region": "四国", "type": "times",
        "models": ["ヤリスクロス", "フィット", "ノート"],
        "note": "高松空港前ステーションあり。"
    },
    {
        "code": "MYJ", "name": "松山空港", "region": "四国", "type": "times",
        "models": ["CX-30", "ヤリスクロス", "フィット"],
        "note": "松山空港周辺ステーションあり。"
    },
    {
        "code": "FUK", "name": "福岡空港", "region": "九州", "type": "times",
        "models": ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア", "ヴォクシー"],
        "note": "国内線/国際線周辺に複数ステーションあり。車種豊富。"
    },
    {
        "code": "KOJ", "name": "鹿児島空港", "region": "九州", "type": "times",
        "models": ["ヤリスクロス", "フィット", "ノート", "ソリオ"],
        "note": "鹿児島空港前ステーションあり。"
    }
]

if search_btn or True:
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)
    
    st.success(f"📅 【設定日時】{start_dt.strftime('%Y/%m/%d %H:%M')} 〜 {end_dt.strftime('%m/%d %H:%M')}")
    
    # ----------------------------------------------------
    # 最上部：条件クリア一括判定サマリー（チェックボックス一覧）
    # ----------------------------------------------------
    st.markdown("### 📊 条件クリア空港 一覧（判定サマリー）")
    st.caption("希望車種の配備状況に基づく自動チェックです。手動確認結果に合わせてチェックを変更できます。")

    cleared_states = {}
    
    # 2列に分けて一覧表示
    col_a, col_b = st.columns(2)
    for idx, ap in enumerate(AIRPORT_DB):
        matched_models = [m for m in times_car_models if m in ap["models"]]
        has_match = len(matched_models) > 0
        
        status_label = f"🟢 {ap['name']} ({ap['code']}) - {', '.join(matched_models) if has_match else '希望車種なし'}"
        if ap["type"] == "rental":
            status_label = f"🔴 {ap['name']} ({ap['code']}) - カーシェア非対応"

        target_col = col_a if idx % 2 == 0 else col_b
        with target_col:
            # 初期値は「希望車種があるかどうか」で自動設定
            cleared_states[ap['code']] = st.checkbox(status_label, value=has_match, key=f"chk_{ap['code']}")

    st.divider()

    # ----------------------------------------------------
    # 下部：各空港の詳細＆リンク確認エリア
    # ----------------------------------------------------
    st.markdown("### 📲 各空港の詳細・照会リンク")

    for ap in AIRPORT_DB:
        is_checked = cleared_states[ap['code']]
        matched_models = [m for m in times_car_models if m in ap["models"]]
        has_match = len(matched_models) > 0
        
        header_icon = "✅" if is_checked else "⚪"
        
        with st.expander(f"{header_icon} 【{ap['name']} ({ap['code']})】 - {ap['region']}", expanded=is_checked):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🚗 車両・配備ステーション情報**")
                st.caption(ap["note"])
                
                if ap["type"] == "times":
                    st.write("**【配備されている主な車種】**")
                    st.write(", ".join(ap["models"]))
                    
                    if has_match:
                        st.success(f"希望一致: {', '.join(matched_models)}")
                    else:
                        st.warning("指定された希望車種の配備が少ない/ありません")
                    
                    st.markdown("---")
                    mypage_url = "https://share.timescar.jp/view/sp/member/mypage.jsp"
                    st.link_button("📲 タイムズカー マイページ（空車照会）へ", mypage_url)
                    st.caption("※マイページの「ステーション検索」で「" + ap['name'] + "」を入力")
                else:
                    st.error("タイムズカーシェアのステーションはありません")
                    st.write("**【代替手段】**")
                    st.link_button("📲 dカーシェアで空車検索", "https://dcarshare.docomo.ne.jp/")
                    st.link_button("📲 タイムズカーレンタル（公式）", "https://rental.timescar.jp/")

            with col2:
                st.markdown("**🏨 温泉＆バイキング宿**")
                st.write("1泊2食付き 予算1〜2万円台")
                jalan_url = f"https://www.jalan.net/uw/uwp3000/uwp3001.do?keyword={ap['name']}+温泉+バイキング"
                st.link_button("📲 じゃらんで空室・プラン確認", jalan_url)

            with col3:
                st.markdown("**🌤 現地天気**")
                st.write("出発前の天気予報確認")
                tenki_url = f"https://tenki.jp/search/?keyword={ap['name']}"
                st.link_button("📲 天気予報を確認", tenki_url)
