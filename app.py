import streamlit as st
import pandas as pd
import folium
from folium.plugins import LocateControl
from streamlit_folium import st_folium
import plotly.express as px
import os
import datetime
import zipfile
import xml.etree.ElementTree as ET
import re
import base64
from PIL import Image

# 1. 頁面設定
st.set_page_config(
    page_title="南澳段省道邊坡全生命週期資料庫",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 主題與狀態管理
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "🌙 深色黑底"
if "bottom_tab" not in st.session_state:
    st.session_state.bottom_tab = "📋 邊坡清冊"
if "selected_slope_id" not in st.session_state:
    st.session_state.selected_slope_id = None
if "active_grade_detail" not in st.session_state:
    st.session_state.active_grade_detail = None

is_light = (st.session_state.theme_mode == "☀️ 淺色白底")
plotly_font_color = "#0f172a" if is_light else "#f8fafc"

# 2. 動態主題 CSS
if is_light:
    theme_vars = """
        --bg-main: #f8fafc;
        --text-main: #0f172a;
        --text-muted: #475569;
        --card-bg: #ffffff;
        --card-border: #cbd5e1;
        --btn-sec-bg: #e2e8f0;
        --btn-sec-text: #0f172a;
        --btn-sec-border: #94a3b8;
        --footer-bg: #f1f5f9;
        --footer-text: #4A6B82;
        --footer-border: #cbd5e1;
    """
else:
    theme_vars = """
        --bg-main: #0b0f19;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --card-bg: rgba(255, 255, 255, 0.04);
        --card-border: rgba(255, 255, 255, 0.12);
        --btn-sec-bg: #1e293b;
        --btn-sec-text: #f1f5f9;
        --btn-sec-border: #334155;
        --footer-bg: rgba(255, 255, 255, 0.03);
        --footer-text: #4A6B82;
        --footer-border: rgba(255, 255, 255, 0.08);
    """

custom_css = f"""
<script>
    document.documentElement.setAttribute('translate', 'no');
    document.documentElement.classList.add('notranslate');
    document.body.setAttribute('translate', 'no');
    document.body.classList.add('notranslate');
    const obs = new MutationObserver((mutations) => {{
        for (const m of mutations) {{
            for (const n of m.addedNodes) {{
                if (n.nodeType === 1 && (n.className && String(n.className).includes('immersive-translate'))) {{
                    n.remove();
                }}
            }}
        }}
    }});
    obs.observe(document.documentElement, {{ childList: true, subtree: true }});
</script>
<style>
    :root {{
        {theme_vars}
    }}

    .stApp {{
        background-color: var(--bg-main) !important;
        color: var(--text-main) !important;
    }}

    [class*="immersive-translate"], .immersive-translate-target-wrapper {{ display: none !important; height: 0 !important; }}
    #MainMenu, footer {{ visibility: hidden; }}
    
    .block-container {{
        max-width: 860px !important;
        padding-top: 4.8rem !important;
        padding-bottom: 4.5rem !important;
        margin: 0 auto !important;
    }}
    
    .system-title {{
        font-size: 26px !important;
        line-height: 1.4 !important;
        font-weight: 900 !important;
        letter-spacing: 1.2px;
        color: #4A6B82 !important;
        text-align: center !important;
        display: block !important;
        width: 100%;
        margin-top: 4px !important;
        margin-bottom: 18px !important;
    }}

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] p {{
        color: var(--text-main) !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
    }}

    .app-card {{
        background: var(--card-bg) !important;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        border: 1px solid var(--card-border) !important;
    }}
    .detail-row {{
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid var(--card-border) !important;
        font-size: 14px;
        line-height: 1.45;
        color: var(--text-main) !important;
    }}
    .detail-label {{ color: var(--text-muted) !important; font-weight: 500; width: 40%; }}
    .detail-value {{ font-weight: 600; width: 60%; text-align: right; word-break: break-all; color: var(--text-main) !important; }}

    .badge {{
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 700;
        color: #ffffff !important;
    }}
    .badge-A {{ background-color: #c05646; }}
    .badge-B {{ background-color: #d9822b; }}
    .badge-C {{ background-color: #4A6B82; }}
    .badge-D {{ background-color: #52796f; }}
    .badge-其他 {{ background-color: #64748b; }}

    .embed-map-box {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--card-border) !important;
        margin: 12px 0;
    }}

    button[kind="secondary"] {{
        background-color: var(--btn-sec-bg) !important;
        color: var(--btn-sec-text) !important;
        border: 1px solid var(--btn-sec-border) !important;
        font-weight: 700 !important;
    }}
    button[kind="primary"] {{
        background-color: #4A6B82 !important;
        border-color: #3E5C76 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    button[key="badge_btn_A"] {{ background-color: #c05646 !important; border: 1px solid #991b1b !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_B"] {{ background-color: #d9822b !important; border: 1px solid #c2410c !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_C"] {{ background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_D"] {{ background-color: #059669 !important; border: 1px solid #047857 !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_其他"] {{ background-color: #475569 !important; border: 1px solid #334155 !important; color: #ffffff !important; font-weight: 800 !important; }}

    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        width: 100% !important;
        margin-top: 20px !important;
        margin-bottom: 12px !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) > div {{
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) button {{
        padding-left: 2px !important;
        padding-right: 2px !important;
        font-size: 13px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        height: 38px !important;
    }}

    .app-official-footer-bottom {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
        padding: 12px 14px !important;
        background: var(--footer-bg) !important;
        border-radius: 10px !important;
        border: 1px solid var(--footer-border) !important;
    }}
    .footer-title-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }}
    .app-official-logo {{ height: 22px !important; width: auto !important; display: inline-block !important; vertical-align: middle !important; }}
    .app-official-text {{
        font-size: 13.5px !important;
        font-weight: 800 !important;
        color: var(--footer-text) !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        line-height: 22px !important;
    }}
    .app-official-source {{
        font-size: 11px !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        margin-top: 4px !important;
        letter-spacing: 0.4px !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 頂部色彩模式切換
col_top_space, col_top_theme = st.columns([0.65, 0.35])
with col_top_theme:
    selected_theme = st.radio(
        "色彩模式",
        ["🌙 深色黑底", "☀️ 淺色白底"],
        index=0 if st.session_state.theme_mode == "🌙 深色黑底" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = selected_theme
        st.rerun()

DATA_FILE = "邊坡資料.xlsx" if os.path.exists("邊坡資料.xlsx") else "1.邊坡資料(11505).xlsx"
KMZ_FILE = "南澳段歷次災害-(更新斑點圖使用).kmz"

# 定量分級標準化轉換函式（自動識別 1~5、1.0、第一級、第1級等）
def normalize_quant(val):
    if pd.isna(val):
        return "未施作"
    s = str(val).strip()
    if s in ["", "nan", "None", "未施作", "未施作定量評估", "無"]:
        return "未施作"
    # 判斷是否為 1~5 或 一~五
    if any(x in s for x in ["1", "一", "第1級", "第一級"]):
        return "第1級"
    if any(x in s for x in ["2", "二", "第2級", "第二級"]):
        return "第2級"
    if any(x in s for x in ["3", "三", "第3級", "第三級"]):
        return "第3級"
    if any(x in s for x in ["4", "四", "第4級", "第四級"]):
        return "第4級"
    if any(x in s for x in ["5", "五", "第5級", "第五級"]):
        return "第5級"
    return "未施作"

# 3. 讀取 Excel 資料
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_excel(DATA_FILE)
    df['起點緯度'] = pd.to_numeric(df['起點緯度'], errors='coerce')
    df['起點經度'] = pd.to_numeric(df['起點經度'], errors='coerce')
    df['定性分級'] = df['定性分級'].fillna('其他').astype(str).str.strip()
    
    # 標準化定量分級
    if '定量分級' in df.columns:
        df['定量分級'] = df['定量分級'].apply(normalize_quant)
    else:
        df['定量分級'] = "未施作"
    return df

# 4. 讀取 KMZ 歷次災害斑點
@st.cache_data
def load_kmz():
    disasters = []
    if not os.path.exists(KMZ_FILE):
        return pd.DataFrame(disasters)
    try:
        with zipfile.ZipFile(KMZ_FILE, 'r') as z:
            kmls = [f for f in z.namelist() if f.endswith('.kml')]
            if not kmls:
                return pd.DataFrame(disasters)
            kml_data = z.read(kmls[0])
        root = ET.fromstring(kml_data)
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        for pm in root.findall('.//kml:Placemark', ns):
            name_node = pm.find('kml:name', ns)
            name = name_node.text.strip() if name_node is not None and name_node.text else "歷次災點"
            desc_node = pm.find('kml:description', ns)
            desc = desc_node.text.strip() if desc_node is not None and desc_node.text else ""
            coord_node = pm.find('.//kml:coordinates', ns)
            
            full_text = f"{name} {desc}"
            year_match = re.search(r'(\d{2,3})年', full_text)
            dis_year = f"{year_match.group(1)}年" if year_match else "其他/歷史"

            if coord_node is not None and coord_node.text:
                parts = coord_node.text.strip().split()[0].split(',')
                if len(parts) >= 2:
                    disasters.append({
                        "災害名稱": name,
                        "年度": dis_year,
                        "詳細說明": desc,
                        "緯度": float(parts[1]),
                        "經度": float(parts[0])
                    })
    except Exception:
        pass
    return pd.DataFrame(disasters)

df = load_data()
df_disasters = load_kmz()

if df.empty:
    st.error(f"找不到邊坡資料檔案：{DATA_FILE}")
    st.stop()

# 子頁面頂部返回鍵
is_sub_view = (st.session_state.bottom_tab != "📋 邊坡清冊") or (st.session_state.selected_slope_id is not None)
if is_sub_view:
    if st.button("⬅️ 返回邊坡清冊主畫面", key="top_back_btn", use_container_width=True, type="primary"):
        st.session_state.bottom_tab = "📋 邊坡清冊"
        st.session_state.selected_slope_id = None
        st.rerun()

# ==============================================================================
# 頁面 1：邊坡清冊與詳細資料
# ==============================================================================
if st.session_state.bottom_tab == "📋 邊坡清冊":
    
    # --- 單筆邊坡詳細資訊 (Details View) ---
    if st.session_state.selected_slope_id is not None:
        matched = df[df['口卡編號'] == st.session_state.selected_slope_id]
        if not matched.empty:
            row = matched.iloc[0]
            q_grade = str(row['定性分級'])

            card_top = (
                "<div class='app-card notranslate' translate='no'>"
                "<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<span style='font-size:19px; font-weight:700;'>📍 {row['路線']} {row['里程樁號(起)']}</span>"
                f"<span class='badge badge-{q_grade}'>{q_grade} 級</span>"
                "</div>"
                f"<div style='font-family:monospace; font-size:12.5px; color:var(--text-muted); margin-top:3px;'>{row['口卡編號']}</div>"
                f"<div style='font-size:12px; color:var(--text-muted); margin-top:2px;'>最近更新：{row.get('最近更新時間', '無')}</div>"
                f"<div style='font-size:14px; font-weight:600; color:#4A6B82; margin-top:4px;'>構造物：{row.get('邊坡構造物', '自然邊坡')}</div>"
                "</div>"
            )
            st.markdown(card_top, unsafe_allow_html=True)

            r_lat, r_lon = row.get('起點緯度'), row.get('起點經度')
            if pd.notna(r_lat) and pd.notna(r_lon):
                st.markdown("##### 🛰️ 現地空間衛星影像位置")
                embed_map_html = (
                    "<div class='embed-map-box notranslate' translate='no'>"
                    f"<iframe width='100%' height='280' frameborder='0' scrolling='no' marginheight='0' marginwidth='0' "
                    f"src='https://maps.google.com/maps?q={r_lat},{r_lon}&t=k&z=17&ie=UTF8&iwloc=&output=embed'></iframe>"
                    "</div>"
                )
                st.markdown(embed_map_html, unsafe_allow_html=True)

                gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={r_lat},{r_lon}"
                nav_link = (
                    "<div style='margin: 8px 0 16px 0;' class='notranslate' translate='no'>"
                    f"<a href='{gmap_url}' target='_blank' style='display:block; text-align:center; padding:9px 12px; background:#4A6B82; color:white; font-weight:bold; border-radius:8px; text-decoration:none; font-size:14px;'>"
                    "🧭 開啟 Google Maps 導航至此處（依目前位置規劃路線）</a></div>"
                )
                st.markdown(nav_link, unsafe_allow_html=True)

            st.markdown("##### 📋 邊坡完整屬性資料")
            detail_fields = [
                ("邊坡狀態", str(row.get('邊坡狀態', '無'))),
                ("區處", str(row.get('區處', '東區養護工程分局'))),
                ("工務段", str(row.get('工務段', '南澳工務段'))),
                ("縣市", str(row.get('縣市', '宜蘭縣'))),
                ("鄉鎮市區", str(row.get('鄉鎮市區', ''))),
                ("路線", str(row.get('路線', ''))),
                ("里程樁號(起)", str(row.get('里程樁號(起)', ''))),
                ("里程樁號(迄)", str(row.get('里程樁號(迄)', ''))),
                ("方向", str(row.get('方向', ''))),
                ("邊坡方向", str(row.get('邊坡方向', ''))),
                ("起點經度", f"{row.get('起點經度', ''):.5f}" if pd.notna(row.get('起點經度')) else "無"),
                ("起點緯度", f"{row.get('起點緯度', ''):.5f}" if pd.notna(row.get('起點緯度')) else "無"),
                ("監控等級", str(row.get('監控等級', '非重點監控路段'))),
                ("坡高", f"{row.get('坡高', '')} m" if pd.notna(row.get('坡高')) else "無"),
                ("邊坡面寬", f"{row.get('邊坡面寬', '')} m" if pd.notna(row.get('邊坡面寬')) else "無"),
                ("坡度", f"{row.get('坡度', '')}°" if pd.notna(row.get('坡度')) else "無"),
                ("專案列管案件", str(row.get('專案列管案件', '無'))),
                ("定性分級", f"{q_grade} 級"),
                ("定量分級", str(row.get('定量分級', '未施作'))),
                ("災害歷史", str(row.get('災害歷史', '無'))),
                ("資料建立日期", str(row.get('資料建立日期', '無'))),
                ("監測情形", str(row.get('監測情形', '無'))),
                ("監測辦理方式", str(row.get('監測辦理方式', '無'))),
                ("附近地名", str(row.get('附近地名', '無'))),
            ]

            rows_html = "".join([f"<div class='detail-row'><span class='detail-label'>{k}</span><span class='detail-value'>{v}</span></div>" for k, v in detail_fields])
            st.markdown(f"<div class='app-card notranslate' translate='no'>{rows_html}</div>", unsafe_allow_html=True)

            st.markdown("**現地狀況描述：**")
            desc_val = str(row.get('現地狀況描述', '無描述紀錄'))
            desc_html = (
                "<div class='app-card notranslate' translate='no' style='background:rgba(74, 107, 130, 0.12); border-left:4px solid #4A6B82; line-height:1.5; font-size:14px;'>"
                f"{desc_val}</div>"
            )
            st.markdown(desc_html, unsafe_allow_html=True)

            # 構造物分項巡查 Form
            st.markdown("##### 📝 構造物分項巡查回報")
            raw_structs = str(row.get('邊坡構造物', '自然邊坡'))
            split_structs = [s.strip() for s in re.split(r'[,、]', raw_structs) if s.strip()]
            if not split_structs:
                split_structs = ["自然邊坡"]
            split_structs.append("＋ 整體邊坡現況")

            with st.form("inspect_form"):
                selected_struct = st.selectbox("構造物項目", split_structs)
                c_st, c_qu = st.columns(2)
                with c_st:
                    new_status = st.selectbox("邊坡管理狀態", ["鎖定管理中", "解除列管", "重點列管"])
                with c_qu:
                    new_qual = st.selectbox("定性分級調整", ["A", "B", "C", "D", "其他"], index=["A","B","C","D","其他"].index(q_grade) if q_grade in ["A","B","C","D","其他"] else 4)

                struct_desc = st.text_area(f"【{selected_struct}】現地狀況描述", placeholder="請輸入現況描述...")
                up_photos = st.file_uploader("選取照片 (支援一次多張)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
                cam_photo = st.camera_input("開啟相機拍照")

                if st.form_submit_button("💾 儲存並寫入 Excel", type="primary", use_container_width=True):
                    os.makedirs("inspection_photos", exist_ok=True)
                    t_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    s_count = 0
                    if up_photos:
                        for idx, p in enumerate(up_photos):
                            c_s = selected_struct.replace(":", "_").replace("/", "_")
                            Image.open(p).save(f"inspection_photos/{row['口卡編號']}_{c_s}_{t_now}_{idx+1}.jpg")
                            s_count += 1
                    if cam_photo:
                        c_s = selected_struct.replace(":", "_").replace("/", "_")
                        Image.open(cam_photo).save(f"inspection_photos/{row['口卡編號']}_{c_s}_{t_now}_cam.jpg")
                        s_count += 1

                    old_desc = str(row.get('現地狀況描述', '')) if pd.notna(row.get('現地狀況描述')) else ""
                    new_entry = f"[{datetime.date.today().strftime('%m/%d')} {selected_struct}] {struct_desc}" if struct_desc else ""
                    combined_desc = (new_entry + "\n" + old_desc).strip() if new_entry else old_desc

                    df.loc[df['口卡編號'] == row['口卡編號'], '定性分級'] = new_qual
                    df.loc[df['口卡編號'] == row['口卡編號'], '邊坡狀態'] = new_status
                    if combined_desc:
                        df.loc[df['口卡編號'] == row['口卡編號'], '現地狀況描述'] = combined_desc
                    df.loc[df['口卡編號'] == row['口卡編號'], '最近更新時間'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

                    df.to_excel(DATA_FILE, index=False)
                    st.cache_data.clear()
                    st.success(f"✅ 成功更新【{selected_struct}】（儲存 {s_count} 張照片）")
                    st.rerun()

    # --- 主清單列表模式 ---
    else:
        st.markdown("<div class='system-title notranslate' translate='no'>南澳段省道邊坡全生命週期資料庫</div>", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            route_list = ["全部路線"] + list(df['路線'].dropna().unique())
            route_filter = st.selectbox("路線篩選", route_list)
        with col_f2:
            qual_list = ["全部分級", "A", "B", "C", "D", "其他"]
            qual_filter = st.selectbox("分級篩選", qual_list)

        search_kw = st.text_input("🔍 搜尋里程、卡號或地名", placeholder="例如: 8k+600、隘丁")

        f_df = df.copy()
        if route_filter != "全部路線":
            f_df = f_df[f_df['路線'] == route_filter]
        if qual_filter != "全部分級":
            f_df = f_df[f_df['定性分級'] == qual_filter]
        if search_kw:
            f_df = f_df[
                f_df['口卡編號'].astype(str).str.contains(search_kw, case=False) |
                f_df['里程樁號(起)'].astype(str).str.contains(search_kw, case=False) |
                f_df['附近地名'].astype(str).str.contains(search_kw, case=False)
            ]

        # 統計數量
        q_counts = f_df['定性分級'].value_counts()
        cnt_a = q_counts.get("A", 0)
        cnt_b = q_counts.get("B", 0)
        cnt_c = q_counts.get("C", 0)
        cnt_d = q_counts.get("D", 0)
        cnt_o = q_counts.get("其他", 0)

        st.caption(f"符合條件邊坡：**{len(f_df)}** 處（總資產：{len(df)} 處） 點擊下方各級按鈕查看對應樁號：")

        # 5 顆高對比彩色分級按鈕
        b_cols = st.columns(5)
        with b_cols[0]:
            if st.button(f"A級 ({cnt_a})", key="badge_btn_A", use_container_width=True):
                st.session_state.active_grade_detail = "A" if st.session_state.active_grade_detail != "A" else None
                st.rerun()
        with b_cols[1]:
            if st.button(f"B級 ({cnt_b})", key="badge_btn_B", use_container_width=True):
                st.session_state.active_grade_detail = "B" if st.session_state.active_grade_detail != "B" else None
                st.rerun()
        with b_cols[2]:
            if st.button(f"C級 ({cnt_c})", key="badge_btn_C", use_container_width=True):
                st.session_state.active_grade_detail = "C" if st.session_state.active_grade_detail != "C" else None
                st.rerun()
        with b_cols[3]:
            if st.button(f"D級 ({cnt_d})", key="badge_btn_D", use_container_width=True):
                st.session_state.active_grade_detail = "D" if st.session_state.active_grade_detail != "D" else None
                st.rerun()
        with b_cols[4]:
            if st.button(f"其他 ({cnt_o})", key="badge_btn_其他", use_container_width=True):
                st.session_state.active_grade_detail = "其他" if st.session_state.active_grade_detail != "其他" else None
                st.rerun()

        # 點擊級數按鈕後展開詳細樁號
        if st.session_state.active_grade_detail:
            selected_grade = st.session_state.active_grade_detail
            grade_sub_df = f_df[f_df['定性分級'] == selected_grade]
            with st.container(border=True):
                st.markdown(f"**📌【{selected_grade} 級】邊坡樁號清冊（共 {len(grade_sub_df)} 處，點擊直達詳情）：**")
                g_cols = st.columns(2)
                for idx, (_, g_row) in enumerate(grade_sub_df.iterrows()):
                    with g_cols[idx % 2]:
                        g_label = f"📍 {g_row['路線']} {g_row['里程樁號(起)']}"
                        if st.button(g_label, key=f"quick_pick_{g_row['口卡編號']}", use_container_width=True):
                            st.session_state.selected_slope_id = g_row['口卡編號']
                            st.rerun()

        st.markdown("<hr style='margin: 12px 0 16px 0; border: none; border-top: 1px solid var(--card-border);' />", unsafe_allow_html=True)

        for r_name in f_df['路線'].dropna().unique():
            sub_df = f_df[f_df['路線'] == r_name]
            total_sub = len(sub_df)
            
            with st.expander(f"🛣️ **{r_name}**（共 {total_sub} 處）", expanded=False):
                show_all = False
                if total_sub > 10:
                    show_all = st.checkbox(f"展開全部 {total_sub} 筆（預設顯示前 10 筆）", key=f"chk_{r_name}")
                
                display_df = sub_df if show_all else sub_df.head(10)

                for _, r in display_df.iterrows():
                    grade = str(r['定性分級'])
                    with st.container(border=True):
                        btn_label = f"📍 {r['里程樁號(起)']}  [{grade}級]"
                        if st.button(btn_label, key=f"pick_{r['口卡編號']}", use_container_width=True):
                            st.session_state.selected_slope_id = r['口卡編號']
                            st.rerun()

                        st.caption(f"卡號：`{r['口卡編號']}` ｜ 構造：`{r.get('邊坡構造物', '自然邊坡')[:18]}`")

# ==============================================================================
# 頁面 2：定量定性分級統計分析 (標準化支援 第1級 ~ 第5級)
# ==============================================================================
elif st.session_state.bottom_tab == "📊 定量定性":
    st.markdown("<div class='system-title notranslate' translate='no'>邊坡定量定性分級統計</div>", unsafe_allow_html=True)
    
    chart_type = st.radio("📈 圖表呈現模式", ["圓餅圖 (Pie Chart)", "長條圖 (Bar Chart)"], horizontal=True)

    # 1. 定性分級
    st.markdown("<div class='notranslate' translate='no' style='font-size:16.5px; font-weight:700; color:var(--text-main); margin-top:8px; margin-bottom:6px;'>1. 定性分級統計 (A, B, C, D, 其他)</div>", unsafe_allow_html=True)
    qual_order = ["A", "B", "C", "D", "其他"]
    c_counts = df['定性分級'].value_counts()
    qual_df = pd.DataFrame({"分級": qual_order, "數量": [c_counts.get(c, 0) for c in qual_order]})
    qual_color_map = {"A": "#c05646", "B": "#d9822b", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}

    if "圓餅圖" in chart_type:
        fig_qual = px.pie(
            qual_df, values='數量', names='分級', hole=0.45,
            color='分級',
            color_discrete_map=qual_color_map,
            category_orders={"分級": qual_order}
        )
        fig_qual.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            insidetextfont=dict(color="#ffffff", size=13),
            sort=False
        )
        fig_qual.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=310,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plotly_font_color),
            legend=dict(font=dict(color=plotly_font_color, size=13))
        )
        st.plotly_chart(fig_qual, use_container_width=True)
    else:
        fig_qual = px.bar(
            qual_df, x="分級", y="數量", text="數量",
            color="分級",
            color_discrete_map=qual_color_map,
            category_orders={"分級": qual_order}
        )
        fig_qual.update_traces(textposition='outside')
        fig_qual.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=290,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plotly_font_color),
            xaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)),
            yaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)),
            legend=dict(font=dict(color=plotly_font_color))
        )
        st.plotly_chart(fig_qual, use_container_width=True)

    st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--card-border);' />", unsafe_allow_html=True)

    # 2. 定量分級（嚴格依序排：第1級 -> 第2級 -> 第3級 -> 第4級 -> 第5級 -> 未施作）
    st.markdown("<div class='notranslate' translate='no' style='font-size:16.5px; font-weight:700; color:var(--text-main); margin-top:8px; margin-bottom:6px;'>2. 定量分級統計 (第1級 ~ 第5級 / 未施作)</div>", unsafe_allow_html=True)
    
    quant_order = ["第1級", "第2級", "第3級", "第4級", "第5級", "未施作"]
    quant_color_map = {
        "第1級": "#1e40af",  # 深藍
        "第2級": "#3b82f6",  # 亮藍
        "第3級": "#f97316",  # 橘紅
        "第4級": "#ef4444",  # 紅色
        "第5級": "#b91c1c",  # 深紅
        "未施作": "#10b981"  # 綠色
    }
    
    q_counts = df['定量分級'].value_counts()
    quant_df = pd.DataFrame({
        "定量分級": quant_order,
        "數量": [q_counts.get(c, 0) for c in quant_order]
    })

    if "圓餅圖" in chart_type:
        fig_quant = px.pie(
            quant_df, values='數量', names='定量分級', hole=0.45,
            color='定量分級',
            color_discrete_map=quant_color_map,
            category_orders={"定量分級": quant_order}
        )
        fig_quant.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            insidetextfont=dict(color="#ffffff", size=13),
            sort=False
        )
        fig_quant.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=310,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plotly_font_color),
            legend=dict(font=dict(color=plotly_font_color, size=13))
        )
        st.plotly_chart(fig_quant, use_container_width=True)
    else:
        fig_quant = px.bar(
            quant_df, x="定量分級", y="數量", text="數量",
            color="定量分級",
            color_discrete_map=quant_color_map,
            category_orders={"定量分級": quant_order}
        )
        fig_quant.update_traces(textposition='outside')
        fig_quant.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=290,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plotly_font_color),
            xaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)),
            yaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)),
            legend=dict(font=dict(color=plotly_font_color))
        )
        st.plotly_chart(fig_quant, use_container_width=True)

# ==============================================================================
# 頁面 3：地圖定位 (整合 GPS 即時定位準心)
# ==============================================================================
elif st.session_state.bottom_tab == "🗺️ 地圖定位":
    st.markdown("<div class='system-title notranslate' translate='no'>邊坡空間地圖定位</div>", unsafe_allow_html=True)
    st.caption("💡 點擊地圖左上方 **「準心定位圖示 🎯」** 即可自動定位目前所在位置並計算視野範圍。")
    
    valid_pts = df.dropna(subset=['起點緯度', '起點經度'])
    
    if not valid_pts.empty:
        c_lat = valid_pts['起點緯度'].median()
        c_lon = valid_pts['起點經度'].median()
        m_loc = folium.Map(location=[c_lat, c_lon], zoom_start=11, tiles=None)

        LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=False).add_to(m_loc)

        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google Earth 衛星空照圖",
            name="🛰️ Google Earth 衛星圖",
            overlay=False,
            control=True
        ).add_to(m_loc)

        folium.TileLayer(
            tiles="OpenStreetMap",
            name="🗺️ 標準電子地圖",
            overlay=False,
            control=True
        ).add_to(m_loc)

        cmap = {"A": "#c05646", "B": "#d9822b", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}
        for _, r in valid_pts.iterrows():
            g = str(r['定性分級'])
            color = cmap.get(g, '#64748b')
            p_lat, p_lon = r['起點緯度'], r['起點經度']
            gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}"
            
            popup_html = (
                "<div translate='no' class='notranslate' style='font-family:sans-serif; font-size:13.5px; line-height:1.45;'>"
                f"<b style='font-size:14.5px; color:#0f172a;'>{r['路線']} {r['里程樁號(起)']}</b><br/>"
                f"<b>卡號：</b>{r['口卡編號']}<br/>"
                f"<b>定性分級：</b><span style='color:{color}; font-weight:bold;'>{g} 級</span><br/>"
                f"<b>構造物：</b>{r.get('邊坡構造物', '自然邊坡')}<br/>"
                f"<a href='{gmap_url}' target='_blank' style='display:inline-block; margin-top:6px; padding:4px 9px; background:#4A6B82; color:white; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;'>🧭 導航到此里程</a>"
                "</div>"
            )
            folium.CircleMarker(
                location=[p_lat, p_lon],
                radius=6,
                popup=folium.Popup(popup_html, max_width=260),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85
            ).add_to(m_loc)

        folium.LayerControl(position="topright", collapsed=True).add_to(m_loc)
        st_folium(m_loc, width="100%", height=530)

# ==============================================================================
# 頁面 4：災害斑點圖 (整合 GPS 即時定位準心)
# ==============================================================================
elif st.session_state.bottom_tab == "🔥 災害斑點圖":
    st.markdown(f"<div class='system-title notranslate' translate='no'>歷次災害斑點專題圖（{len(df_disasters)} 處）</div>", unsafe_allow_html=True)
    st.caption("💡 點擊地圖左上方 **「準心定位圖示 🎯」** 即可自動定位目前所在位置與最近災點距離。")

    if not df_disasters.empty:
        c_lat = df_disasters['緯度'].median()
        c_lon = df_disasters['經度'].median()
        m_dis = folium.Map(location=[c_lat, c_lon], zoom_start=11, tiles=None)

        LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=False).add_to(m_dis)

        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google Earth 衛星空照圖",
            name="🛰️ Google Earth 衛星圖",
            overlay=False,
            control=True
        ).add_to(m_dis)

        folium.TileLayer(
            tiles="OpenStreetMap",
            name="🗺️ 標準電子地圖",
            overlay=False,
            control=True
        ).add_to(m_dis)

        year_palette = {
            "113年": "#e63946",
            "114年": "#f77f00",
            "112年": "#457b9d",
            "115年": "#2a9d8f",
            "其他/歷史": "#6c757d"
        }

        unique_years = sorted(df_disasters['年度'].unique())
        for yr in unique_years:
            yr_df = df_disasters[df_disasters['年度'] == yr]
            yr_color = year_palette.get(yr, "#8338ec")
            
            yr_layer = folium.FeatureGroup(name=f"📍 {yr} ({len(yr_df)}處)", show=True)
            for _, d in yr_df.iterrows():
                d_lat, d_lon = d['緯度'], d['經度']
                d_gurl = f"https://www.google.com/maps/dir/?api=1&destination={d_lat},{d_lon}"
                d_popup = (
                    "<div translate='no' class='notranslate' style='font-family:sans-serif; font-size:13.5px; line-height:1.45;'>"
                    f"<span style='background:{yr_color}; color:white; padding:2px 6px; border-radius:3px; font-size:11px; font-weight:bold;'>{yr} 災害斑點</span><br/>"
                    f"<b style='color:#0f172a; font-size:13.5px; margin-top:4px; display:inline-block;'>{d['災害名稱']}</b><br/>"
                    f"{d['詳細說明']}<br/>"
                    f"<a href='{d_gurl}' target='_blank' style='display:inline-block; margin-top:5px; padding:3px 8px; background:#4A6B82; color:white; border-radius:4px; text-decoration:none; font-size:12px; font-weight:bold;'>🧭 導航至此災點</a>"
                    "</div>"
                )
                folium.CircleMarker(
                    location=[d_lat, d_lon],
                    radius=5.5,
                    popup=folium.Popup(d_popup, max_width=260),
                    color="#2b2d42",
                    weight=1,
                    fill=True,
                    fill_color=yr_color,
                    fill_opacity=0.9
                ).add_to(yr_layer)
            yr_layer.add_to(m_dis)

        folium.LayerControl(position="topright", collapsed=True).add_to(m_dis)
        st_folium(m_dis, width="100%", height=530)

# ==============================================================================
# 5. 4 個功能鍵：橫式排列，位於內容與 LOGO 之間
# ==============================================================================
nav_cols = st.columns(4)
with nav_cols[0]:
    if st.button("📋 邊坡清冊", key="nav_btn_1", use_container_width=True, type="primary" if st.session_state.bottom_tab == "📋 邊坡清冊" else "secondary"):
        st.session_state.bottom_tab = "📋 邊坡清冊"
        st.rerun()

with nav_cols[1]:
    if st.button("📊 定量定性", key="nav_btn_2", use_container_width=True, type="primary" if st.session_state.bottom_tab == "📊 定量定性" else "secondary"):
        st.session_state.bottom_tab = "📊 定量定性"
        st.session_state.selected_slope_id = None
        st.rerun()

with nav_cols[2]:
    if st.button("🗺️ 地圖定位", key="nav_btn_3", use_container_width=True, type="primary" if st.session_state.bottom_tab == "🗺️ 地圖定位" else "secondary"):
        st.session_state.bottom_tab = "🗺️ 地圖定位"
        st.session_state.selected_slope_id = None
        st.rerun()

with nav_cols[3]:
    if st.button("🔥 災害斑點", key="nav_btn_4", use_container_width=True, type="primary" if st.session_state.bottom_tab == "🔥 災害斑點圖" else "secondary"):
        st.session_state.bottom_tab = "🔥 災害斑點圖"
        st.session_state.selected_slope_id = None
        st.rerun()

# ==============================================================================
# 6. 單位識別頁尾：保持在全頁面最底端
# ==============================================================================
LOGO_VECTOR_SVG = (
    "<svg class='app-official-logo notranslate' viewBox='0 0 818 138' fill='none' xmlns='http://www.w3.org/2000/svg' translate='no'>"
    "<path d='M409 69C409 30.89 439.89 0 478 0C516.11 0 547 30.89 547 69C547 107.11 516.11 138 478 138C439.89 138 409 107.11 409 69Z' fill='#E62117'/>"
    "<path d='M478 14C447.62 14 423 38.62 423 69C423 99.38 447.62 124 478 124C508.38 124 533 99.38 533 69C533 38.62 508.38 14 478 14ZM478 110C455.36 110 437 91.64 437 69C437 46.36 455.36 28 478 28C500.64 28 519 46.36 519 69C519 91.64 500.64 110 478 110Z' fill='white'/>"
    "<path d='M0 24L380 24C395 24 402 36 388 48L70 48C50 48 30 40 0 24Z' fill='#1E50A2'/>"
    "<path d='M818 24L438 24C423 24 416 36 430 48L748 48C768 48 788 40 818 24Z' fill='#1E50A2'/>"
    "<path d='M60 56L370 56C382 56 388 66 376 76L120 76C100 76 80 70 60 56Z' fill='#0080FF'/>"
    "<path d='M758 56L448 56C436 56 430 66 442 76L698 76C718 76 738 70 758 56Z' fill='#0080FF'/>"
    "<path d='M120 86L360 86C370 86 375 94 365 102L170 102C150 102 135 96 120 86Z' fill='#00BFFF'/>"
    "<path d='M698 86L458 86C448 86 443 94 453 102L648 102C668 102 683 96 698 86Z' fill='#00BFFF'/>"
    "</svg>"
)

logo_render = LOGO_VECTOR_SVG
for possible_logo in ["LOGO.webp", "LOGO.png", "logo.png", "logo.webp"]:
    if os.path.exists(possible_logo):
        try:
            with open(possible_logo, "rb") as f:
                b64_val = base64.b64encode(f.read()).decode()
                ext = "webp" if possible_logo.endswith("webp") else "png"
                logo_render = f"<img class='app-official-logo notranslate' src='data:image/{ext};base64,{b64_val}' alt='公路局LOGO' translate='no' />"
                break
        except Exception:
            pass

footer_bottom_html = (
    "<div class='app-official-footer-bottom notranslate' translate='no'>"
    "  <div class='footer-title-row'>"
    f"    {logo_render}"
    "    <span class='app-official-text notranslate' translate='no'>交通部公路局東區養護工程分局南澳工務段</span>"
    "  </div>"
    "  <div class='app-official-source notranslate' translate='no'>本網頁資料來源：邊坡全生命週期管理系統</div>"
    "</div>"
)

st.markdown(footer_bottom_html, unsafe_allow_html=True)