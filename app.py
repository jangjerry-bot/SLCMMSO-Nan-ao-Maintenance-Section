# app.py
import os
import streamlit as st
import pandas as pd
import folium
from folium.plugins import LocateControl
from streamlit_folium import st_folium
import plotly.express as px
import datetime
import zipfile
import xml.etree.ElementTree as ET
import re

# 自動防呆建立 .streamlit/config.toml 設定檔
os.makedirs(".streamlit", exist_ok=True)
config_path = os.path.join(".streamlit", "config.toml")
config_content = """[theme]
base = "light"
primaryColor = "#4A6B82"
backgroundColor = "#f8fafc"
secondaryBackgroundColor = "#ffffff"
textColor = "#0f172a"
"""
if not os.path.exists(config_path) or open(config_path, "r", encoding="utf-8").read() != config_content:
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

from style import get_theme_css, render_footer, render_top_logo
from inspection_schema import INSPECTION_TEMPLATES, match_template, generate_doc_report

# 1. 頁面設定
st.set_page_config(
    page_title="南澳邊坡全生命週期資料庫",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 狀態管理
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "☀️ 淺色白底"
if "bottom_tab" not in st.session_state:
    st.session_state.bottom_tab = "📋 邊坡清冊"
if "selected_slope_id" not in st.session_state:
    st.session_state.selected_slope_id = None
if "active_grade_detail" not in st.session_state:
    st.session_state.active_grade_detail = None
if "patrol_draft" not in st.session_state:
    st.session_state.patrol_draft = {}

is_light = (st.session_state.theme_mode == "☀️ 淺色白底")
plotly_font_color = "#0f172a" if is_light else "#f8fafc"

st.markdown(get_theme_css(is_light), unsafe_allow_html=True)

# 頂部色彩切換
_, col_top_theme = st.columns([0.65, 0.35])
with col_top_theme:
    selected_theme = st.radio(
        "色彩模式",
        ["🌙 深色黑底", "☀️ 淺色白底"],
        index=1 if is_light else 0,
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = selected_theme
        st.rerun()

# 頂部 LOGO 與標題 (3D 向量 LOGO 水平並排於「南澳」文字前)
st.markdown(render_top_logo(), unsafe_allow_html=True)

# ==============================================================================
# ★★★ 5 大功能導航鍵：直接置頂於標題正下方、篩選條件上方 ★★★
# ==============================================================================
tabs = ["📋 邊坡清冊", "📊 定量定性", "🗺️ 地圖定位", "🔥 災害斑點", "📝 養護巡查"]
nav_cols = st.columns(5)
for i, tab_name in enumerate(tabs):
    with nav_cols[i]:
        is_cur = (st.session_state.bottom_tab == tab_name or (tab_name == "🔥 災害斑點" and st.session_state.bottom_tab == "🔥 災害斑點圖"))
        if st.button(tab_name, key=f"nav_btn_{i+1}", use_container_width=True, type="primary" if is_cur else "secondary"):
            st.session_state.bottom_tab = "🔥 災害斑點圖" if tab_name == "🔥 災害斑點" else tab_name
            if tab_name != "📋 邊坡清冊":
                st.session_state.selected_slope_id = None
            st.rerun()

DATA_FILE = "邊坡資料.xlsx" if os.path.exists("邊坡資料.xlsx") else "1.邊坡資料(11505).xlsx"
KMZ_FILE = "南澳段歷次災害-(更新斑點圖使用).kmz"

def normalize_quant(val):
    if pd.isna(val): return "未施作"
    s = str(val).strip()
    if s in ["", "nan", "None", "未施作", "未施作定量評估", "無"]: return "未施作"
    for num, zh in [("1", "一"), ("2", "二"), ("3", "三"), ("4", "四"), ("5", "五")]:
        if num in s or zh in s: return f"第{num}級"
    return "未施作"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE): return pd.DataFrame()
    df = pd.read_excel(DATA_FILE)
    df['起點緯度'] = pd.to_numeric(df['起點緯度'], errors='coerce')
    df['起點經度'] = pd.to_numeric(df['起點經度'], errors='coerce')
    df['定性分級'] = df['定性分級'].fillna('其他').astype(str).str.strip()
    df['定量分級'] = df['定量分級'].apply(normalize_quant) if '定量分級' in df.columns else "未施作"
    return df

@st.cache_data
def load_kmz():
    disasters = []
    if not os.path.exists(KMZ_FILE): return pd.DataFrame(disasters)
    try:
        with zipfile.ZipFile(KMZ_FILE, 'r') as z:
            kmls = [f for f in z.namelist() if f.endswith('.kml')]
            if not kmls: return pd.DataFrame(disasters)
            root = ET.fromstring(z.read(kmls[0]))
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        for pm in root.findall('.//kml:Placemark', ns):
            name_node = pm.find('kml:name', ns)
            name = name_node.text.strip() if name_node is not None and name_node.text else "歷次災點"
            desc_node = pm.find('kml:description', ns)
            desc = desc_node.text.strip() if desc_node is not None and desc_node.text else ""
            coord_node = pm.find('.//kml:coordinates', ns)
            ym = re.search(r'(\d{2,3})年', f"{name} {desc}")
            dis_year = f"{ym.group(1)}年" if ym else "其他/歷史"
            if coord_node is not None and coord_node.text:
                parts = coord_node.text.strip().split()[0].split(',')
                if len(parts) >= 2:
                    disasters.append({"災害名稱": name, "年度": dis_year, "詳細說明": desc, "緯度": float(parts[1]), "經度": float(parts[0])})
    except Exception:
        pass
    return pd.DataFrame(disasters)

df = load_data()
df_disasters = load_kmz()

if df.empty:
    st.error(f"找不到邊坡資料檔案：{DATA_FILE}")
    st.stop()

# ==============================================================================
# 頁面 1：邊坡清冊
# ==============================================================================
if st.session_state.bottom_tab == "📋 邊坡清冊":
    if st.session_state.selected_slope_id is not None:
        if st.button("⬅️ 返回邊坡清冊主畫面", key="detail_back_btn", use_container_width=True, type="primary"):
            st.session_state.selected_slope_id = None
            st.rerun()

        matched = df[df['口卡編號'] == st.session_state.selected_slope_id]
        if not matched.empty:
            row = matched.iloc[0]
            q_grade = str(row['定性分級'])
            card_top = f"""<div class='app-card notranslate' translate='no'>
<div style='display:flex; justify-content:space-between; align-items:center;'>
<span style='font-size:19px; font-weight:700;'>📍 {row['路線']} {row['里程樁號(起)']}</span>
<span class='badge badge-{q_grade}'>{q_grade} 級</span>
</div>
<div style='font-family:monospace; font-size:12.5px; color:var(--text-muted); margin-top:3px;'>口卡：{row['口卡編號']}</div>
<div style='font-size:14px; font-weight:600; color:#4A6B82; margin-top:4px;'>構造物：{row.get('邊坡構造物', '自然邊坡')}</div>
</div>"""
            st.markdown(card_top, unsafe_allow_html=True)

            r_lat, r_lon = row.get('起點緯度'), row.get('起點經度')
            if pd.notna(r_lat) and pd.notna(r_lon):
                st.markdown("##### 🛰️ 現地空間衛星影像位置")
                embed_map = f"""<div class='embed-map-box notranslate' translate='no'>
<iframe width='100%' height='280' frameborder='0' scrolling='no' src='https://maps.google.com/maps?q={r_lat},{r_lon}&t=k&z=17&ie=UTF8&iwloc=&output=embed'></iframe>
</div>"""
                st.markdown(embed_map, unsafe_allow_html=True)
                gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={r_lat},{r_lon}"
                st.markdown(f"<div style='margin: 8px 0 16px 0;'><a href='{gmap_url}' target='_blank' style='display:block; text-align:center; padding:9px 12px; background:#4A6B82; color:white; font-weight:bold; border-radius:8px; text-decoration:none;'>🧭 開啟 Google Maps 導航至此處</a></div>", unsafe_allow_html=True)

            st.markdown("##### 📋 邊坡完整屬性資料（唯讀瀏覽）")
            detail_fields = [
                ("邊坡狀態", str(row.get('邊坡狀態', '無'))),
                ("工務段", str(row.get('工務段', '南澳工務段'))),
                ("路線 / 里程", f"{row.get('路線', '')} {row.get('里程樁號(起)', '')}"),
                ("起點經緯度", f"{r_lon:.5f}, {r_lat:.5f}" if pd.notna(r_lat) else "無"),
                ("坡高 / 坡度 / 面寬", f"{row.get('坡高', '')}m / {row.get('坡度', '')}° / {row.get('邊坡面寬', '')}m"),
                ("定性 / 定量分級", f"{q_grade}級 / {row.get('定量分級', '未施作')}"),
                ("災害歷史", str(row.get('災害歷史', '無'))),
                ("附近地名", str(row.get('附近地名', '無'))),
            ]
            rows_html = "".join([f"<div class='detail-row'><span class='detail-label'>{k}</span><span class='detail-value'>{v}</span></div>" for k, v in detail_fields])
            st.markdown(f"<div class='app-card notranslate' translate='no'>{rows_html}</div>", unsafe_allow_html=True)

            st.markdown("**現地狀況描述：**")
            st.markdown(f"<div class='app-card notranslate' translate='no' style='background:rgba(74, 107, 130, 0.12); border-left:4px solid #4A6B82; line-height:1.5;'>{row.get('現地狀況描述', '無描述紀錄')}</div>", unsafe_allow_html=True)

            if st.button("📝 前往填寫此邊坡之「養護巡查檢測表」", type="primary", use_container_width=True):
                st.session_state.bottom_tab = "📝 養護巡查"
                st.session_state.target_slope_for_patrol = row['口卡編號']
                st.rerun()
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            route_list = ["全部路線"] + list(df['路線'].dropna().unique())
            route_filter = st.selectbox("路線篩選", route_list)
        with col_f2:
            qual_filter = st.selectbox("分級篩選", ["全部分級", "A", "B", "C", "D", "其他"])

        search_kw = st.text_input("🔍 搜尋里程、卡號或地名", placeholder="例如: 8k+600、隘丁")
        f_df = df.copy()
        if route_filter != "全部路線": f_df = f_df[f_df['路線'] == route_filter]
        if qual_filter != "全部分級": f_df = f_df[f_df['定性分級'] == qual_filter]
        if search_kw:
            f_df = f_df[f_df['口卡編號'].astype(str).str.contains(search_kw, case=False) | f_df['里程樁號(起)'].astype(str).str.contains(search_kw, case=False) | f_df['附近地名'].astype(str).str.contains(search_kw, case=False)]

        q_counts = f_df['定性分級'].value_counts()
        st.caption(f"符合條件邊坡：**{len(f_df)}** 處（總資產：{len(df)} 處） 點擊下方各級按鈕查看對應樁號：")

        b_cols = st.columns(5)
        for idx, g in enumerate(["A", "B", "C", "D", "其他"]):
            with b_cols[idx]:
                if st.button(f"{g}級 ({q_counts.get(g, 0)})", key=f"badge_btn_{g}", use_container_width=True):
                    st.session_state.active_grade_detail = g if st.session_state.active_grade_detail != g else None
                    st.rerun()

        if st.session_state.active_grade_detail:
            sel_g = st.session_state.active_grade_detail
            g_sub_df = f_df[f_df['定性分級'] == sel_g]
            with st.container(border=True):
                st.markdown(f"**📌【{sel_g} 級】邊坡樁號清冊（共 {len(g_sub_df)} 處）：**")
                g_cols = st.columns(2)
                for idx, (_, g_row) in enumerate(g_sub_df.iterrows()):
                    with g_cols[idx % 2]:
                        if st.button(f"📍 {g_row['路線']} {g_row['里程樁號(起)']}", key=f"quick_pick_{g_row['口卡編號']}", use_container_width=True):
                            st.session_state.selected_slope_id = g_row['口卡編號']
                            st.rerun()

        st.markdown("<hr style='margin: 12px 0 16px 0; border: none; border-top: 1px solid var(--card-border);' />", unsafe_allow_html=True)

        for r_name in f_df['路線'].dropna().unique():
            sub_df = f_df[f_df['路線'] == r_name]
            total_sub = len(sub_df)
            with st.expander(f"🛣️ **{r_name}**（共 {total_sub} 處）", expanded=False):
                show_all = False
                if total_sub > 10:
                    show_all = st.checkbox(f"展開全部 {total_sub} 筆（預設前 10 筆）", key=f"chk_{r_name}")
                display_df = sub_df if show_all else sub_df.head(10)
                for _, r in display_df.iterrows():
                    grade = str(r['定性分級'])
                    with st.container(border=True):
                        if st.button(f"📍 {r['里程樁號(起)']}  [{grade}級]", key=f"pick_{r['口卡編號']}", use_container_width=True):
                            st.session_state.selected_slope_id = r['口卡編號']
                            st.rerun()
                        st.caption(f"卡號：`{r['口卡編號']}` ｜ 構造：`{r.get('邊坡構造物', '自然邊坡')[:18]}`")

# ==============================================================================
# 頁面 2：定量定性分級統計
# ==============================================================================
elif st.session_state.bottom_tab == "📊 定量定性":
    st.markdown("<div class='system-title notranslate' translate='no' style='text-align:center;'>邊坡定量定性分級統計</div>", unsafe_allow_html=True)
    chart_type = st.radio("📈 圖表呈現模式", ["圓餅圖 (Pie Chart)", "長條圖 (Bar Chart)"], horizontal=True)

    qual_order = ["A", "B", "C", "D", "其他"]
    c_counts = df['定性分級'].value_counts()
    qual_df = pd.DataFrame({"分級": qual_order, "數量": [c_counts.get(c, 0) for c in qual_order]})
    qual_color = {"A": "#c05646", "B": "#d9822b", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}

    if "圓餅圖" in chart_type:
        fig_qual = px.pie(qual_df, values='數量', names='分級', hole=0.45, color='分級', color_discrete_map=qual_color, category_orders={"分級": qual_order})
        fig_qual.update_traces(textposition='inside', textinfo='percent+label+value', insidetextfont=dict(color="#ffffff", size=13), sort=False)
        fig_qual.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color))
        st.plotly_chart(fig_qual, use_container_width=True)
    else:
        fig_qual = px.bar(qual_df, x="分級", y="數量", text="數量", color="分級", color_discrete_map=qual_color, category_orders={"分級": qual_order})
        fig_qual.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=280, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color))
        st.plotly_chart(fig_qual, use_container_width=True)

    st.markdown("---")
    quant_order = ["第1級", "第2級", "第3級", "第4級", "第5級", "未施作"]
    quant_color = {"第1級": "#1e40af", "第2級": "#3b82f6", "第3級": "#f97316", "第4級": "#ef4444", "第5級": "#b91c1c", "未施作": "#10b981"}
    q_counts = df['定量分級'].value_counts()
    quant_df = pd.DataFrame({"定量分級": quant_order, "數量": [q_counts.get(c, 0) for c in quant_order]})

    if "圓餅圖" in chart_type:
        fig_quant = px.pie(quant_df, values='數量', names='定量分級', hole=0.45, color='定量分級', color_discrete_map=quant_color, category_orders={"定量分級": quant_order})
        fig_quant.update_traces(textposition='inside', textinfo='percent+label+value', insidetextfont=dict(color="#ffffff", size=13), sort=False)
        fig_quant.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color))
        st.plotly_chart(fig_quant, use_container_width=True)
    else:
        fig_quant = px.bar(quant_df, x="定量分級", y="數量", text="數量", color="定量分級", color_discrete_map=quant_color, category_orders={"定量分級": quant_order})
        fig_quant.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=280, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color))
        st.plotly_chart(fig_quant, use_container_width=True)

