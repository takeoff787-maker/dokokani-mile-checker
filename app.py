import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="どこかにマイル 条件クリア空港 判定アプリ", page_icon="✈️", layout="wide")
st.title("✈️ どこかにマイル 条件クリア空港 判定アプリ")

# --- セッション状態の初期化（カスタムホテル用） ---
if "custom_hotels" not in st.session_state:
    st.session_state.custom_hotels = {}

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 基本・検索条件")
    
    # 滞在パターン設定
    trip_type = st.radio("旅行スタイル", ["1泊2日", "2泊3日", "日帰り"], index=0)
    
    default_start = datetime.now() + timedelta(days=4)
    start_date = st.date_input("出発日", default_start)
    start_time = st.time_input("出発時間", datetime.strptime("09:00", "%H:%M").time())
    
    if trip_type == "日帰り":
        end_date = start_date
    elif trip_type == "1泊2日":
        end_date = start_date + timedelta(days=1)
    else:  # 2泊3日
        end_date = start_date + timedelta(days=2)
        
    end_time = st.time_input("帰着時間", datetime.strptime("18:00", "%H:%M").time())
    
    st.subheader("🚗 車両条件（タイムズカー希望車種）")
    times_car_models = st.multiselect(
        "希望車種・クラス（一次判定用）",
        ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア", "ヴォクシー", "フィット/ヤリス等"],
        default=["C-HR", "CX-30", "MAZDA3", "ヤリスクロス"]
    )
    
    st.markdown("---")
    st.caption("※ タイムズカーシェアのマイページで空車を確認したら、各ステーションの車種横にある「☑ 空車確認済」にチェックを入れて記録できます。")

# --- 空港＆ステーション＆ホテルデータベース ---
AIRPORT_DB = [
    {
        "code": "CTS", "name": "新千歳空港", "region": "北海道", "type": "times",
        "stations": [
            {"name": "タイムズカー新千歳空港店（送迎あり）", "models": ["C-HR", "CX-30", "MAZDA3", "ノア", "ヴォクシー"]},
            {"name": "新千歳空港A駐車場ステーション", "models": ["ヤリスクロス", "フィット"]}
        ],
        "fav_hotels": ["定山渓万世閣 ホテルミリオーネ", "登別万世閣"]
    },
    {
        "code": "HKD", "name": "函館空港", "region": "北海道", "type": "times",
        "stations": [
            {"name": "函館空港駐車場ステーション", "models": ["ヤリスクロス", "フィット", "ノート"]}
        ],
        "fav_hotels": ["湯の川温泉 ホテル万惣", "イマジン ホテル＆リゾート函館"]
    },
    {
        "code": "AOJ", "name": "青森空港", "region": "東北", "type": "rental",
        "stations": [],
        "fav_hotels": ["浅虫温泉 宿屋つばき"]
    },
    {
        "code": "KMQ", "name": "小松空港", "region": "北陸", "type": "times",
        "stations": [
            {"name": "小松空港第一駐車場ステーション", "models": ["CX-30", "ヤリスクロス", "フィット"]}
        ],
        "fav_hotels": ["加賀温泉郷 瑠璃光"]
    },
    {
        "code": "HIJ", "name": "広島空港", "region": "中国", "type": "times",
        "stations": [
            {"name": "広島空港前ステーション", "models": ["MAZDA3", "CX-30", "ヤリスクロス", "ノア"]}
        ],
        "fav_hotels": ["宮島温泉 錦水館"]
    },
    {
        "code": "TKM", "name": "高松空港", "region": "四国", "type": "times",
        "stations": [
            {"name": "高松空港前ステーション", "models": ["ヤリスクロス", "フィット", "ノート"]}
        ],
        "fav_hotels": ["琴平温泉 琴参閣"]
    },
    {
        "code": "MYJ", "name": "松山空港", "region": "四国", "type": "times",
        "stations": [
            {"name": "松山空港前ステーション", "models": ["CX-30", "ヤリスクロス", "フィット"]}
        ],
        "fav_hotels": ["道後温泉 ふなや"]
    },
    {
        "code": "FUK", "name": "福岡空港", "region": "九州", "type": "times",
        "stations": [
            {"name": "福岡空港国内線前ステーション", "models": ["C-HR", "CX-30", "MAZDA3", "ノア"]},
            {"name": "福岡空港国際線前ステーション", "models": ["ヤリスクロス", "ヴォクシー", "フィット"]}
        ],
        "fav_hotels": ["原鶴温泉 泰泉閣"]
    },
    {
        "code": "KOJ", "name": "鹿児島空港", "region": "九州", "type": "times",
        "stations": [
            {"name": "鹿児島空港前ステーション", "models": ["ヤリスクロス", "フィット", "ノート"]}
        ],
        "fav_hotels": ["霧島温泉 霧島ホテル"]
    }
]

# --- メイン処理 ---
start_dt = datetime.combine(start_date, start_time)
end_dt = datetime.combine(end_date, end_time)

