import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="どこかにマイル 判定＆チェックツール", page_icon="✈️", layout="centered")

# カスタムCSS
st.markdown("""
    <style>
    html {
        scroll-behavior: smooth;
    }
    /* 赤色メインヘッダー */
    .header-card {
        background: linear-gradient(135deg, #d32f2f 0%, #9a0007 100%);
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .header-card h1 {
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: bold;
        margin: 0 0 6px 0;
    }
    .header-card p {
        color: #f5f5f5 !important;
        font-size: 12px;
        margin: 0;
    }
    /* 使い方案内 */
    .info-box {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        color: #e2e8f0 !important;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 12px;
        margin-bottom: 16px;
    }
    /* クイックジャンプリンク表示 */
    .quick-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 10px 0 20px 0;
    }
    .quick-nav a {
        background-color: #1e293b;
        color: #60a5fa !important;
        border: 1px solid #3b82f6;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        text-decoration: none;
        font-weight: bold;
    }
    .quick-nav a:hover {
        background-color: #3b82f6;
        color: #ffffff !important;
    }
    /* 空港枠（カード風コンテナ） */
    div[data-testid="stForm"] {
        border: 1px solid #334155 !important;
        background-color: #0f172a !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 画面トップアンカー
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# 赤ヘッダー
st.markdown("""
    <div class="header-card">
        <h1>✈️ どこかにマイル 判定＆チェックツール</h1>
        <p>羽田発・車シェア空き・バイキング/温泉宿・天気を一括チェック</p>
    </div>
""", unsafe_allow_html=True)

# 説明カード
st.markdown("""
    <div class="info-box">
        💡 <b>使い方:</b> 初期状態で全空港に☑が入っています。不要な空港は☑を外し、下のジャンプボタンから目的の空港へ直接移動できます。
    </div>
""", unsafe_allow_html=True)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 条件設定")
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

    st.subheader("🚗 車両・配備条件")
    selected_models = st.multiselect(
        "優先カーシェア車種",
        ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア", "ヴォクシー", "フィット", "ヤリス", "ノート"],
        default=["C-HR", "CX-30", "MAZDA3", "ヤリスクロス"]
    )
    
    allow_other_car = st.checkbox("タイムズに希望車種がなければ dカーシェア/一般レンタカーも検討", value=False)

# --- 空港データベース ---
AIRPORT_DB = [
    {"code": "CTS", "name": "新千歳空港", "type": "times", "stations": [{"name": "新千歳空港店（送迎）", "models": ["C-HR", "CX-30", "MAZDA3", "ノア", "ヴォクシー"]}, {"name": "新千歳空港A駐車場", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["定山渓万世閣", "登別万世閣"]},
    {"code": "HKD", "name": "函館空港", "type": "times", "stations": [{"name": "函館空港駐車場", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["湯の川温泉 ホテル万惣"]},
    {"code": "AKJ", "name": "旭川空港", "type": "times", "stations": [{"name": "旭川空港前店", "models": ["ヤリスクロス", "フィット", "ノア"]}], "fav_hotels": ["層雲峡観光ホテル"]},
    {"code": "MMB", "name": "女満別空港", "type": "times", "stations": [{"name": "女満別空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["網走観光ホテル"]},
    {"code": "OBO", "name": "帯広空港", "type": "times", "stations": [{"name": "帯広空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["十勝川温泉 第一ホテル"]},
    {"code": "KUH", "name": "釧路空港", "type": "times", "stations": [{"name": "釧路空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["阿寒湖温泉 あかん遊久の里鶴雅"]},
    {"code": "AOJ", "name": "青森空港", "type": "rental", "stations": [], "fav_hotels": ["浅虫温泉 宿屋つばき"]},
    {"code": "MSJ", "name": "三沢空港", "type": "rental", "stations": [], "fav_hotels": ["星野リゾート 青森屋"]},
    {"code": "AXT", "name": "秋田空港", "type": "times", "stations": [{"name": "秋田空港駐車場", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["男鹿温泉 ホテルきららか"]},
    {"code": "GAJ", "name": "山形空港", "type": "times", "stations": [{"name": "山形空港前", "models": ["フィット", "ヤリス"]}], "fav_hotels": ["蔵王温泉 高見屋"]},
    {"code": "HNA", "name": "花巻空港", "type": "times", "stations": [{"name": "花巻空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["花巻温泉 ホテル千秋閣"]},
    {"code": "KMQ", "name": "小松空港", "type": "times", "stations": [{"name": "小松空港第一駐車場", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["加賀温泉郷 瑠璃光"]},
    {"code": "OKJ", "name": "岡山空港", "type": "times", "stations": [{"name": "岡山空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["湯郷温泉 季譜の里"]},
    {"code": "HIJ", "name": "広島空港", "type": "times", "stations": [{"name": "広島空港前", "models": ["MAZDA3", "CX-30", "ヤリスクロス", "ノア"]}], "fav_hotels": ["宮島温泉 錦水館"]},
    {"code": "IZO", "name": "出雲空港", "type": "times", "stations": [{"name": "出雲空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["玉造温泉 佳翠苑皆美"]},
    {"code": "UBJ", "name": "山口宇部空港", "type": "times", "stations": [{"name": "山口宇部空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["湯田温泉 松田屋ホテル"]},
    {"code": "TKM", "name": "高松空港", "type": "times", "stations": [{"name": "高松空港前", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["琴平温泉 琴参閣"]},
    {"code": "MYJ", "name": "松山空港", "type": "times", "stations": [{"name": "松山空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["道後温泉 ふなや"]},
    {"code": "TKS", "name": "徳島空港", "type": "times", "stations": [{"name": "徳島空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["鳴門温泉 アオアヲナルトリゾート"]},
    {"code": "KCZ", "name": "高知空港", "type": "times", "stations": [{"name": "高知空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["城西館"]},
    {"code": "FUK", "name": "福岡空港", "type": "times", "stations": [{"name": "福岡空港国内線前", "models": ["C-HR", "CX-30", "MAZDA3", "ノア"]}, {"name": "福岡空港国際線前", "models": ["ヤリスクロス", "ヴォクシー", "フィット"]}], "fav_hotels": ["原鶴温泉 泰泉閣"]},
    {"code": "KKJ", "name": "北九州空港", "type": "times", "stations": [{"name": "北九州空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["ホテルクラウンパレス小倉"]},
    {"code": "OIT", "name": "大分空港", "type": "times", "stations": [{"name": "大分空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["別府温泉 杉乃井ホテル"]},
    {"code": "NGS", "name": "長崎空港", "type": "times", "stations": [{"name": "長崎空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["雲仙温泉 雲仙宮崎旅館"]},
    {"code": "KMJ", "name": "熊本空港", "type": "times", "stations": [{"name": "熊本空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["黒川温泉 ふじ屋"]},
    {"code": "KMI", "name": "宮崎空港", "type": "times", "stations": [{"name": "宮崎空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["シェラトン・グランデ"]},
    {"code": "KOJ", "name": "鹿児島空港", "type": "times", "stations": [{"name": "鹿児島空港前", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["霧島温泉 霧島ホテル"]},
    {"code": "OKA", "name": "那覇空港", "type": "times", "stations": [{"name": "那覇空港店（送迎あり）", "models": ["C-HR", "CX-30", "MAZDA3", "ノア", "ヴォクシー"]}], "fav_hotels": ["サザンビーチホテル"]},
    {"code": "MMY", "name": "宮古空港", "type": "times", "stations": [{"name": "宮古空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["シギラベイサイドスイート"]},
    {"code": "ISG", "name": "新石垣空港", "type": "times", "stations": [{"name": "石垣空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["フサキビーチリゾート"]}
]

# 車種適合判定
def has_matching_car(ap, target_models):
    if not target_models:
        return True
    for st_info in ap.get("stations", []):
        for m in st_info.get("models", []):
            if m in target_models:
                return True
    return False

# 可否ステータス判定
def get_status_tag(ap):
    car_ok = False
    hotel_ok = True if trip_type == "日帰り" else False

    for s_idx, st_info in enumerate(ap["stations"]):
        for m_idx, _ in enumerate(st_info["models"]):
            if st.session_state.get(f"car_chk_{ap['code']}_{s_idx}_{m_idx}", False):
                car_ok = True
                break

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

selected_airports = []

# --- 枠で囲んだ空港選択エリア ---
st.markdown("##### ⚙️ 候補空港選択")

with st.form(key="airport_select_form", border=True):
    cols = st.columns(2)
    
    for idx, ap in enumerate(AIRPORT_DB):
        car_match = has_matching_car(ap, selected_models)
        is_available = car_match or allow_other_car
        
        key_name = f"select_{ap['code']}"
        if key_name not in st.session_state:
            st.session_state[key_name] = is_available

        status_icon = get_status_tag(ap)
        col_target = cols[idx % 2]

        with col_target:
            if is_available:
                label = f"{status_icon} {ap['name']}"
                checked = st.checkbox(label, key=key_name)
                if checked:
                    selected_airports.append(ap)
            else:
                st.caption(f"⚪ (希望車種なし) {ap['name']}")

    st.form_submit_button("受け入れ態勢の判定を更新", use_container_width=True)

# --- 🎯 ワンタップジャンプ（ショートカット目次） ---
if selected_airports:
    st.markdown("##### 🚀 選択中空港へ一発ジャンプ")
    nav_html = '<div class="quick-nav">'
    for ap in selected_airports:
        status_icon = get_status_tag(ap)
        nav_html += f'<a href="#airport-{ap["code"]}">{status_icon} {ap["name"]}</a>'
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

st.divider()

# --- 詳細照会エリア ---
if selected_airports:
    st.markdown(f"### 📋 候補空港の空き確認 ({len(selected_airports)}件)")

    for ap in selected_airports:
        status_icon = get_status_tag(ap)
        
        # ジャンプ先用アンカータグ
        st.markdown(f'<div id="airport-{ap["code"]}"></div>', unsafe_allow_html=True)
        
        with st.expander(f"【{status_icon}】✈️ {ap['name']} ({ap['code']})", expanded=True):
            col1, col2 = st.columns([1.2, 1])
            
            with col1:
                st.markdown("**🚗 車両空き状況 (☑)**")
                if ap["type"] == "times":
                    st.link_button("📲 タイムズマイページへ", "https://share.timescar.jp/view/sp/member/mypage.jsp")
                    for s_idx, st_info in enumerate(ap["stations"]):
                        st.caption(f"📍 {st_info['name']}")
                        for m_idx, model in enumerate(st_info["models"]):
                            st.checkbox(f"☑ {model} 空車あり", key=f"car_chk_{ap['code']}_{s_idx}_{m_idx}")
                
                if not has_matching_car(ap, selected_models) or ap["type"] != "times":
                    st.caption("💡 タイムズ希望車種なし／その他")
                    st.link_button("📲 dカーシェアで検索", "https://dcarshare.docomo.ne.jp/")
                    st.link_button("📲 楽天トラベル レンタカー", "https://travel.rakuten.co.jp/cars/")

            with col2:
                st.markdown(f"**🏨 温泉宿・天気**")
                if trip_type == "日帰り":
                    st.info("日帰りのため宿不要")
                else:
                    jalan_url = f"https://www.jalan.net/uw/uwp3000/uwp3001.do?keyword={ap['name']}+温泉+バイキング&adultNum={num_people}"
                    st.link_button(f"📲 じゃらんで宿検索", jalan_url)
                    for h_idx, h_name in enumerate(ap["fav_hotels"]):
                        st.checkbox(f"☑ {h_name} 空室あり", key=f"hotel_chk_{ap['code']}_{h_idx}")

                st.link_button("🌤 天気予報を見る", f"https://tenki.jp/search/?keyword={ap['name']}")

            # 各枠の右下に「▲ トップに戻る」ボタンを追加
            st.markdown("""
                <div style="text-align: right; margin-top: 10px;">
                    <a href="#top" style="text-decoration: none; font-size: 12px; background-color: #334155; color: #f8fafc; padding: 4px 12px; border-radius: 4px; font-weight: bold;">▲ トップに戻る</a>
                </div>
            """, unsafe_allow_html=True)