# ==============================================================================
# 頁面 3：地圖定位
# ==============================================================================
elif st.session_state.bottom_tab == "🗺️ 地圖定位":
    st.markdown("<div class='system-title notranslate' translate='no' style='text-align:center;'>邊坡空間地圖定位</div>", unsafe_allow_html=True)
    valid_pts = df.dropna(subset=['起點緯度', '起點經度'])
    if not valid_pts.empty:
        m_loc = folium.Map(location=[valid_pts['起點緯度'].median(), valid_pts['起點經度'].median()], zoom_start=11, tiles=None)
        LocateControl(auto_start=False, flyTo=True).add_to(m_loc)
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Earth", name="🛰️ 衛星空照圖").add_to(m_loc)
        folium.TileLayer(tiles="OpenStreetMap", name="🗺️ 標準電子地圖").add_to(m_loc)
        cmap = {"A": "#c05646", "B": "#d9822b", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}
        for _, r in valid_pts.iterrows():
            g = str(r['定性分級'])
            p_lat, p_lon = r['起點緯度'], r['起點經度']
            popup = f"<b>{r['路線']} {r['里程樁號(起)']}</b><br/>卡號：{r['口卡編號']}<br/>分級：{g}級<br/><a href='https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}' target='_blank'>🧭 導航至此處</a>"
            folium.CircleMarker(location=[p_lat, p_lon], radius=6, popup=popup, color=cmap.get(g, '#64748b'), fill=True, fill_opacity=0.85).add_to(m_loc)
        folium.LayerControl(position="topright").add_to(m_loc)
        st_folium(m_loc, width="100%", height=530)

