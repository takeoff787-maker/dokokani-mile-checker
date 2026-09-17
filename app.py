import time
from datetime import datetime, timedelta
import requests
import streamlit as st

# --- 画面ヘッダー設定 ---
st.set_page_config(
    page_title="どこかにマイル候補地 自動判定アプリ", page_icon="✈️", layout="wide"
)

st.title("✈️ どこかにマイル 条件クリア空港 自動一括検索")
st.caption(
    "羽田発・1泊2日・一人旅向け｜カーシェア/レンタカー空き・バイキング/温泉宿・天気を自動判定"
)

# --- 入力フォーム ---
with st.sidebar:
    st.header("⚙️ 検索条件")
    default_date = datetime.now() + timedelta(days=4)
    target_date = st.date_input("出発予定日（4日以上先）", default_date)

    st.subheader("🚗 車両条件")
    times_car_models = st.multiselect(
        "タイムズカーシェアの希望車種",
        ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア"],
        default=["C-HR", "CX-30", "MAZDA3", "ヤリスクロス"],
    )

    allow_rental = st.checkbox(
        "タイムズ不在エリア（青森等）でdカーシェア/レンタカー（SUV/カローラ等）を許可",
        value=True,
    )

    st.subheader("🏨 宿泊条件")
    budget_max = st.slider("1泊2食の上限予算 (円)", 10000, 30000, 25000, step=1000)
    need_buffet = st.checkbox("朝夕バイキング形式必須", value=True)
    need_onsen = st.checkbox("温泉必須", value=True)

    search_btn = st.button("🔍 条件に合う空港を自動スキャン", type="primary")

# --- 羽田発 ターゲット空港データベース ---
AIRPORT_DB = [
    {
        "code": "CTS",
        "name": "新千歳空港",
        "region": "北海道",
        "type": "times",
        "station": "タイムズカー新千歳空港店（走ってマイル対象）",
    },
    {
        "code": "HKD",
        "name": "函館空港",
        "region": "北海道",
        "type": "times",
        "station": "タイムズカー函館空港店",
    },
    {
        "code": "AOJ",
        "name": "青森空港",
        "region": "東北",
        "type": "rental",
        "station": "タイムズ無し：dカーシェア／トヨタレンタカー（カローラツーリング/ヤリスクロス等）",
    },
    {
        "code": "KMQ",
        "name": "小松空港",
        "region": "北陸",
        "type": "times",
        "station": "タイムズカー小松空港店",
    },
    {
        "code": "HIJ",
        "name": "広島空港",
        "region": "中国",
        "type": "times",
        "station": "タイムズカー広島空港店",
    },
    {
        "code": "TKM",
        "name": "高松空港",
        "region": "四国",
        "type": "times",
        "station": "タイムズカー高松空港店",
    },
    {
        "code": "MYJ",
        "name": "松山空港",
        "region": "四国",
        "type": "times",
        "station": "タイムズカー松山空港店",
    },
    {
        "code": "FUK",
        "name": "福岡空港",
        "region": "九州",
        "type": "times",
        "station": "タイムズカー福岡空港店",
    },
    {
        "code": "KOJ",
        "name": "鹿児島空港",
        "region": "九州",
        "type": "times",
        "station": "タイムズカー鹿児島空港店",
    },
]


# --- モック照会ロジック（実際の実装ではスクレイピングや各種APIを呼出） ---
def check_car_availability(airport, date, preferred_models, allow_rental):
    # タイムズ店舗が存在しないエリアの処理
    if airport["type"] == "rental":
        if allow_rental:
            return True, "SUV/カローラツーリング等 空きあり (dカーシェア/レンタカー)"
        return False, "タイムズカーシェア非対応エリア"

    # タイムズ店舗の車種マッチング判定（実機ではWebスクレイピング連携）
    # ※デモ用判定ロジック
    return True, f"希望車種あり ({', '.join(preferred_models[:2])})"


def check_hotel_availability(airport, date, budget, buffet, onsen):
    # 楽天トラベルAPI等で「1人部屋」「1泊2食」「バイキング」「温泉」を検索
    return True, f"空室あり（バイキング＆温泉付 1名込 ¥18,500〜）"


def check_weather(airport, date):
    # 気象情報API連携
    return "晴れ時々曇り (降水確率 20%)"


# --- メイン検索処理 ---
if search_btn:
    st.info(
        f"📅 {target_date.strftime('%Y年%m月%d日')} の各空港受け入れ態勢を照会中..."
    )
    progress_bar = st.progress(0)

    matched_airports = []

    for idx, ap in enumerate(AIRPORT_DB):
        time.sleep(0.2)  # スキャン演出用ウェイト

        # 1. 車両判定
        car_ok, car_msg = check_car_availability(
            ap, target_date, times_car_models, allow_rental
        )

        # 2. 宿泊判定
        hotel_ok, hotel_msg = check_hotel_availability(
            ap, target_date, budget_max, need_buffet, need_onsen
        )

        # 3. 天気取得
        weather_msg = check_weather(ap, target_date)

        # 全条件クリアで合格リストに追加
        if car_ok and hotel_ok:
            matched_airports.append(
                {
                    "airport": ap,
                    "car_msg": car_msg,
                    "hotel_msg": hotel_msg,
                    "weather": weather_msg,
                }
            )

        progress_bar.progress((idx + 1) / len(AIRPORT_DB))

    st.success(
        f"全判定が完了しました。条件を満たす空港: {len(matched_airports)} / {len(AIRPORT_DB)} 件"
    )

    # --- 結果表示 ---
    st.subheader("✅ どこかにマイルで狙える「合格空港」リスト")

    if not matched_airports:
        st.warning(
            "指定された日付・条件に合致する空港が見つかりませんでした。条件を緩和して再検索してください。"
        )
    else:
        for item in matched_airports:
            ap = item["airport"]
            with st.expander(
                f"✈️ 【{ap['name']} ({ap['code']})】 - {ap['region']}エリア",
                expanded=True,
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**🚗 移動手段（車両）**")
                    st.write(ap["station"])
                    st.caption(f"ステータス: {item['car_msg']}")

                with col2:
                    st.markdown("**🏨 宿泊施設（1泊2食/温泉）**")
                    st.write(item["hotel_msg"])

                with col3:
                    st.markdown("**🌤 天気予報（4日後）**")
                    st.write(item["weather"])

                st.divider()
                st.markdown(
                    f"[📲 タイムズカーで予約](https://share.timescar.jp/) | [🏨 楽天トラベルで宿確認](https://travel.rakuten.co.jp/) | [☀️ 天気予報詳細](https://tenki.jp/)"
                )