st.success(f"📅 【設定条件】{trip_type} | {start_dt.strftime('%Y/%m/%d %H:%M')} 〜 {end_dt.strftime('%m/%d %H:%M')}")

st.markdown("### 📊 候補空港 一括判定サマリー")
st.caption("希望車種が配備されているステーションがある空港を判定しています。")

# 空港ごとのクリア状況のまとめ
summary_cols = st.columns(2)
for idx, ap in enumerate(AIRPORT_DB):
    all_models_in_ap = set()
    for st_info in ap["stations"]:
        all_models_in_ap.update(st_info["models"])
    
    matched_models = [m for m in times_car_models if m in all_models_in_ap]
    has_match = len(matched_models) > 0
    
    col_target = summary_cols[0] if idx % 2 == 0 else summary_cols[1]
    with col_target:
        if ap["type"] == "rental":
            st.error(f"🔴 **{ap['name']} ({ap['code']})** - カーシェア非対応（レンタカー店舗のみ）")
        elif has_match:
            st.success(f"🟢 **{ap['name']} ({ap['code']})** - 希望車種あり ({', '.join(matched_models)})")
        else:
            st.warning(f"🟡 **{ap['name']} ({ap['code']})** - 希望車種なし（コンパクト他のみ）")

st.divider()

# --- 各空港の詳細・空車チェック＆ホテル管理 ---
st.markdown("### 📲 各空港の詳細・空車チェック ＆ 宿案内")

for ap in AIRPORT_DB:
    all_models_in_ap = set()
    for st_info in ap["stations"]:
        all_models_in_ap.update(st_info["models"])
    matched_models = [m for m in times_car_models if m in all_models_in_ap]
    has_match = len(matched_models) > 0

    with st.expander(f"✈️ 【{ap['name']} ({ap['code']})】詳細と空車確認・宿設定", expanded=has_match):
        c1, c2, c3 = st.columns([1.2, 1, 0.8])
        
        # --- Column 1: ステーション＆車種配備 & 空車マーク ---
        with c1:
            st.markdown("##### 🚗 配備ステーション＆車両空き確認")
            if ap["type"] == "times":
                mypage_url = "https://share.timescar.jp/view/sp/member/mypage.jsp"
                st.link_button("📲 タイムズカー マイページ（空室照会）", mypage_url)
                st.caption(f"※検索キーワード: 「{ap['name']}」")
                
                for s_idx, st_info in enumerate(ap["stations"]):
                    st.markdown(f"**📍 {st_info['name']}**")
                    for m_idx, model in enumerate(st_info["models"]):
                        is_fav = "⭐" if model in times_car_models else ""
                        chk_key = f"chk_{ap['code']}_{s_idx}_{m_idx}"
                        st.checkbox(f"{is_fav} {model} （実車の空き確認済☑）", key=chk_key)
                    st.write("")
            else:
                st.error("タイムズカーシェア非対応エリアです")
                st.link_button("📲 dカーシェアで検索", "https://dcarshare.docomo.ne.jp/")
                st.link_button("📲 タイムズカーレンタル（公式）", "https://rental.timescar.jp/")

        # --- Column 2: ホテル・温泉宿管理 ---
        with c2:
            st.markdown("##### 🏨 温泉＆バイキング宿")
            if trip_type == "日帰り":
                st.info("💡 日帰りプランが選択されているため、ホテル検索・予約は不要です。")
            else:
                st.write("**【登録中のお気に入りホテル】**")
                # 初期お気に入りリスト
                for h in ap["fav_hotels"]:
                    st.markdown(f"・ **{h}**")
                
                # 動的追加されたホテル
                custom_list = st.session_state.custom_hotels.get(ap['code'], [])
                for ch in custom_list:
                    st.markdown(f"・ **{ch}** *(追加済み)*")
                
                # 新しいお気に入りホテルの手動追加
                new_h = st.text_input(f"新しいホテルを追加 ({ap['code']})", key=f"input_h_{ap['code']}", placeholder="例: 登別グランドホテル")
                if st.button("追加", key=f"btn_h_{ap['code']}"):
                    if new_h:
                        if ap['code'] not in st.session_state.custom_hotels:
                            st.session_state.custom_hotels[ap['code']] = []
                        st.session_state.custom_hotels[ap['code']].append(new_h)
                        st.rerun()

                st.markdown("---")
                st.write("**【満室時の代替・一覧検索】**")
                jalan_url = f"https://www.jalan.net/uw/uwp3000/uwp3001.do?keyword={ap['name']}+温泉+バイキング"
                st.link_button("📲 じゃらんで検索", jalan_url)
                
                gmap_url = f"https://www.google.com/maps/search/{ap['name']}+温泉+ホテル"
                st.link_button("📲 Googleマップで探す", gmap_url)

        # --- Column 3: 天気情報 ---
        with c3:
            st.markdown("##### 🌤 現地天気")
            tenki_url = f"https://tenki.jp/search/?keyword={ap['name']}"
            st.link_button("📲 天気予報を確認", tenki_url)