# ==============================================================================
# 頁面 4：災害斑點圖
# ==============================================================================
elif st.session_state.bottom_tab == "🔥 災害斑點圖":
    st.markdown("<div class='map-sub-title notranslate' translate='no'>歷次災害斑點圖</div>", unsafe_allow_html=True)
    if not df_disasters.empty:
        m_dis = folium.Map(location=[df_disasters['緯度'].median(), df_disasters['經度'].median()], zoom_start=11, tiles=None)
        LocateControl(auto_start=False, flyTo=True).add_to(m_dis)
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Earth", name="🛰️ 衛星空照圖").add_to(m_dis)
        folium.TileLayer(tiles="OpenStreetMap", name="🗺️ 標準電子地圖").add_to(m_dis)
        yp = {"113年": "#e63946", "114年": "#f77f00", "112年": "#457b9d", "115年": "#2a9d8f"}
        for yr in sorted(df_disasters['年度'].unique()):
            fg = folium.FeatureGroup(name=f"📍 {yr}")
            for _, d in df_disasters[df_disasters['年度'] == yr].iterrows():
                pop = f"<b>{d['災害名稱']}</b><br/>{d['詳細說明']}"
                folium.CircleMarker(location=[d['緯度'], d['經度']], radius=5.5, popup=pop, color=yp.get(yr, "#8338ec"), fill=True, fill_opacity=0.9).add_to(fg)
            fg.add_to(m_dis)
        folium.LayerControl(position="topright").add_to(m_dis)
        st_folium(m_dis, width="100%", height=600)

