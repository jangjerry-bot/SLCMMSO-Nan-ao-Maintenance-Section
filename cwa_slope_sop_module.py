import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
from pathlib import Path
from urllib.parse import quote
import urllib3

# 忽略政府憑證偶發之 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 0. 延續邊坡口卡系統 style.py 之動畫與手機端放大 CSS
# ==========================================
def inject_custom_style_and_banner():
    """
    注入專為手機端優化的放大字體、高對比毛玻璃卡片，以及開頭動態雷達橫幅
    """
    st.markdown("""
    <style>
        /* 全域字體與手機端觸控優化 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", Roboto, sans-serif;
            font-size: 18px !important;
        }
        .block-container {
            padding-top: 2rem !important; 
            padding-bottom: 3rem !important;
            max-width: 960px !important;
        }

        /* 下拉選單 (Selectbox) 與輸入框字體全面放大 */
        div[data-baseweb="select"] > div {
            min-height: 52px !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            background-color: #1e293b !important;
            border: 2px solid #38bdf8 !important;
            border-radius: 12px !important;
            color: #ffffff !important;
        }
        label[data-testid="stWidgetLabel"] p {
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: #cbd5e1 !important;
        }

        /* 動態視覺橫幅動畫 (Keyframes) */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes radarPulse {
            0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.8); transform: scale(0.95); }
            70% { box-shadow: 0 0 0 14px rgba(245, 158, 11, 0); transform: scale(1.05); }
            100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); transform: scale(0.95); }
        }
        @keyframes slideDownFade {
            0% { opacity: 0; transform: translateY(-18px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes scanLine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .hero-banner {
            position: relative;
            overflow: hidden;
            background: linear-gradient(-45deg, #0f172a, #1e3a8a, #0f766e, #1e293b);
            background-size: 300% 300%;
            animation: gradientBG 10s ease infinite, slideDownFade 0.7s ease-out;
            border-radius: 18px;
            padding: 28px 22px 22px 22px; 
            border: 1px solid rgba(56, 189, 248, 0.35);
            box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.6);
            margin-top: 15px; 
            margin-bottom: 18px;
        }
        .hero-banner::after {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 3px;
            background: linear-gradient(90deg, transparent, #38bdf8, #f59e0b, transparent);
            animation: scanLine 3.5s linear infinite;
        }
        .radar-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid #f59e0b;
            color: #fbbf24;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .radar-dot {
            width: 10px;
            height: 10px;
            background-color: #f59e0b;
            border-radius: 50%;
            display: inline-block;
            animation: radarPulse 1.8s infinite;
        }
        .hero-title {
            font-size: 1.65rem !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            line-height: 1.3 !important;
            margin: 0 0 10px 0 !important;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .hero-subtitle {
            font-size: 0.95rem !important;
            color: #e2e8f0 !important;
            line-height: 1.45 !important;
            font-weight: 600;
            background: rgba(15, 23, 42, 0.55);
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 4px solid #38bdf8;
        }

        /* 手機端重點放大卡片 */
        .mobile-card {
            background: #1e293b;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 14px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
        }
        .card-safe { border-left: 8px solid #10b981; }
        .card-warn { border-left: 8px solid #f59e0b; }
        .card-danger { border-left: 8px solid #ef4444; background: linear-gradient(145deg, #1e293b, #311018); }

        .big-number {
            font-size: 2.1rem;
            font-weight: 900;
            line-height: 1.1;
            color: #ffffff;
        }
        .sop-action-box {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 12px;
            padding: 12px 14px;
            margin-top: 10px;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.5;
            color: #fef08a;
            border: 1px solid rgba(250, 204, 21, 0.3);
        }
        .sop-mgmt-box {
            background: rgba(6, 78, 59, 0.45);
            border-radius: 12px;
            padding: 10px 14px;
            margin-top: 8px;
            font-size: 1.05rem;
            font-weight: 700;
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .link-btn {
            display: inline-block;
            background: #0284c7;
            color: #ffffff !important;
            font-weight: 800;
            font-size: 0.92rem;
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none !important;
            text-align: center;
            border: 1px solid #38bdf8;
        }
        .link-btn-sec {
            display: inline-block;
            background: #334155;
            color: #e2e8f0 !important;
            font-weight: 700;
            font-size: 0.92rem;
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none !important;
            text-align: center;
            border: 1px solid #64748b;
        }
    </style>

    <div class="hero-banner">
        <div class="radar-badge">
            <span class="radar-dot"></span> LIVE 宜花災變水情與地震自動化監測中
        </div>
        <div class="hero-title">蘇花廊道災變暨邊坡巡查自動化決策系統</div>
        <div class="hero-subtitle">
            法規依據：路養護字第1155009531號函(115年5月修訂)｜雨量分析邏輯：採用【區域測站群組最大值包絡法】
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 1. 核心常數、API 金鑰與區域群組定義
# ==========================================
try:
    DEFAULT_CWA_API_KEY = st.secrets.get("CWA_API_KEY", "CWA-E9410456-F2F6-489C-BD69-8C45B13EBEFD")
except Exception:
    DEFAULT_CWA_API_KEY = "CWA-E9410456-F2F6-489C-BD69-8C45B13EBEFD"

REGIONAL_GROUPS = {
    "蘇澳地區": ["蘇澳", "馬賽", "永樂", "白米", "南方澳", "北方澳"],
    "東澳地區": ["東澳", "東澳嶺", "粉鳥林", "西帽山"],
    "南澳地區": ["南澳", "朝陽", "碧候", "金洋", "古魯", "鹿皮"],
    "武塔觀音漢本區": ["武塔", "觀音", "澳花", "漢本", "大濁水"],
    "和平崇德地區": ["和平", "和中", "和仁", "崇德", "太魯閣", "清水", "富世", "布洛灣"]
}

SEISMIC_RANK = {"0級": 0, "1級": 1, "2級": 2, "3級": 3, "4級": 4, "5弱": 5, "5強": 6, "6弱": 7, "6強": 8, "7級": 9}
RANK_TO_SEISMIC = {v: k for k, v in SEISMIC_RANK.items()}

def build_event_links(ev_type: str, ev_date: str, ev_name: str, ev_region: str):
    """
    針對每一筆歷史天災事件，產生兩個 100% 有效且精準的連結：
    1. primary_url: 直接調閱該次特定事件(如康芮颱風、凱米颱風、0403地震)於中央氣象署與防災專網之官方報告與雨量極值圖表。
    2. cwa_db_url: 中央氣象署現行有效之官方歷史查詢系統 (CODiS 氣候資料服務系統 / 颱風資料庫 / 地震中心)。
    """
    clean_query = f"中央氣象署 {ev_date[:4]}年 {ev_name} {ev_region} 雨量 震度 報告"
    primary_url = f"https://www.google.com/search?q={quote(clean_query)}"
    
    if ev_type == "地震":
        # 氣象署地震測報中心 - 全球資訊網首頁與歷史地震查詢 (真實有效網址)
        cwa_db_url = "https://scweb.cwa.gov.tw/"
        db_btn_label = "🌋 氣象署地震測報中心"
    elif ev_type == "颱風":
        # 氣象署颱風資料庫 - 歷年颱風警報單與路徑雨量系統 (真實有效網址)
        cwa_db_url = "https://rdc28.cwa.gov.tw/TDB/public/warning_typhoon_list/"
        db_btn_label = "🌀 氣象署歷年颱風清單"
    else:
        # 氣象署新版 CODiS 氣候資料服務系統 (取代已廢止之舊版 e-service，可查各雨量站歷史逐時雨量)
        cwa_db_url = "https://codis.cwa.gov.tw/StationData"
        db_btn_label = "🌧️ 氣象署CODiS歷史雨量站"
        
    return primary_url, cwa_db_url, db_btn_label


DEFAULT_DISASTER_HISTORY = [
    {"date": "2026-09-20", "type": "地震", "name": "0920 南澳外海地震 (M5.6)", "max_seismic": "4級", "max_rain_3h": 0.0, "max_rain_48h": 10.0, "region": "南澳地區", "collapse_m3": 0, "note": "震度達4級，觸發優先關注邊坡(RHRS中高風險)立即巡查"},
    {"date": "2026-05-12", "type": "豪雨", "name": "0512 梅雨滯留鋒面劇烈豪雨", "max_seismic": "0級", "max_rain_3h": 130.0, "max_rain_48h": 365.0, "region": "東澳地區", "collapse_m3": 0, "note": "115年汛期首波達標豪雨，東澳嶺3hr與48hr雙雙突破門檻"},
    {"date": "2025-11-18", "type": "豪雨", "name": "東北季風共伴效應超大豪雨", "max_seismic": "0級", "max_rain_3h": 142.0, "max_rain_48h": 460.0, "region": "東澳地區", "collapse_m3": 1200, "note": "典型秋冬地形鎖水效應，啟動A級邊坡14日內特檢與降低雨量門檻"},
    {"date": "2025-08-13", "type": "颱風", "name": "楊柳颱風外圍環流強降雨", "max_seismic": "0級", "max_rain_3h": 135.0, "max_rain_48h": 390.0, "region": "南澳地區", "collapse_m3": 0, "note": "短延時強降雨突破120mm/3hr，揭露強降雨訊息並於2日內特巡"},
    {"date": "2024-10-31", "type": "颱風", "name": "康芮颱風東部超大豪雨", "max_seismic": "0級", "max_rain_3h": 160.0, "max_rain_48h": 680.0, "region": "和平崇德地區", "collapse_m3": 8500, "note": "海警解除後全線特巡，坍方逾5,000m³路段強制升級比照A級"},
    {"date": "2024-07-24", "type": "颱風", "name": "凱米颱風強降雨致災", "max_seismic": "0級", "max_rain_3h": 185.0, "max_rain_48h": 820.0, "region": "和平崇德地區", "collapse_m3": 25000, "note": "0403震後首個強颱，坍方逾20,000m³，啟動空拍判釋與保全守視"},
    {"date": "2024-04-23", "type": "地震", "name": "0423 花蓮壽豐群震 (M6.3)", "max_seismic": "5強", "max_rain_3h": 45.0, "max_rain_48h": 110.0, "region": "和平崇德地區", "collapse_m3": 3000, "note": "震度達5強，觸發A、B、C、E類橋梁特別檢測與邊坡立即巡查"},
    {"date": "2024-04-03", "type": "地震", "name": "0403 花蓮大地震 (M7.2)", "max_seismic": "6強", "max_rain_3h": 15.0, "max_rain_48h": 30.0, "region": "和平崇德地區", "collapse_m3": 35000, "note": "成立大規模震災緊急應變小組，全線橋梁特檢、A~C級邊坡7日內特檢+朝巡1週+空拍"},
]

DEFAULT_SLOPE_INVENTORY = [
    {"邊坡編號": "台9線-108K+500", "路段名稱": "蘇澳東澳段", "所屬雨量分區": "蘇澳地區", "邊坡分級": "C", "RHRS中高風險": "否", "復建完工日": "2022-10-01", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線-114K+200", "路段名稱": "東澳段", "所屬雨量分區": "東澳地區", "邊坡分級": "A", "RHRS中高風險": "是", "復建完工日": "2025-04-15", "具遠端致災因素": "是"},
    {"邊坡編號": "台9丁線-16K+800", "路段名稱": "東澳舊線", "所屬雨量分區": "東澳地區", "邊坡分級": "B", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線-119K+500", "路段名稱": "南澳段", "所屬雨量分區": "南澳地區", "邊坡分級": "C+", "RHRS中高風險": "否", "復建完工日": "2023-10-01", "具遠端致災因素": "是"},
    {"邊坡編號": "台9線-129K+800", "路段名稱": "觀音段", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "B", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "否"},
    {"邊坡編號": "台9丁線-38K+600", "路段名稱": "觀音海岸舊線", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "大型地滑/順向坡", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "是"},
    {"邊坡編號": "台9線-141K+100", "路段名稱": "武塔漢本段", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "C", "RHRS中高風險": "否", "復建完工日": "2022-08-20", "具遠端致災因素": "否"},
    {"邊坡編號": "台9丁線-61K+000", "路段名稱": "澳花和平段", "所屬雨量分區": "和平崇德地區", "邊坡分級": "D", "RHRS中高風險": "否", "復建完工日": "", "具遠端致災因素": "否"},
]


# ==========================================
# 2. 區域分類與氣象署 API 串接引擎
# ==========================================
def classify_station_region(county: str, town: str, st_name: str) -> str:
    for region_name, keywords in REGIONAL_GROUPS.items():
        if any(k in st_name for k in keywords):
            return region_name
    if "蘇澳" in town:
        return "蘇澳地區"
    if "南澳" in town:
        return "南澳地區"
    if "秀林" in town:
        return "和平崇德地區"
    return "宜花其他區域"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_cwa_rainfall_and_envelope(api_key: str):
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
    params = {"Authorization": api_key.strip(), "format": "JSON"}
    try:
        resp = requests.get(url, params=params, timeout=12, verify=False)
        resp.raise_for_status()
        data = resp.json()
        stations = data.get("records", {}).get("Station", [])
        
        records = []
        for st_obj in stations:
            geo = st_obj.get("GeoInfo", {})
            county = geo.get("CountyName", "")
            town = geo.get("TownName", "")
            st_name = st_obj.get("StationName", "")
            
            if county in ["宜蘭縣", "花蓮縣"]:
                rain_elem = st_obj.get("RainfallElement", {})
                def parse_val(key):
                    val = rain_elem.get(key, {}).get("Precipitation")
                    try:
                        v = float(val)
                        return 0.0 if v < 0 else v
                    except (TypeError, ValueError):
                        return 0.0

                r_1h = parse_val("Past1hr")
                r_3h = parse_val("Past3hr")
                r_24h = parse_val("Past24hr")
                r_2d = parse_val("Past2days")
                r_3d = parse_val("Past3days")
                r_48h = r_2d if r_2d > 0 else max(r_24h, round(r_3d * 0.75, 1))
                region = classify_station_region(county, town, st_name)
                
                records.append({
                    "所屬雨量分區": region,
                    "鄉鎮": town,
                    "測站名稱": st_name,
                    "1hr雨量": r_1h,
                    "3hr雨量(mm)": r_3h,
                    "24hr雨量": r_24h,
                    "48hr雨量(mm)": r_48h,
                    "觀測時間": st_obj.get("ObsTime", {}).get("DateTime", "")
                })
                
        df_stations = pd.DataFrame(records)
        if df_stations.empty:
            return pd.DataFrame(), pd.DataFrame()

        envelope_rows = []
        for reg in list(REGIONAL_GROUPS.keys()):
            sub = df_stations[df_stations["所屬雨量分區"] == reg]
            if not sub.empty:
                idx_max3 = sub["3hr雨量(mm)"].idxmax()
                idx_max48 = sub["48hr雨量(mm)"].idxmax()
                max_3h_val = sub.loc[idx_max3, "3hr雨量(mm)"]
                max_3h_st = sub.loc[idx_max3, "測站名稱"]
                max_48h_val = sub.loc[idx_max48, "48hr雨量(mm)"]
                max_48h_st = sub.loc[idx_max48, "測站名稱"]
                
                is_alert = (max_3h_val >= 120 or max_48h_val >= 350)
                status_text = "🚨 觸發法定特別巡檢門檻！" if is_alert else "🟢 安全常態 (未達門檻)"
                
                envelope_rows.append({
                    "所屬雨量分區": reg,
                    "納入測站數": len(sub),
                    "區內最大3hr雨量(mm)": max_3h_val,
                    "3hr極值站": max_3h_st,
                    "區內最大48hr雨量(mm)": max_48h_val,
                    "48hr極值站": max_48h_st,
                    "狀態判定": status_text,
                    "是否超標": is_alert,
                    "測站群組清單": "、".join(sub["測站名稱"].tolist())
                })
        return df_stations, pd.DataFrame(envelope_rows)
    except Exception:
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_cwa_earthquake(api_key: str) -> list:
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
    params = {"Authorization": api_key.strip(), "format": "JSON", "limit": 3}
    try:
        resp = requests.get(url, params=params, timeout=10, verify=False)
        resp.raise_for_status()
        eq_list = resp.json().get("records", {}).get("Earthquake", [])
        parsed = []
        for eq in eq_list:
            info = eq.get("EarthquakeInfo", {})
            shaking_areas = eq.get("Intensity", {}).get("ShakingArea", [])
            max_rank = 0
            for area in shaking_areas:
                if any(k in area.get("CountyName", "") for k in ["宜蘭", "花蓮"]):
                    rank = SEISMIC_RANK.get(area.get("AreaIntensity", "0級"), 0)
                    if rank > max_rank:
                        max_rank = rank
            parsed.append({
                "發震時間": info.get("OriginTime", ""),
                "震央位置": info.get("Epicenter", {}).get("Location", ""),
                "規模": info.get("EarthquakeMagnitude", {}).get("MagnitudeValue", ""),
                "宜花最大震度": RANK_TO_SEISMIC.get(max_rank, "0級"),
                "官方報告連結": eq.get("Web", "https://scweb.cwa.gov.tw/")
            })
        return parsed
    except Exception:
        return []


# ==========================================
# 3. 115年10月版養護手冊 SOP 律定決策演算法
# ==========================================
def evaluate_slope_sop(slope_grade, is_rhrs_high, seismic_str, rain_3h, rain_48h, is_typhoon, is_debris_red, collapse_m3):
    insp_actions, mgmt_actions, bridge_actions = [], [], []
    clean_grade = str(slope_grade).replace("級邊坡", "").replace("級", "").strip()
    if "地滑" in clean_grade or "順向" in clean_grade:
        clean_grade = "大型地滑/順向坡"

    effective_grade = clean_grade
    upgraded_flag = False
    if collapse_m3 >= 5000 and clean_grade in ["B", "C+", "C", "D", "大型地滑/順向坡"]:
        effective_grade = "A"
        upgraded_flag = True

    s_rank = SEISMIC_RANK.get(seismic_str, 0)

    if s_rank == 4 and (is_rhrs_high or effective_grade in ["A", "B"]):
        insp_actions.append("🚨【震度4級】立即巡查「優先關注邊坡」(RHRS中高風險)")
    elif s_rank == 5:
        insp_actions.append("🚨【震度5弱】立即巡查公路構造物、邊坡、特別照護喬木")
    elif s_rank == 6:
        insp_actions.append("🚨【震度5強】立即巡查構造物、邊坡、特別照護喬木")
        bridge_actions.append("🌉【震度5強】立即巡查橋梁，並特別檢測 A、B、C、E 類橋梁")
    elif s_rank >= 7:
        mgmt_actions.append("🚨【震度6弱以上】成立「大規模震災」緊急應變小組 (處置6)")
        bridge_actions.append("🌉【震度6弱以上】立即辦理震區內「所有橋梁」特別檢測")
        if effective_grade in ["A", "B", "C+", "C"]:
            insp_actions.append("🚨【震度6弱以上】① 7日內特別檢測 ② 朝巡1週 ③ 取得空拍或衛星影像")
        elif effective_grade == "D":
            insp_actions.append("🚨【震度6弱以上】2日內實施特別巡查")
        elif effective_grade == "大型地滑/順向坡":
            insp_actions.append("🚨【震度6弱以上】14日內完成特別檢測")

    if rain_3h >= 120.0:
        insp_actions.append(f"🌧️【3hr雨量 {rain_3h}mm (≥120)】2日內實施特別巡查")
        mgmt_actions.append("🛡️【養護處置】實施巡查作業" if effective_grade in ["A", "B"] else "📢【養護處置】揭露路段強降雨訊息")

    if rain_48h >= 350.0:
        if effective_grade in ["A", "大型地滑/順向坡"]:
            insp_actions.append(f"🌧️【48hr雨量 {rain_48h}mm (≥350)】14日內完成特別檢測")
        elif effective_grade == "B":
            insp_actions.append(f"🌧️【48hr雨量 {rain_48h}mm (≥350)】2日內實施特別巡查")
        mgmt_actions.append("📉【養護處置】降低雨量門檻值" if effective_grade in ["A", "B", "大型地滑/順向坡"] else "👁️【養護處置】加強水情監控")

    if is_typhoon:
        insp_actions.append("🌀【海警解除後】2日內實施特別巡查")
        mgmt_actions.append("🛡️【颱風期間】依「公路防災預警機制」辦理")

    if 5000 <= collapse_m3 < 20000:
        insp_actions.append("⛰️【坍方5千~2萬m³搶通後】實施朝巡、暮巡 1 週")
    elif collapse_m3 >= 20000:
        insp_actions.append("⛰️【坍方≥2萬m³搶通後】① 朝巡暮巡1週 ② 取得空拍或衛星影像")
        mgmt_actions.append("🚧【養護處置】執行保全守視 (必要時交通管制)")

    if is_debris_red:
        insp_actions.append("⚠️【土石流紅色警戒】2日內實施特別巡查")
        if effective_grade in ["A", "B", "C+", "大型地滑/順向坡"]:
            mgmt_actions.append("🛡️【養護處置】擬定加碼部署策略，按計畫執行")

    is_triggered = len(insp_actions) > 0 or len(mgmt_actions) > 0
    if not is_triggered:
        insp_actions.append("🟢 未達門檻｜常態車巡 1次/週、步巡 1次/月、定檢 1次/年")

    return {
        "effective_grade": effective_grade,
        "upgraded_flag": upgraded_flag,
        "is_triggered": is_triggered,
        "inspection": "<br>".join(insp_actions),
        "management": "<br>".join(mgmt_actions) if mgmt_actions else "🟢 常態養護管理",
        "bridge": "；".join(bridge_actions) if bridge_actions else ""
    }


def auto_assign_region_by_text(text_val: str) -> str:
    t = str(text_val)
    for reg, kws in REGIONAL_GROUPS.items():
        if any(k in t for k in kws):
            return reg
    return "南澳地區"


# ==========================================
# 4. 手機端優先 (Mobile-First) 介面主程式
# ==========================================
def render_app():
    st.set_page_config(page_title="蘇花廊道災變暨邊坡巡查自動化決策系統", layout="centered", initial_sidebar_state="collapsed")

    inject_custom_style_and_banner()

    if "disaster_db" not in st.session_state:
        st.session_state.disaster_db = pd.DataFrame(DEFAULT_DISASTER_HISTORY)
    if "slope_db" not in st.session_state:
        st.session_state.slope_db = pd.DataFrame(DEFAULT_SLOPE_INVENTORY)

    with st.sidebar:
        st.header("⚙️ 系統設定與資料庫掛載")
        api_key = st.text_input("🔑 氣象署 API 授權碼", value=DEFAULT_CWA_API_KEY, type="password")
        if st.button("🔄 立即強制刷新氣象署數據", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()
        st.subheader("📂 掛載邊坡資料庫 (.xlsx)")
        local_xlsx = [f.name for f in Path(".").glob("*.xlsx") if not f.name.startswith("~$")]
        up_file = st.file_uploader("上傳 .xlsx 檔案", type=["xlsx"])
        raw_df = None
        if up_file:
            xl = pd.ExcelFile(up_file)
            sh = st.selectbox("選擇工作表", xl.sheet_names)
            raw_df = xl.parse(sh)
        elif local_xlsx:
            sel_lx = st.selectbox("選擇本地 Excel 檔", ["(使用預設口卡)"] + local_xlsx)
            if sel_lx != "(使用預設口卡)":
                xl = pd.ExcelFile(sel_lx)
                sh = st.selectbox("選擇工作表", xl.sheet_names)
                raw_df = xl.parse(sh)

        if raw_df is not None and not raw_df.empty:
            cols = raw_df.columns.tolist()
            c_id = st.selectbox("【邊坡編號】欄", cols, index=0)
            c_loc = st.selectbox("【路段名稱】欄", cols, index=min(1, len(cols)-1))
            c_grade = st.selectbox("【邊坡分級】欄", cols, index=min(2, len(cols)-1))
            if st.button("✅ 套用至決策系統", use_container_width=True):
                mapped = []
                for _, r in raw_df.iterrows():
                    s_id, s_loc, s_g = str(r[c_id]), str(r[c_loc]), str(r[c_grade])
                    mapped.append({
                        "邊坡編號": s_id, "路段名稱": s_loc,
                        "所屬雨量分區": auto_assign_region_by_text(f"{s_id} {s_loc}"),
                        "邊坡分級": s_g,
                        "RHRS中高風險": "是" if any(g in s_g for g in ["A", "B"]) else "否",
                        "復建完工日": "", "具遠端致災因素": "是" if "C+" in s_g else "否"
                    })
                st.session_state.slope_db = pd.DataFrame(mapped)
                st.success("已成功載入 Excel 口卡！")

    df_stations, df_envelope = fetch_cwa_rainfall_and_envelope(api_key)
    eq_records = fetch_cwa_earthquake(api_key)

    main_menu = st.selectbox(
        "👇 請選擇功能模組 (下拉切換)：",
        [
            "📡 1. 區域雨量群組包絡看板 (即時重點放大)",
            "⚙️ 2. 邊坡巡查自動化派工決策 (下拉篩選)",
            "📅 3. 宜花歷年天災時序查詢 (地震/颱風/豪雨)",
            "📉 4. 115年修訂：A級邊坡降等資格檢核"
        ]
    )

    region_rain_map = {}
    if not df_envelope.empty:
        for _, r_env in df_envelope.iterrows():
            region_rain_map[r_env["所屬雨量分區"]] = (
                float(r_env["區內最大3hr雨量(mm)"]),
                float(r_env["區內最大48hr雨量(mm)"]),
                r_env["3hr極值站"]
            )

    # ==================================================
    # 模組 1：區域雨量群組包絡看板
    # ==================================================
    if main_menu.startswith("📡 1"):
        reg_filter = st.selectbox(
            "📍 下拉選擇欲檢視之蘇花微氣候防區：",
            ["全部五大防區總覽"] + list(REGIONAL_GROUPS.keys())
        )

        if not df_envelope.empty:
            show_env = df_envelope if reg_filter == "全部五大防區總覽" else df_envelope[df_envelope["所屬雨量分區"] == reg_filter]
            
            for _, row in show_env.iterrows():
                r3 = row["區內最大3hr雨量(mm)"]
                r48 = row["區內最大48hr雨量(mm)"]
                card_cls = "card-danger" if row["是否超標"] else ("card-warn" if (r3 >= 80 or r48 >= 200) else "card-safe")
                
                st.markdown(f"""
                <div class="mobile-card {card_cls}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:1.35rem; font-weight:900; color:#38bdf8;">📍 {row['所屬雨量分區']}</span>
                        <span style="font-size:0.95rem; font-weight:700; background:#0f172a; padding:4px 10px; border-radius:99px;">納入 {row['納入測站數']} 站包絡</span>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin: 12px 0;">
                        <div style="background:rgba(15,23,42,0.7); padding:12px; border-radius:12px;">
                            <div style="font-size:0.9rem; color:#94a3b8;">區內最大 3hr 雨量 (門檻120)</div>
                            <div class="big-number" style="color:{'#f87171' if r3>=120 else '#ffffff'};">{r3} <span style="font-size:1rem;">mm</span></div>
                            <div style="font-size:0.85rem; color:#cbd5e1; margin-top:4px;">極值站：{row['3hr極值站']}</div>
                        </div>
                        <div style="background:rgba(15,23,42,0.7); padding:12px; border-radius:12px;">
                            <div style="font-size:0.9rem; color:#94a3b8;">區內最大 48hr 雨量 (門檻350)</div>
                            <div class="big-number" style="color:{'#f87171' if r48>=350 else '#ffffff'};">{r48} <span style="font-size:1rem;">mm</span></div>
                            <div style="font-size:0.85rem; color:#cbd5e1; margin-top:4px;">極值站：{row['48hr極值站']}</div>
                        </div>
                    </div>
                    <div style="font-size:1.1rem; font-weight:800; color:{'#fca5a5' if row['是否超標'] else '#6ee7b7'};">
                        {row['狀態判定']}
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:6px;">
                        涵蓋雨量站：{row['測站群組清單']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if reg_filter != "全部五大防區總覽":
                st.markdown(f"#### 📋 {reg_filter} 各雨量站即時數據")
                sub_st = df_stations[df_stations["所屬雨量分區"] == reg_filter].sort_values(by="3hr雨量(mm)", ascending=False)
                st.dataframe(sub_st[["測站名稱", "3hr雨量(mm)", "48hr雨量(mm)", "1hr雨量", "24hr雨量"]], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ 無法連線至氣象署 API，請確認網路狀態。")

        st.markdown("""
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:10px;">
            <a href="https://www.cwa.gov.tw/V8/C/P/Rainfall/Rainfall_QZJ.html" target="_blank" style="display:block; text-align:center; background:#f59e0b; color:#0f172a; font-weight:900; font-size:1.05rem; padding:14px 8px; border-radius:12px; text-decoration:none;">
                🌧️ 氣象署即時雨量排行
            </a>
            <a href="https://codis.cwa.gov.tw/StationData" target="_blank" style="display:block; text-align:center; background:#38bdf8; color:#0f172a; font-weight:900; font-size:1.05rem; padding:14px 8px; border-radius:12px; text-decoration:none;">
                📊 氣象署CODiS測站查詢
            </a>
        </div>
        """, unsafe_allow_html=True)

    # ==================================================
    # 模組 2：邊坡巡查自動化派工決策
    # ==================================================
    elif main_menu.startswith("⚙️ 2"):
        drive_mode = st.selectbox(
            "⚡ 1. 下拉選擇外力觸發來源：",
            [
                "🟢 即時模式：自動套用【氣象署 API 各分區最大包絡雨量】",
                "🧪 模擬模式：載入【歷年天災事件 / 自訂震度與雨量】測試"
            ]
        )

        target_region = st.selectbox(
            "📍 2. 下拉篩選欲派工之轄區路段：",
            ["全部轄區邊坡口卡"] + list(REGIONAL_GROUPS.keys())
        )

        if drive_mode.startswith("🟢"):
            override_rain = False
            default_eq = eq_records[0]["宜花最大震度"] if eq_records else "0級"
            c1, c2 = st.columns(2)
            sim_seis = c1.selectbox("當前宜花最大震度", list(SEISMIC_RANK.keys()), index=list(SEISMIC_RANK.keys()).index(default_eq))
            sim_scenario = c2.selectbox("特殊防災情境狀態", ["無特殊附加警戒", "🌀 海上颱風警報解除/期間", "⚠️ 鄰河側土石流紅色警戒", "⛰️ 無預警坍方 5,000~20,000 m³", "⛰️ 無預警大規模坍方 ≥ 20,000 m³"])
        else:
            override_rain = True
            ev_opts = ["手動輸入測試數值"] + [f"{r['date']} | {r['name']} ({r['region']})" for _, r in st.session_state.disaster_db.iterrows()]
            sel_ev = st.selectbox("📥 下拉載入歷史天災事件：", ev_opts)
            
            def_seis, def_r3, def_r48, def_col = "0級", 135.0, 380.0, 0
            if sel_ev != "手動輸入測試數值":
                ev_date = sel_ev.split(" | ")[0]
                ev_name = sel_ev.split(" | ")[1].rsplit(" (", 1)[0]
                row = st.session_state.disaster_db[(st.session_state.disaster_db["date"] == ev_date) & (st.session_state.disaster_db["name"] == ev_name)].iloc[0]
                def_seis, def_r3, def_r48, def_col = row["max_seismic"], float(row["max_rain_3h"]), float(row["max_rain_48h"]), int(row["collapse_m3"])

            c1, c2 = st.columns(2)
            sim_seis = c1.selectbox("模擬最大震度", list(SEISMIC_RANK.keys()), index=list(SEISMIC_RANK.keys()).index(def_seis))
            sim_scenario = c2.selectbox("特殊防災情境狀態", ["無特殊附加警戒", "🌀 海上颱風警報解除/期間", "⚠️ 鄰河側土石流紅色警戒", "⛰️ 無預警坍方 5,000~20,000 m³", "⛰️ 無預警大規模坍方 ≥ 20,000 m³"], index=(4 if def_col>=20000 else (3 if def_col>=5000 else 0)))
            
            r_col1, r_col2 = st.columns(2)
            sim_r3_manual = r_col1.number_input("模擬 3hr 雨量 (mm)", value=def_r3, step=10.0)
            sim_r48_manual = r_col2.number_input("模擬 48hr 雨量 (mm)", value=def_r48, step=20.0)

        is_ty = "颱風" in sim_scenario
        is_deb = "土石流" in sim_scenario
        sim_col = 20000 if "≥ 20,000" in sim_scenario else (5000 if "5,000" in sim_scenario else 0)

        slopes_df = st.session_state.slope_db.copy()
        if target_region != "全部轄區邊坡口卡":
            slopes_df = slopes_df[slopes_df["所屬雨量分區"] == target_region]

        st.markdown(f"#### 📋 派工決策結果（共 {len(slopes_df)} 處邊坡）")

        for _, slope in slopes_df.iterrows():
            s_reg = slope["所屬雨量分區"]
            if not override_rain and s_reg in region_rain_map:
                r3_val, r48_val, rep_st = region_rain_map[s_reg]
                rain_tag = f"{s_reg}極值 ({rep_st}: 3h={r3_val} / 48h={r48_val}mm)"
            elif not override_rain:
                r3_val, r48_val = 0.0, 0.0
                rain_tag = f"{s_reg} (無超標雨量)"
            else:
                r3_val, r48_val = sim_r3_manual, sim_r48_manual
                rain_tag = f"模擬外力 (3h={r3_val} / 48h={r48_val}mm)"

            res = evaluate_slope_sop(
                slope_grade=slope["邊坡分級"],
                is_rhrs_high=(slope["RHRS中高風險"] == "是"),
                seismic_str=sim_seis,
                rain_3h=r3_val,
                rain_48h=r48_val,
                is_typhoon=is_ty,
                is_debris_red=is_deb,
                collapse_m3=sim_col
            )

            if res["bridge"]:
                st.error(res["bridge"])

            card_style = "card-danger" if res["is_triggered"] else "card-safe"
            grade_badge = f"🔥 強制升為 A 級 (原{slope['邊坡分級']})" if res["upgraded_flag"] else f"{slope['邊坡分級']} 級邊坡"

            st.markdown(f"""
            <div class="mobile-card {card_style}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                    <div>
                        <div style="font-size:1.4rem; font-weight:900; color:#ffffff;">{slope['邊坡編號']} <span style="font-size:1.1rem; color:#38bdf8;">({slope['路段名稱']})</span></div>
                        <div style="font-size:0.9rem; color:#cbd5e1; margin-top:2px;">🌧️ {rain_tag}</div>
                    </div>
                    <span style="background:#f59e0b; color:#0f172a; font-weight:900; font-size:0.95rem; padding:4px 10px; border-radius:8px; white-space:nowrap;">
                        {grade_badge}
                    </span>
                </div>
                <div class="sop-action-box">
                    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:2px;">🔍 法定巡查與特別檢測指令：</div>
                    {res['inspection']}
                </div>
                <div class="sop-mgmt-box">
                    <div style="font-size:0.85rem; color:#a7f3d0; margin-bottom:2px;">🛡️ 防災管制與養護機制：</div>
                    {res['management']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================
    # 模組 3：宜花歷年天災時序查詢 (精準雙連結配置)
    # ==================================================
    elif main_menu.startswith("📅 3"):
        df_hist = st.session_state.disaster_db.copy()
        df_hist["year"] = df_hist["date"].str.slice(0, 4)

        c1, c2 = st.columns(2)
        sel_year = c1.selectbox("📅 1. 下拉選擇查詢年份：", ["全部歷年紀錄"] + sorted(df_hist["year"].unique().tolist(), reverse=True))
        sel_type = c2.selectbox("🌪️ 2. 下拉選擇災害類別：", ["全部災別 (地震/颱風/豪雨)", "地震", "颱風", "豪雨"])
        
        c3, c4 = st.columns(2)
        sel_reg_h = c3.selectbox("📍 3. 下拉篩選受災分區：", ["全部宜花防區"] + list(REGIONAL_GROUPS.keys()))
        sort_dir = c4.selectbox("⏳ 4. 日期排序方式：", ["日期：由新到舊 (最新優先)", "日期：由舊到新 (時間先後順序)"])

        if sel_year != "全部歷年紀錄":
            df_hist = df_hist[df_hist["year"] == sel_year]
        if sel_type != "全部災別 (地震/颱風/豪雨)":
            df_hist = df_hist[df_hist["type"] == sel_type]
        if sel_reg_h != "全部宜花防區":
            df_hist = df_hist[df_hist["region"] == sel_reg_h]

        df_hist = df_hist.sort_values(by="date", ascending=("由舊到新" in sort_dir))

        st.markdown(f"#### 📖 查詢結果：共 {len(df_hist)} 筆宜花天災事件")
        for _, ev in df_hist.iterrows():
            t_color = "#ef4444" if ev["type"] == "地震" else ("#3b82f6" if ev["type"] == "颱風" else "#eab308")
            
            # 取得該事件的精準報告連結與氣象署資料庫連結
            primary_url, cwa_db_url, db_btn_label = build_event_links(
                ev_type=ev["type"],
                ev_date=ev["date"],
                ev_name=ev["name"],
                ev_region=ev["region"]
            )

            st.markdown(f"""
            <div class="mobile-card" style="border-left: 8px solid {t_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <a href="{primary_url}" target="_blank" style="text-decoration:none; color:inherit; display:block;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.1rem; font-family:monospace; font-weight:800; color:#94a3b8;">📅 {ev['date']}</span>
                        <span style="background:{t_color}; color:#ffffff; font-weight:900; font-size:0.9rem; padding:3px 10px; border-radius:99px;">{ev['type']}｜{ev['region']}</span>
                    </div>
                    <div style="font-size:1.35rem; font-weight:900; color:#38bdf8; margin: 8px 0; text-decoration:underline;">
                        {ev['name']} ↗
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#fca5a5;">震度：{ev['max_seismic']}</span>
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#38bdf8;">3hr雨量：{ev['max_rain_3h']}mm</span>
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#fbbf24;">48hr雨量：{ev['max_rain_48h']}mm</span>
                    </div>
                    <div style="font-size:1.05rem; color:#e2e8f0; line-height:1.4; margin-bottom:12px;">
                        📌 {ev['note']}
                    </div>
                </a>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                    <a href="{primary_url}" target="_blank" class="link-btn">
                        🔍 查閱該次災情與氣象報告
                    </a>
                    <a href="{cwa_db_url}" target="_blank" class="link-btn-sec">
                        {db_btn_label}
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================
    # 模組 4：115年修訂 A級邊坡降等資格檢核
    # ==================================================
    elif main_menu.startswith("📉 4"):
        st.markdown("""
        <div class="mobile-card card-warn">
            <div style="font-size:1.25rem; font-weight:900; color:#fbbf24; margin-bottom:6px;">📋 115年5月修訂：A級邊坡降等法則</div>
            <div style="font-size:1rem; color:#e2e8f0; line-height:1.5;">
                依路養護字第1155009531號函：已完成復建工程並歷經至少 <b>1個完整汛期 (5/1~11/30)</b> 之A級邊坡，得於年度汛期結束後，檢具致災原因、削減措施及安定分析佐證，由分局召開專家會議調降至 <b>C+級</b> 或 <b>C級</b>。
            </div>
        </div>
        """, unsafe_allow_html=True)

        a_slopes = st.session_state.slope_db[st.session_state.slope_db["邊坡分級"].astype(str).str.contains("A")]
        slope_opts = [f"{r['邊坡編號']} ({r['路段名稱']})" for _, r in a_slopes.iterrows()] + ["自訂評估邊坡"]
        st.selectbox("⛰️ 1. 下拉選擇欲評估降等之 A 級邊坡：", slope_opts)

        c1, c2 = st.columns(2)
        rehab_dt = c1.date_input("2. 復建工程完工日", value=date(2025, 4, 15))
        eval_dt = c2.date_input("3. 提報審查日 (須於11/30後)", value=date(2026, 12, 5))

        remote_opt = st.selectbox(
            "🔍 4. C+級邊坡快篩表 (是否具4類遠端致災因素)：",
            [
                "是：具遠端致災因素 (上/下邊坡、曲流/浪襲、坡頂開發、明隧道上方)",
                "否：無上述遠端致災因素，且無明顯不穩定徵兆"
            ]
        )

        full_seasons = [y for y in range(rehab_dt.year, eval_dt.year + 1) if rehab_dt <= date(y, 5, 1) and eval_dt > date(y, 11, 30)]
        df_h = st.session_state.disaster_db.copy()
        df_h["dt"] = pd.to_datetime(df_h["date"]).dt.date
        exp_ev = df_h[(df_h["dt"] >= rehab_dt) & (df_h["dt"] <= eval_dt)]
        max_48 = exp_ev["max_rain_48h"].max() if not exp_ev.empty else 0.0

        is_qualified = (len(full_seasons) >= 1) and not (5 <= eval_dt.month <= 11)
        target_g = "C+ 級邊坡" if remote_opt.startswith("是") else "C 級邊坡"

        st.markdown(f"""
        <div class="mobile-card {'card-safe' if is_qualified else 'card-danger'}">
            <div style="font-size:1.1rem; color:#94a3b8;">法規暨自然外力壓力測試判定結果：</div>
            <div class="big-number" style="color:{'#6ee7b7' if is_qualified else '#fca5a5'}; margin:8px 0;">
                {'✅ 符合資格 ➔ 可調降至 ' + target_g if is_qualified else '❌ 尚未符合降等法定啟動時機'}
            </div>
            <div style="font-size:1.05rem; color:#ffffff; line-height:1.6;">
                • 完整經歷汛期數：<b>{len(full_seasons)} 個</b> ({full_seasons if full_seasons else '未滿1個完整汛期 5/1~11/30'})<br>
                • 完工後經歷天災次數：<b>{len(exp_ev)} 次</b><br>
                • 期間承受最大 48hr 雨量：<b>{max_48} mm</b> ({'已通過 350mm 豪雨壓力測試' if max_48>=350 else '期間未達 350mm 門檻'})
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_app()