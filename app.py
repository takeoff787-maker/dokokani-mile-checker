import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="どこかにマイル 条件クリア空港 判定アプリ", page_icon="✈️", layout="wide")
st.title("✈️ どこかにマイル 条件クリア空港 判定アプリ")

# --- セッション状態の初期化 ---
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
    else:  # 2泊3日
        end_date = start_date + timedelta(days=2)
        
    end_time = st.time_input("帰着時間", datetime.strptime("18:00", "%H:%M").time())
    
    st.subheader("🚗 車両希望条件")
    times_car_models = st.multiselect(
        "希望特定車種（参考）",
        ["C-HR", "CX-30", "MAZDA3", "ヤリスクロス", "ノア", "ヴォクシー", "フィット/ヤリス等"],
        default=["C-HR", "CX-30", "MAZDA3", "ヤリスクロス"]
    )

# --- 全国主要どこかにマイル対象空港データベース（拡張版） ---
AIRPORT_DB = [
    # 北海道
    {"code": "CTS", "name": "新千歳空港", "region": "北海道", "type": "times", "stations": [{"name": "タイムズカー新千歳空港店", "models": ["C-HR", "CX-30", "MAZDA3", "ノア", "ヴォクシー"]}, {"name": "新千歳空港A駐車場", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["定山渓万世閣", "登別万世閣"]},
    {"code": "HKD", "name": "函館空港", "region": "北海道", "type": "times", "stations": [{"name": "函館空港駐車場", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["湯の川温泉 ホテル万惣"]},
    {"code": "AKJ", "name": "旭川空港", "region": "北海道", "type": "times", "stations": [{"name": "旭川空港前店", "models": ["ヤリスクロス", "フィット", "ノア"]}], "fav_hotels": ["層雲峡観光ホテル"]},
    {"code": "MMB", "name": "女満別空港", "region": "北海道", "type": "times", "stations": [{"name": "女満別空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["網走観光ホテル"]},
    {"code": "OBO", "name": "帯広空港", "region": "北海道", "type": "times", "stations": [{"name": "帯広空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["十勝川温泉 第一ホテル"]},
    {"code": "KUH", "name": "釧路空港", "region": "北海道", "type": "times", "stations": [{"name": "釧路空港前店", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["阿寒湖温泉 あかん遊久の里鶴雅"]},

    # 東北
    {"code": "AOJ", "name": "青森空港", "region": "東北", "type": "rental", "stations": [], "fav_hotels": ["浅虫温泉 宿屋つばき"]},
    {"code": "MSJ", "name": "三沢空港", "region": "東北", "type": "rental", "stations": [], "fav_hotels": ["星野リゾート 青森屋"]},
    {"code": "AXT", "name": "秋田空港", "region": "東北", "type": "times", "stations": [{"name": "秋田空港駐車場", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["男鹿温泉 ホテルきららか"]},
    {"code": "GAJ", "name": "山形空港", "region": "東北", "type": "times", "stations": [{"name": "山形空港前", "models": ["フィット", "ヤリス"]}], "fav_hotels": ["蔵王温泉 高見屋"]},
    {"code": "HNA", "name": "花巻空港", "region": "東北", "type": "times", "stations": [{"name": "花巻空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["花巻温泉 ホテル千秋閣"]},

    # 北陸・中国・四国
    {"code": "KMQ", "name": "小松空港", "region": "北陸", "type": "times", "stations": [{"name": "小松空港第一駐車場", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["加賀温泉郷 瑠璃光"]},
    {"code": "OKJ", "name": "岡山空港", "region": "中国", "type": "times", "stations": [{"name": "岡山空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["湯郷温泉 季譜の里"]},
    {"code": "HIJ", "name": "広島空港", "region": "中国", "type": "times", "stations": [{"name": "広島空港前", "models": ["MAZDA3", "CX-30", "ヤリスクロス", "ノア"]}], "fav_hotels": ["宮島温泉 錦水館"]},
    {"code": "IZO", "name": "出雲空港", "region": "中国", "type": "times", "stations": [{"name": "出雲空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["玉造温泉 佳翠苑皆美"]},
    {"code": "UBJ", "name": "山口宇部空港", "region": "中国", "type": "times", "stations": [{"name": "山口宇部空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["湯田温泉 松田屋ホテル"]},
    {"code": "TKM", "name": "高松空港", "region": "四国", "type": "times", "stations": [{"name": "高松空港前", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["琴平温泉 琴参閣"]},
    {"code": "MYJ", "name": "松山空港", "region": "四国", "type": "times", "stations": [{"name": "松山空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["道後温泉 ふなや"]},
    {"code": "TKS", "name": "徳島空港", "region": "四国", "type": "times", "stations": [{"name": "徳島空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["鳴門温泉 アオアヲナルトリゾート"]},
    {"code": "KCZ", "name": "高知空港", "region": "四国", "type": "times", "stations": [{"name": "高知空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["城西館"]},

    # 九州・沖縄
    {"code": "FUK", "name": "福岡空港", "region": "九州", "type": "times", "stations": [{"name": "福岡空港国内線前", "models": ["C-HR", "CX-30", "MAZDA3", "ノア"]}, {"name": "福岡空港国際線前", "models": ["ヤリスクロス", "ヴォクシー", "フィット"]}], "fav_hotels": ["原鶴温泉 泰泉閣"]},
    {"code": "KKJ", "name": "北九州空港", "region": "九州", "type": "times", "stations": [{"name": "北九州空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["ホテルクラウンパレス小倉"]},
    {"code": "OIT", "name": "大分空港", "region": "九州", "type": "times", "stations": [{"name": "大分空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["別府温泉 杉乃井ホテル"]},
    {"code": "NGS", "name": "長崎空港", "region": "九州", "type": "times", "stations": [{"name": "長崎空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["雲仙温泉 雲仙宮崎旅館"]},
    {"code": "KMJ", "name": "熊本空港", "region": "九州", "type": "times", "stations": [{"name": "熊本空港前", "models": ["CX-30", "ヤリスクロス", "フィット"]}], "fav_hotels": ["黒川温泉 ふじ屋"]},
    {"code": "KMI", "name": "宮崎空港", "region": "九州", "type": "times", "stations": [{"name": "宮崎空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["シェラトン・グランデ・オーシャンリゾート"]},
    {"code": "KOJ", "name": "鹿児島空港", "region": "九州", "type": "times", "stations": [{"name": "鹿児島空港前", "models": ["ヤリスクロス", "フィット", "ノート"]}], "fav_hotels": ["霧島温泉 霧島ホテル"]},
    {"code": "OKA", "name": "那覇空港", "region": "沖縄", "type": "times", "stations": [{"name": "那覇空港店（送迎あり）", "models": ["C-HR", "CX-30", "ヤリスクロス", "ノア", "ヴォクシー"]}], "fav_hotels": ["サザンビーチホテル＆リゾート沖縄"]},
    {"code": "MMY", "name": "宮古空港", "region": "沖縄", "type": "times", "stations": [{"name": "宮古空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["シギラベイサイドスイート アラマンダ"]},
    {"code": "ISG", "name": "新石垣空港", "region": "沖縄", "type": "times", "stations": [{"name": "石垣空港前", "models": ["ヤリスクロス", "フィット"]}], "fav_hotels": ["フサキビーチリゾート"]}
]

# --- MAIN PAGE ---
start_dt = datetime.combine(start_date, start_time)
end_dt = datetime.combine(end_date, end_time)

st.success(f"📅 【設定条件】{num_people}名利用 | {trip_type} | {start_dt.strftime('%Y/%m/%d %H:%M')} 〜 {end_dt.strftime('%m/%d %H:%M')}")

# ----------------------------------------------------
# STEP 1: ガチャ結果の4空港 絞り込み選択
# ----------------------------------------------------
st.markdown("### 🎲 ガチャ候補空港の絞り込み (出てきた4箇所にチェック)")
st.caption("どこかにマイルで提示された4つの空港にチェックを入れてください。")

selected_airports = []
cols = st.columns(4)

for idx, ap in enumerate(AIRPORT_DB):
    col_target = cols[idx % 4]
    with col_target:
        is_selected = st.checkbox(f"✈️ **{ap['name']} ({ap['code']})**", key=f"select_{ap['code']}")
        if is_selected:
            selected_airports.append(ap)

st.divider()

# ----------------------------------------------------
# STEP 2: 選択された空港の照会・手動判定
# ----------------------------------------------------
if not selected_airports:
    st.info("👆 上の全空港リストから、ガチャで出た候補空港（4箇所など）にチェックを入れてください。")
else:
    st.markdown(f"### 📋 選択中空港の照会＆最終判定 ({len(selected_airports)}件)")

    for ap in selected_airports:
        with st.container():
            st.markdown(f"#### ✈️ 【{ap['name']} ({ap['code']})】")
            
            c_chk1, c_chk2, c_res = st.columns([1, 1, 1.5])
            with c_chk1:
                car_ok = st.checkbox("🚗 車の空車 OK", key=f"car_ok_{ap['code']}")
            with c_chk2:
                if trip_type == "日帰り":
                    hotel_ok = True
                    st.caption("🏨 宿：日帰り不要")
                else:
                    hotel_ok = st.checkbox("🏨 宿の空室 OK", key=f"hotel_ok_{ap['code']}")
            
            with c_res:
                if car_ok and hotel_ok:
                    st.success("🎉 **最終判定：遂行可能 (OK)**")
                elif car_ok or hotel_ok:
                    st.warning("⏳ 最終判定：一部未確認")
                else:
                    st.error("❌ 最終判定：未確認 / 遂行不可")

            with st.expander(f"{ap['name']} の照会リンク＆ステーション詳細を開く"):
                col1, col2, col3 = st.columns([1.2, 1, 0.8])
                
                with col1:
                    st.markdown("**🚗 タイムズカー配備・空き照会**")
                    if ap["type"] == "times":
                        st.link_button("📲 マイページ（空車照会）へ", "https://share.timescar.jp/view/sp/member/mypage.jsp")
                        st.caption(f"※「{ap['name']}」で検索")
                        
                        for st_info in ap["stations"]:
                            st.write(f"📍 **{st_info['name']}**")
                            st.caption("配備: " + ", ".join(st_info["models"]))
                    else:
                        st.error("タイムズ非対応エリア")
                        st.link_button("📲 dカーシェア", "https://dcarshare.docomo.ne.jp/")

                with col2:
                    st.markdown(f"**🏨 温泉・バイキング宿 ({num_people}名設定)**")
                    if trip_type == "日帰り":
                        st.info("日帰りプランのため不要")
                    else:
                        st.write("**【登録中のお気に入り】**")
                        for h in ap["fav_hotels"]:
                            st.write(f"・ {h}")
                        
                        jalan_person_url = f"https://www.jalan.net/uw/uwp3000/uwp3001.do?keyword={ap['name']}+温泉+バイキング&adultNum={num_people}"
                        st.link_button(f"📲 じゃらんで空室確認 ({num_people}名)", jalan_person_url)

                with col3:
                    st.markdown("**🌤 現地天気**")
                    tenki_url = f"https://tenki.jp/search/?keyword={ap['name']}"
                    st.link_button("📲 天気予報を確認", tenki_url)
            
            st.divider()