# ==============================================================================
# 頁面 5：養護巡查
# ==============================================================================
elif st.session_state.bottom_tab == "📝 養護巡查":
    st.markdown("<div class='system-title notranslate' translate='no' style='text-align:center;'>邊坡養護巡查檢測系統</div>", unsafe_allow_html=True)
    st.caption("📱 外業專用檢測表：支援斷點暫存、接電話防跳出、即時拍照，並產出公務標準 .doc 文件。")

    slope_opts = df['口卡編號'].dropna().unique().tolist()
    def_idx = slope_opts.index(st.session_state.target_slope_for_patrol) if "target_slope_for_patrol" in st.session_state and st.session_state.target_slope_for_patrol in slope_opts else 0
    chosen_code = st.selectbox("🎯 巡查目標口卡編號", slope_opts, index=def_idx)
    target_row = df[df['口卡編號'] == chosen_code].iloc[0]

    raw_s = str(target_row.get('邊坡構造物', '自然邊坡'))
    avail_s = list(dict.fromkeys([s.strip() for s in re.split(r'[,、]', raw_s) if s.strip()] + ["自然邊坡"]))
    chosen_struct = st.selectbox("構造物設施類別", avail_s)
    current_tpl = INSPECTION_TEMPLATES[match_template(chosen_struct)]

    st.info(f"📋 目前依據規範載入：**【{current_tpl['title']}】**（自動帶入 {len(current_tpl['items'])} 項標準規範）")
    draft = st.session_state.patrol_draft.get(f"{chosen_code}_{chosen_struct}", {})

    c1, c2, c3 = st.columns(3)
    with c1: f_date = st.date_input("檢測日期", draft.get("date", datetime.date.today()))
    with c2: f_weather = st.selectbox("天氣狀況", ["晴", "陰", "雨"], index=["晴", "陰", "雨"].index(draft.get("weather", "晴")))
    with c3: f_type = st.selectbox("檢測類別", ["定期檢測", "特別檢測"], index=["定期檢測", "特別檢測"].index(draft.get("type", "定期檢測")))

    cg1, cg2 = st.columns(2)
    with cg1: f_geo = st.selectbox("地質狀況", ["土層邊坡", "岩層邊坡", "礫石層邊坡", "其他地質"], index=["土層邊坡", "岩層邊坡", "礫石層邊坡", "其他地質"].index(draft.get("geo", "土層邊坡")))
    with cg2: f_water = st.selectbox("地下水／排水湧水狀況", ["乾燥", "濕潤", "表面水", "湧水"], index=["乾燥", "濕潤", "表面水", "湧水"].index(draft.get("water", "乾燥")))

    cg3, cg4 = st.columns(2)
    with cg3: f_drain = st.selectbox("排(洩)水管", ["正常", "阻塞"], index=["正常", "阻塞"].index(draft.get("drain", "正常")))
    with cg4: f_disaster = st.selectbox("以往災害歷史", ["無", "有"], index=["無", "有"].index(draft.get("disaster", "無")))

    st.markdown("#### 設施檢測項目")
    item_results = []
    draft_items = draft.get("items", {})

    for idx, (iname, iact) in enumerate(current_tpl["items"]):
        ci1, ci2 = st.columns([0.65, 0.35])
        with ci1:
            st.markdown(f"**{iname}**")
            st.caption(f"養護措施：{iact}")
        with ci2:
            prev_res = draft_items.get(iname, {}).get("res", "○ 正常")
            res_val = st.radio("結果", ["○ 正常", "× 異常", "／ 無此項"], index=["○ 正常", "× 異常", "／ 無此項"].index(prev_res) if prev_res in ["○ 正常", "× 異常", "／ 無此項"] else 0, horizontal=True, key=f"patrol_res_{idx}", label_visibility="collapsed")
        desc_val = st.text_input(f"【{iname}】異常情形/處理說明", value=draft_items.get(iname, {}).get("desc", ""), key=f"patrol_desc_{idx}") if "×" in res_val else ""
        item_results.append((iname, iact, res_val[0], desc_val))

    # ==========================================================================
    # ★★★ 相機與照片記錄升級：原生手機/平板主相機、前後翻轉與連拍多選 ★★★
    # ==========================================================================
    st.markdown("#### 四、 現地拍照記錄與署名")
    st.caption("💡 **外業拍照建議**：點擊下方 **「📸 開啟相機拍照／相簿多選」**，系統將直接啟動行動裝置的原生相機，**可自由翻轉切換後置主鏡頭、超廣角 (0.5x) 或望遠鏡頭**，並支援連續拍攝多張邊坡照片！")

    cp1, cp2 = st.columns(2)
    with cp1:
        f_photos = st.file_uploader(
            "📸 開啟相機拍照／相簿多選 (推薦，原生支援切換前後鏡頭與超廣角)",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            help="手機或平板點擊即可調用原生相機拍攝，支援後置鏡頭翻轉、望遠與連續多張拍攝。"
        )
    with cp2:
        f_camera = st.camera_input("📷 網頁即時拍照 (單張快速紀錄)")

    f_remark = st.text_area("現地綜合備註", value=draft.get("remark", ""), placeholder="請輸入邊坡現況其他補充說明...")
    cu1, cu2 = st.columns(2)
    with cu1: f_inspector = st.text_input("檢測人員姓名 (必填)", value=draft.get("inspector", ""), placeholder="例如：李工程師")
    with cu2: f_supervisor = st.text_input("單位主管 (選填)", value=draft.get("supervisor", ""), placeholder="例如：段長")

    act_col1, act_col2 = st.columns(2)
    with act_col1:
        if st.button("💾 暫存草稿 (防跳出遺失)", use_container_width=True):
            st.session_state.patrol_draft[f"{chosen_code}_{chosen_struct}"] = {
                "date": f_date, "weather": f_weather, "type": f_type, "geo": f_geo, "water": f_water,
                "drain": f_drain, "disaster": f_disaster, "remark": f_remark, "inspector": f_inspector,
                "supervisor": f_supervisor, "items": {item[0]: {"res": item[2], "desc": item[3]} for item in item_results}
            }
            st.success("✅ 草稿已暫存！即便接電話、關閉頁面或跳到其他分頁，再回來內容都在。")

    with act_col2:
        export_name = f"邊坡口卡編號{chosen_code}-構造物{chosen_struct}.doc"
        report_data = {
            "title": current_tpl.get("title"),
            "category_col_header": current_tpl.get("category_col_header"),
            "category_name": current_tpl.get("category_name"),
            "dim_title": current_tpl.get("dim_title"),
            "dim_h_label": current_tpl.get("dim_h_label"),
            "dim_w_label": current_tpl.get("dim_w_label"),
            "code": chosen_code,
            "date": f_date.strftime("%Y年%m月%d日"),
            "weather": f_weather,
            "type": f_type,
            "unit": "南澳工務段",
            "location": f"{target_row.get('鄉鎮市區', '蘇澳鎮')} {target_row.get('路線', '')} {target_row.get('里程樁號(起)', '')}",
            "direction": target_row.get("方向", "北下"),
            "geo": f_geo,
            "height": target_row.get("坡高", "30"),
            "slope": target_row.get("坡度", "85"),
            "width": target_row.get("邊坡面寬", "200"),
            "water": f_water,
            "drain": f_drain,
            "survey_month": f_date.month,
            "rain_days": "3",
            "check_rows": item_results,
            "remark": f_remark.strip() if f_remark.strip() else current_tpl.get("remark_default", ""),
            "inspector": f_inspector,
            "supervisor": f_supervisor
        }
        p_bytes = [p.getvalue() for p in (f_photos or [])] + ([f_camera.getvalue()] if f_camera else [])
        doc_bytes = generate_doc_report(report_data, p_bytes)
        st.download_button(label=f"📥 產出並下載 {export_name}", data=doc_bytes, file_name=export_name, mime="application/msword", type="primary", use_container_width=True)

# 頁尾
st.markdown(render_footer(), unsafe_allow_html=True)