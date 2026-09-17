import streamlit as st
import json
import urllib.parse
from datetime import datetime, timedelta

st.set_page_config(page_title="どこかにマイル 空き確認＆設定ツール", page_icon="✈️", layout="wide")

# スタイル定義
st.markdown("""
    <style>
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 16px;
    }
    .status-badge-set {
        background-color: #065f46;
        color: #34d399;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-badge-unset {
        background-color: #374151;
        color: #9ca3af;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .station-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# 画面トップアンカー
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown("""
    <div class="header-card">
        <h2 style="margin:0; font-size: 20px;">✈️ どこかにマイル マイル判定・ステーション設定ツール</h2>
        <p style="margin:4px 0 0 0; font-size:12px; color:#cbd5e1;">空港ステーションごとの実車配備を設定し、予約・空車状況をスマートに管理します。</p>
    </div>
""", unsafe_allow_html=True)

# --- タイムズカー公式クラス別車種リスト ---
TIMES_CAR_MODELS = {
    "ベーシック": [
        "ヤリスクロス", "ヤリス", "フィット", "ノート e-POWER", "MAZDA3", 
        "アクア", "オーラ e-POWER", "ライズ", "ソリオ", "スイフト", 
        "MAZDA2", "ルーミー", "N-BOX", "ハスラー", "サクラ"
    ],
    "ミドル": [
        "CX-30", "シエンタ", "フリード", "プリウス", "CX-5", "C-HR", "リーフ"
    ],
    "プレミアム": [
        "ノア", "ヴォクシー", "セレナ", "アルファード", "bZ4X"
    ]
}

# 全車種の一覧リスト
ALL_MODELS = TIMES_CAR_MODELS["ベーシック"] + TIMES_CAR_MODELS["ミドル"] + TIMES_CAR_MODELS["プレミアム"]

# --- 空港＆公式ステーション マスターデータベース ---
AIRPORT_DB = [
    {"code": "AKJ", "name": "旭川空港", "stations": ["旭川空港", "タイムズカー旭川空港前店"], "fav_hotels": ["層雲峡観光ホテル", "OMO7旭川"]},
    {"code": "MMB", "name": "女満別空港", "stations": ["女満別空港駐車場", "タイムズカー女満別空港前店"], "fav_hotels": ["網走観光ホテル", "ホテル網走湖荘"]},
    {"code": "KMJ", "name": "阿蘇くまもと空港", "stations": ["阿蘇くまもと空港駐車場（P3）", "タイムズカー熊本空港前店"], "fav_hotels": ["黒川温泉 ふじ屋", "栃木温泉 小松別荘"]},
    {"code": "CTS", "name": "新千歳空港", "stations": ["新千歳空港A駐車場", "新千歳空港B駐車場", "タイムズカー新千歳空港店"], "fav_hotels": ["定山渓万世閣", "登別万世閣"]},
    {"code": "HKD", "name": "函館空港", "stations": ["函館空港駐車場", "タイムズカー函館空港前店"], "fav_hotels": ["湯の川温泉 ホテル万惣"]},
    {"code": "OBO", "name": "帯広空港", "stations": ["タイムズカー帯広空港前店"], "fav_hotels": ["十勝川温泉 第一ホテル"]},
    {"code": "KUH", "name": "釧路空港", "stations": ["タイムズカー釧路空港前店"], "fav_hotels": ["阿寒湖温泉 あかん遊久の里鶴雅"]},
    {"code": "KMQ", "name": "小松空港", "stations": ["小松空港第一駐車場", "タイムズカー小松空港前店"], "fav_hotels": ["加賀温泉郷 瑠璃光"]},
    {"code": "NGO", "name": "中部国際空港", "stations": ["タイムズカー中部国際空港店"], "fav_hotels": ["下呂温泉 水明館"]},
    {"code": "ITM", "name": "大阪国際(伊丹)空港", "stations": ["タイムズカー伊丹空港店"], "fav_hotels": ["有馬温泉 兵衛向陽閣"]},
    {"code": "KIX", "name": "関西国際空港", "stations": ["タイムズカー関西空港店"], "fav_hotels": ["犬鳴山温泉 不動口館"]},
    {"code": "FUK", "name": "福岡空港", "stations": ["福岡空港国内線前", "福岡空港国際線前"], "fav_hotels": ["原鶴温泉 泰泉閣"]},
    {"code": "OKA", "name": "那覇空港", "stations": ["タイムズカー那覇空港店"], "fav_hotels": ["サザンビーチホテル"]}
]

# --- セッション状態（ステーション配備設定）の初期化 ---
if "station_config" not in st.session_state:
    st.session_state["station_config"] = {}

# --- サイドバー：設定・検索条件 ---
with st.sidebar:
    st.header("⚙️ 検索条件＆優先車種")
    
    trip_type = st.radio("旅行スタイル", ["1泊2日", "2泊3日", "日帰り"], index=0)
    num_people = st.number_input("利用人数", min_value=1, max_value=8, value=2)

    st.subheader("🚗 探したい優先クラス・車種")
    selected_classes = st.multiselect("希望クラス", ["ベーシック", "ミドル", "プレミアム"], default=["ベーシック", "ミドル"])
    
    user_priority_models = st.multiselect("希望車種（複数選択可）", options=ALL_MODELS, default=["ヤリスクロス", "CX-30", "シエンタ", "ノア"])

    st.divider()
    
    # 設定データのバックアップ / リスト初期化
    st.subheader("💾 設定データの保存 / 復元")
    config_json = json.dumps(st.session_state["station_config"], ensure_ascii=False, indent=2)
    st.download_button("⚙️ 設定をJSONで保存", data=config_json, file_name="times_station_config.json", mime="application/json")
    
    uploaded_file = st.file_uploader("📥 JSON設定を読み込む", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state["station_config"] = json.load(uploaded_file)
            st.success("設定を読み込みました！")
            st.rerun()
        except Exception as e:
            st.error("設定ファイルの読み込みに失敗しました。")

# --- メイン画面：モード切り替え ---
tab1, tab2 = st.tabs(["🔍 空車照会・確認メモ", "⚙️ 空港＆ステーション配備設定"])

# ==========================================
# TAB 1: 空車照会・メモ確認画面
# ==========================================
with tab1:
    st.caption("設定済みのステーション情報をベースに、実際の空車状況をチェック・記憶できます。")
    
    # 候補空港の上部ボタン表示
    st.markdown("##### ✈️ 候補空港一覧")
    
    btn_html = '<div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px;">'
    for ap in AIRPORT_DB:
        code = ap["code"]
        name = ap["name"]
        
        # 設定済みステーション数をカウント
        set_count = sum(1 for st_name in ap["stations"] if st.session_state["station_config"].get(f"{code}_{st_name}"))
        
        if set_count > 0:
            badge = f'<span class="status-badge-set">設定済 ✅ ({set_count}/{len(ap["stations"])})</span>'
        else:
            badge = '<span class="status-badge-unset">未設定 ⚪</span>'
            
        btn_html += f'<a href="#ap-{code}" style="text-decoration:none; color:inherit;"><div style="background-color:#1e293b; border:1px solid #334155; padding:6px 12px; border-radius:6px; font-size:13px;"><b>{name}</b> {badge}</div></a>'
    btn_html += '</div>'
    st.markdown(btn_html, unsafe_allow_html=True)

    st.divider()

    # 各空港のチェックカード
    for ap in AIRPORT_DB:
        code = ap["code"]
        name = ap["name"]
        
        st.markdown(f'<div id="ap-{code}"></div>', unsafe_allow_html=True)
        
        with st.expander(f"✈️ 【{name} ({code})】 空きチェック＆情報", expanded=True):
            col_car, col_other = st.columns([1.2, 1])
            
            with col_car:
                st.markdown("**🚗 タイムズカー ステーション状況**")
                st.link_button("📲 タイムズカー公式マイページで照会", "https://share.timescar.jp/view/sp/member/mypage.jsp")
                
                for st_name in ap["stations"]:
                    st_key = f"{code}_{st_name}"
                    configured_models = st.session_state["station_config"].get(st_key, [])
                    
                    st.markdown('<div class="station-box">', unsafe_allow_html=True)
                    if configured_models:
                        st.markdown(f'<b>📍 {st_name}</b> <span class="status-badge-set">設定済 ✅</span>', unsafe_allow_html=True)
                        st.caption("配備設定車種:")
                        
                        # 配備車種ごとにチェックボックス作成
                        for m in configured_models:
                            is_hit = "⭐ " if m in user_priority_models else ""
                            st.checkbox(f"{is_hit}{m} （空車あり）", key=f"check_{code}_{st_name}_{m}")
                    else:
                        st.markdown(f'<b>📍 {st_name}</b> <span class="status-badge-unset">未設定 ⚪</span>', unsafe_allow_html=True)
                        st.caption("※「配備設定」タブで車種を登録すると、チェックリストが表示されます。")
                        
                    st.markdown('</div>', unsafe_allow_html=True)

            with col_other:
                st.markdown("**🏨 宿・天気**")
                if trip_type == "日帰り":
                    st.info("日帰りのため宿検索は不要です")
                else:
                    jalan_url = f"https://www.jalan.net/uw/uwp3000/uwp3001.do?keyword={urllib.parse.quote(name)}+温泉+バイキング&adultNum={num_people}"
                    st.link_button("📲 じゃらんで温泉・バイキング宿を検索", jalan_url)
                    for h_idx, h_name in enumerate(ap["fav_hotels"]):
                        st.checkbox(f"☑ {h_name} 空室あり", key=f"hotel_{code}_{h_idx}")

                yahoo_weather = f"https://search.yahoo.co.jp/realtime/search?p={urllib.parse.quote(name + ' 天気')}"
                st.link_button("🌤 Yahoo!リアルタイム天気検索", yahoo_weather)

            st.markdown("""
                <div style="text-align: right; margin-top: 8px;">
                    <a href="#top" style="text-decoration: none; font-size: 11px; color: #94a3b8;">▲ トップに戻る</a>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# TAB 2: ステーション配備車種の設定画面
# ==========================================
with tab2:
    st.subheader("⚙️ 各空港ステーションの配備車種を設定")
    st.info("実際のタイムズカー予約画面で確認したステーションごとの配備車種（またはクラス別代表車種）を事前に登録しておきます。")
    
    selected_ap_code = st.selectbox(
        "設定対象の空港を選択",
        options=[ap["code"] for ap in AIRPORT_DB],
        format_func=lambda code: next(f"{ap['name']} ({ap['code']})" for ap in AIRPORT_DB if ap['code'] == code)
    )
    
    target_ap = next(ap for ap in AIRPORT_DB if ap["code"] == selected_ap_code)
    
    st.markdown(f"### 📍 {target_ap['name']} のステーション設定")
    
    for st_name in target_ap["stations"]:
        st_key = f"{selected_ap_code}_{st_name}"
        current_saved = st.session_state["station_config"].get(st_key, [])
        
        with st.form(key=f"form_{st_key}"):
            st.markdown(f"#### 📍 {st_name}")
            
            if current_saved:
                st.markdown('<span class="status-badge-set">現在: 設定済み ✅</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-badge-unset">現在: 未設定 ⚪</span>', unsafe_allow_html=True)
                
            new_selected = st.multiselect(
                "配備されている車種を選択",
                options=ALL_MODELS,
                default=current_saved,
                key=f"select_{st_key}"
            )
            
            submit_btn = st.form_submit_button("💾 このステーションの車種を保存")
            if submit_btn:
                st.session_state["station_config"][st_key] = new_selected
                st.success(f"{st_name} の配備車種を保存しました！")
                st.rerun()
