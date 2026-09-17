import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="どこかにマイル 条件クリア空港 判定アプリ", page_icon="✈️", layout="wide")

# スマホ画面でも強制的に3列表示を維持するCSS
st.markdown("""
    <style>
    [data-testid="column"] {
        min-width: 30% !important;
    }
    div.stCheckbox > label {
        font-size: 13px !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ どこかにマイル 条件クリア空港 判定アプリ")

if "custom_hotels" not in st.session_state:
    st.session_state.custom_hotels = {}

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 初期設定・基本条件")
    num_people = st.number_input("利用人数（名）", min_value=1, max_value=6, value=1, step=1)
    trip_type = st.radio("旅行スタイル", ["1泊2日", "2泊3日", "日帰り"], index=0)
    
    default_start = datetime.now() + timedelta(days=4)
    start_date = st.date_input("出発日", default_start)
    start_time = st.time_input("出発時間", datetime.strptime("09:00", "%H:%M").time())
    
    if trip_type == "日帰り":
        end_date = start_date
    elif trip_type == "1泊2日":
        end_date = start_date + timedelta(days=1)
    else:
        end_date = start_date + timedelta(days=2)
        
    end_time = st.time_input("帰着時間", datetime.strptime("18:00", "%H:%M").time())

# --- 空港データベース ---
AIRPORT_DB = [
    {"code": "CTS", "name": "新千歳", "type": "times", "stations": [{"name": "新千歳空港店（送迎）", "models": ["C-HR", "CX-30", "MAZDA3", "ノア", "ヴォクシー"]}, {"name": "新千歳空港A駐車場", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["定山渓万世閣", "登別万世閣"]},
    {"code": "HKD", "name": "函館", "type": "times", "stations": [{"name": "函館空港駐車場", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["湯の川温泉 ホテル万惣"]},
    {"code": "AKJ", "name": "旭川", "type": "times", "stations": [{"name": "旭川空港前店", "models": ["ヤリスクロス", "フィット", "ノア"]}], "fav_hotels": ["層雲峡観光ホテル"]},
    {"code": "MMB", "name": "女満別", "type": "times", "stations": [{"name": "女満別空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["網走観光ホテル"]},
    {"code": "OBO", "name": "帯広", "type": "times", "stations": [{"name": "帯広空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["十勝川温泉 第一ホテル"]},
    {"code": "KUH", "name": "釧路", "type": "times", "stations": [{"name": "釧路空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["阿寒湖温泉 あかん遊久の里鶴雅"]},
    {"code": "AOJ", "name": "青森", "type": "rental", "stations": [], "fav_hotels": ["浅虫温泉 宿屋つばき"]},
    {"code": "MSJ", "name": "三沢", "type": "rental", "stations": [], "fav_hotels": ["星野リゾート 青森屋"]},
    {"code": "AXT", "name": "秋田", "type": "times", "stations": [{"name": "秋田空港駐車場", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["男鹿温泉 ホテルきららか"]},
    {"code": "GAJ", "name": "山形", "type": "times", "stations": [{"name": "山形空港前", "models": ["フィット", "ヤリス"]}], "fav_hotels": ["蔵王温泉 高見屋"]},
    {"code": "HNA", "name": "花巻", "type": "times", "stations": [{"name": "花巻空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["花巻温泉 ホテル千秋閣"]},
    {"code": "KMQ", "name": "小松", "type": "times", "stations": [{"name": "小松空港第一駐車場", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["加賀温泉郷 瑠璃光"]},
    {"code": "OKJ", "name": "岡山", "type": "times", "stations": [{"name": "岡山空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["湯郷温泉 季譜の里"]},
    {"code": "HIJ", "name": "広島", "type": "times", "stations": [{"name": "広島空港前", "models": ["MAZDA3", "CX-30", "ヤリスクロス", "ノア"]}], "fav_hotels": ["宮島温泉 錦水館"]},
    {"code": "IZO", "name": "出雲", "type": "times", "stations": [{"name": "出雲空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["玉造温泉 佳翠苑皆美"]},
    {"code": "UBJ", "name": "山口宇部", "type": "times", "stations": [{"name": "山口宇部空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["湯田温泉 松田屋ホテル"]},
    {"code": "TKM", "name": "高松", "type": "times", "stations": [{"name": "高松空港前", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["琴平温泉 琴参閣"]},
    {"code": "MYJ", "name": "松山", "type": "times", "stations": [{"name": "松山空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["道後温泉 ふなや"]},
    {"code": "TKS", "name": "徳島", "type": "times", "stations": [{"name": "徳島空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["鳴門温泉 アオアヲナルトリゾート"]},
    {"code": "KCZ", "name": "高知", "type": "times", "stations": [{"name": "高知空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["城西館"]},
    {"code": "FUK", "name": "福岡", "type": "times", "stations": [{"name": "福岡空港国内線前", "models": ["C-HR", "CX-30", "MAZDA3", "ノア"]}, {"name": "福岡空港国際線前", "models": ["ヤリスクロス", "ヴォクシー", "フィット"]}], "fav_hotels": ["原鶴温泉 泰泉閣"]},
    {"code": "KKJ", "name": "北九州", "type": "times", "stations": [{"name": "北九州空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["ホテルクラウンパレス小倉"]},
    {"code": "OIT", "name": "大分", "type": "times", "stations": [{"name": "大分空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["別府温泉 杉乃井ホテル"]},
    {"code": "NGS", "name": "長崎", "type": "times", "stations": [{"name": "長崎空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["雲仙温泉 雲仙宮崎旅館"]},
    {"code": "KMJ", "name": "熊本", "type": "times", "stations": [{"name": "熊本空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["黒川温泉 ふじ屋"]},
    {"code": "KMI", "name": "宮崎", "type": "times", "stations": [{"name": "宮崎空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["シェラトン・グランデ"]},
    {"code": "KOJ", "name": "鹿児島", "type": "times", "stations": [{"name": "鹿児島空港前", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["霧島温泉 霧島ホテル"]},
    {"code": "OKA", "name": "那覇", "type": "times", "stations": [{"name": "那覇空港店（送迎あり）", "models": ["C-HR", "CX-30", "ヤリスクロス", "ノア", "ヴォクシー"]}], "fav_hotels": ["サザンビーチホテル"]},
    {"code": "MMY", "name": "宮古", "type": "times", "stations": [{"name": "宮古空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["シギラベイサイドスイート"]},
    {"code": "ISG", "name": "新石垣", "type": "times", "stations": [{"name": "石垣空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["フサキビーチリゾート"]}
]

start_dt = datetime.combine(start_date, start_time)
end_dt = datetime.combine(end_date, end_time)

st.success(f"📅 【設定条件】{num_people}名 | {trip_type} | {start_dt.strftime('%m/%d %H:%M')} 〜 {end_dt.strftime('%m/%d %H:%M')}")

# 各空港のチェック済み状態（ステータス）を事前に算出
def get_status_tag(ap):
    car_ok = False
    hotel_ok = True if trip_type == "日帰り" else False

    # 車両チェック確認
    for s_idx, st_info in enumerate(ap["stations"]):
        for m_idx, _ in enumerate(st_info["models"]):
            if st.session_state.get(f"car_chk_{ap['code']}_{s_idx}_{m_idx}", False):
                car_ok = True
                break

    # ホテルチェック確認
    if trip_type != "日帰り":
        for h_idx, _ in enumerate(ap["fav_hotels"]):
            if st.session_state.get(f"hotel_chk_{ap['code']}_{h_idx}", False):
                hotel_ok = True
                break

    if car_ok and hotel_ok:
        return "🟢OK"
    elif car_ok or hotel_ok:
        return "🟡一部"
    else:
        return "❌未照"

# --- STEP 1: 空港選択リスト（横3列固定） ---
st.markdown("### 🎲 ガチャ照合用 空港リスト")

selected_airports = []

# 画面を常に横3列に分ける
cols = st.columns(3)
for idx, ap in enumerate(AIRPORT_DB):
    status_icon = get_status_tag(ap)
    col_target = cols[idx % 3]
    with col_target:
        # 空港名横にステータスバッジ（🟢OK等）を表示
        label = f"[{status_icon}] {ap['name']}({ap['code']})"
        if st.checkbox(label, key=f"select_{ap['code']}"):
            selected_airports.append(ap)

st.divider()

# --- STEP 2: 選択された空港の詳細照会 ＆ チェック入力 ---
if not selected_airports:
    st.info("👆 上の3列リストから、ガチャで出た4空港にチェックを入れてください。")
else:
    st.markdown(f"### 📋 選択中空港の車・宿照会 ({len(selected_airports)}件)")

    for ap in selected_airports:
        status_icon = get_status_tag(ap)
        with st.expander(f"【{status_icon}】✈️ {ap['name']}空港 ({ap['code']}) の詳細・空き入力", expanded=True):
            col1, col2, col3 = st.columns([1.2, 1, 0.8])
            
            with col1:
                st.markdown("**🚗 タイムズカー空車(☑)**")
                if ap["type"] == "times":
                    st.link_button("📲 マイページ照会へ", "https://share.timescar.jp/view/sp/member/mypage.jsp")
                    for s_idx, st_info in enumerate(ap["stations"]):
                        st.caption(f"📍 {st_info['name']}")
                        for m_idx, model in enumerate(st_info["models"]):
                            st.checkbox(f"☑ {model} 空車あり", key=f"car_chk_{ap['code']}_{s_idx}_{m_idx}")
                else:
                    st.error("タイムズ非対応")
                    st.link_button("📲 dカーシェア", "https://dcarshare.docomo.ne.jp/")

            with col2:
                st.markdown(f"**🏨 温泉・バイキング宿({num_people}名)**")
                if trip_type == "日帰り":
                    st.info("日帰りのため宿不要")
                else:
                    jalan_url = f"https://www.jalan.net/uw/uwp3000/uwp3001.do?keyword={ap['name']}+温泉+バイキング&adultNum={num_people}"
                    st.link_button(f"📲 じゃらんで検索", jalan_url)
                    for h_idx, h_name in enumerate(ap["fav_hotels"]):
                        st.checkbox(f"☑ {h_name} 空室あり", key=f"hotel_chk_{ap['code']}_{h_idx}")

            with col3:
                st.markdown("**🌤 天気**")
                st.link_button("📲 天気予報", f"https://tenki.jp/search/?keyword={ap['name']}")

            st.divider()
