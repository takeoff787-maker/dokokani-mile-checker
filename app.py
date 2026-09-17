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
    
    st.subheader("🚗 車両条件（タイムズカー）")
    times_car_models = st.multiselect(
        "希望車種",
        ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア"],
        default=["C-HR", "CX-30", "MAZDA3", "ヤリスクロス"]
    )
    
    search_btn = st.button("🔍 条件に合う候補地を一括確認", type="primary")

# --- 空港＆店舗情報データベース ---
AIRPORT_DB = [
    {"code": "CTS", "name": "新千歳空港", "region": "北海道", "type": "times", "keyword": "新千歳空港"},
    {"code": "HKD", "name": "函館空港", "region": "北海道", "type": "times", "keyword": "函館空港"},
    {"code": "AOJ", "name": "青森空港", "region": "東北", "type": "rental", "keyword": "青森空港"},
    {"code": "KMQ", "name": "小松空港", "region": "北陸", "type": "times", "keyword": "小松空港"},
    {"code": "HIJ", "name": "広島空港", "region": "中国", "type": "times", "keyword": "広島空港"},
    {"code": "TKM", "name": "高松空港", "region": "四国", "type": "times", "keyword": "高松空港"},
    {"code": "MYJ", "name": "松山空港", "region": "四国", "type": "times", "keyword": "松山空港"},
    {"code": "FUK", "name": "福岡空港", "region": "九州", "type": "times", "keyword": "福岡空港"},
    {"code": "KOJ", "name": "鹿児島空港", "region": "九州", "type": "times", "keyword": "鹿児島空港"}
]

if search_btn or True:
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)
    
    st.success(f"📅 【設定日時】{start_dt.strftime('%Y/%m/%d %H:%M')} 〜 {end_dt.strftime('%m/%d %H:%M')}")
    st.write("各空港の条件を確認してください。ボタンを押すとそれぞれの公式予約・確認画面が開きます。")
    
    for ap in AIRPORT_DB:
        with st.expander(f"✈️ 【{ap['name']} ({ap['code']})】 - {ap['region']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🚗 車移動（タイムズ / レンタカー）**")
                if ap["type"] == "times":
                    st.write(f"タイムズカー {ap['name']}周辺エリア")
                    # スマホ対応のステーション一覧検索URL（空港周辺の全ステーションを表示）
                    times_url = f"https://share.timescar.jp/sp/view/station/list.jsp?keyword={ap['keyword']}"
                    st.link_button("📲 周辺の全ステーション・空車一覧へ", times_url)
                else:
                    st.warning("タイムズ非対応エリア")
                    st.link_button("📲 dカーシェア / レンタカー検索", "https://dcarshare.docomo.ne.jp/")

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
