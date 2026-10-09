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
from PIL import Image
import io

# 匯入樣式與規範模組
from style import get_theme_css, render_footer
from inspection_schema import INSPECTION_TEMPLATES, match_template, generate_doc_report

st.set_page_config(
    page_title="南澳邊坡全生命週期資料庫",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 狀態管理
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "🌙 深色黑底"
if "bottom_tab" not in st.session_state:
    st.session_state.bottom_tab = "📋 邊坡清冊"
if "selected_slope_id" not in st.session_state:
    st.session_state.selected_slope_id = None
if "active_grade_detail" not in st.session_state:
    st.session_state.active_grade_detail = None

# 外業巡查草稿暫存區（防止電話打斷、意外跳出遺失內容）
if "patrol_draft" not in st.session_state:
    st.session_state.patrol_draft = {}

is_light = (st.session_state.theme_mode == "☀️ 淺色白底")
plotly_font_color = "#0f172a" if is_light else "#f8fafc"

st.markdown(get_theme_css(is_light), unsafe_allow_html=True)

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

def normalize_quant(val):
    if pd.isna(val):
        return "未施作"
    s = str(val).strip()
    if s in ["", "nan", "None", "未施作", "未施作定量評估", "無"]:
        return "未施作"
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

# 唯讀載入主檔案
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_excel(DATA_FILE)
    df['起點緯度'] = pd.to_numeric(df['起點緯度'], errors='coerce')
    df['起點經度'] = pd.to_numeric(df['起點經度'], errors='coerce')
    df['定性分級'] = df['定性分級'].fillna('其他').astype(str).str.strip()
    if '定量分級' in df.columns:
        df['定量分級'] = df['定量分級'].apply(normalize_quant)
    else:
        df['定量分級'] = "未施作"
    return df

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
# 頁面 1：邊坡清冊（唯讀查詢檢索，資料絕不更改）
# ==============================================================================
if st.session_state.bottom_tab == "📋 邊坡清冊":
    if st.session_state.selected_slope_id is not None:
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
                embed_map_html = f"""<div class='embed-map-box notranslate' translate='no'>
<iframe width='100%' height='280' frameborder='0' scrolling='no' marginheight='0' marginwidth='0' src='https://maps.google.com/maps?q={r_lat},{r_lon}&t=k&z=17&ie=UTF8&iwloc=&output=embed'></iframe>
</div>"""
                st.markdown(embed_map_html, unsafe_allow_html=True)

                gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={r_lat},{r_lon}"
                nav_link = f"""<div style='margin: 8px 0 16px 0;' class='notranslate' translate='no'>
<a href='{gmap_url}' target='_blank' style='display:block; text-align:center; padding:9px 12px; background:#4A6B82; color:white; font-weight:bold; border-radius:8px; text-decoration:none; font-size:14px;'>🧭 開啟 Google Maps 導航至此處（依目前位置規劃路線）</a></div>"""
                st.markdown(nav_link, unsafe_allow_html=True)

            st.markdown("##### 📋 邊坡完整屬性資料（唯讀瀏覽）")
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
                ("附近地名", str(row.get('附近地名', '無'))),
            ]

            rows_html = "".join([f"<div class='detail-row'><span class='detail-label'>{k}</span><span class='detail-value'>{v}</span></div>" for k, v in detail_fields])
            st.markdown(f"<div class='app-card notranslate' translate='no'>{rows_html}</div>", unsafe_allow_html=True)

            st.markdown("**現地狀況歷史紀錄：**")
            desc_val = str(row.get('現地狀況描述', '無描述紀錄'))
            desc_html = f"""<div class='app-card notranslate' translate='no' style='background:rgba(74, 107, 130, 0.12); border-left:4px solid #4A6B82; line-height:1.5; font-size:14px;'>{desc_val}</div>"""
            st.markdown(desc_html, unsafe_allow_html=True)

            # 快速導流鍵：直接帶此卡號進入「養護巡查」
            if st.button("📝 前往填寫此邊坡之「養護巡查檢測表」", type="primary", use_container_width=True):
                st.session_state.bottom_tab = "📝 養護巡查"
                st.session_state.target_slope_for_patrol = row['口卡編號']
                st.rerun()

    else:
        st.markdown("<div class='system-title notranslate' translate='no'>南澳邊坡全生命週期資料庫</div>", unsafe_allow_html=True)

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

        q_counts = f_df['定性分級'].value_counts()
        cnt_a = q_counts.get("A", 0)
        cnt_b = q_counts.get("B", 0)
        cnt_c = q_counts.get("C", 0)
        cnt_d = q_counts.get("D", 0)
        cnt_o = q_counts.get("其他", 0)

        st.caption(f"符合條件邊坡：**{len(f_df)}** 處（總資產：{len(df)} 處） 點擊下方各級按鈕查看對應樁號：")

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

        if st.session_state.active_grade_detail:
            selected_grade = st.session_state.active_grade_detail
            grade_sub_df = f_df[f_df['定性分級'] == selected_grade]
            with st.container(border=True):
                st.markdown(f"**📌【{selected_grade} 級】邊坡樁號清冊（共 {len(grade_sub_df)} 處）：**")
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
# 頁面 2：定量定性分級統計
# ==============================================================================
elif st.session_state.bottom_tab == "📊 定量定性":
    st.markdown("<div class='system-title notranslate' translate='no'>邊坡定量定性分級統計</div>", unsafe_allow_html=True)
    chart_type = st.radio("📈 圖表呈現模式", ["圓餅圖 (Pie Chart)", "長條圖 (Bar Chart)"], horizontal=True)

    st.markdown("<div class='notranslate' translate='no' style='font-size:16.5px; font-weight:700; color:var(--text-main); margin-top:8px; margin-bottom:6px;'>1. 定性分級統計 (A, B, C, D, 其他)</div>", unsafe_allow_html=True)
    qual_order = ["A", "B", "C", "D", "其他"]
    c_counts = df['定性分級'].value_counts()
    qual_df = pd.DataFrame({"分級": qual_order, "數量": [c_counts.get(c, 0) for c in qual_order]})
    qual_color_map = {"A": "#c05646", "B": "#d9822b", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}

    if "圓餅圖" in chart_type:
        fig_qual = px.pie(
            qual_df, values='數量', names='分級', hole=0.45,
            color='分級', color_discrete_map=qual_color_map, category_orders={"分級": qual_order}
        )
        fig_qual.update_traces(textposition='inside', textinfo='percent+label+value', insidetextfont=dict(color="#ffffff", size=13), sort=False)
        fig_qual.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=310, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color), legend=dict(font=dict(color=plotly_font_color, size=13)))
        st.plotly_chart(fig_qual, use_container_width=True)
    else:
        fig_qual = px.bar(qual_df, x="分級", y="數量", text="數量", color="分級", color_discrete_map=qual_color_map, category_orders={"分級": qual_order})
        fig_qual.update_traces(textposition='outside')
        fig_qual.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=290, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color), xaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)), yaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)), legend=dict(font=dict(color=plotly_font_color)))
        st.plotly_chart(fig_qual, use_container_width=True)

    st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--card-border);' />", unsafe_allow_html=True)

    st.markdown("<div class='notranslate' translate='no' style='font-size:16.5px; font-weight:700; color:var(--text-main); margin-top:8px; margin-bottom:6px;'>2. 定量分級統計 (第1級 ~ 第5級 / 未施作)</div>", unsafe_allow_html=True)
    quant_order = ["第1級", "第2級", "第3級", "第4級", "第5級", "未施作"]
    quant_color_map = {"第1級": "#1e40af", "第2級": "#3b82f6", "第3級": "#f97316", "第4級": "#ef4444", "第5級": "#b91c1c", "未施作": "#10b981"}
    q_counts = df['定量分級'].value_counts()
    quant_df = pd.DataFrame({"定量分級": quant_order, "數量": [q_counts.get(c, 0) for c in quant_order]})

    if "圓餅圖" in chart_type:
        fig_quant = px.pie(quant_df, values='數量', names='定量分級', hole=0.45, color='定量分級', color_discrete_map=quant_color_map, category_orders={"定量分級": quant_order})
        fig_quant.update_traces(textposition='inside', textinfo='percent+label+value', insidetextfont=dict(color="#ffffff", size=13), sort=False)
        fig_quant.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=310, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color), legend=dict(font=dict(color=plotly_font_color, size=13)))
        st.plotly_chart(fig_quant, use_container_width=True)
    else:
        fig_quant = px.bar(quant_df, x="定量分級", y="數量", text="數量", color="定量分級", color_discrete_map=quant_color_map, category_orders={"定量分級": quant_order})
        fig_quant.update_traces(textposition='outside')
        fig_quant.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=290, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color), xaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)), yaxis=dict(tickfont=dict(color=plotly_font_color), title_font=dict(color=plotly_font_color)), legend=dict(font=dict(color=plotly_font_color)))
        st.plotly_chart(fig_quant, use_container_width=True)

# ==============================================================================
# 頁面 3：地圖定位
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
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Earth 衛星空照圖", name="🛰️ Google Earth 衛星圖", overlay=False, control=True).add_to(m_loc)
        folium.TileLayer(tiles="OpenStreetMap", name="🗺️ 標準電子地圖", overlay=False, control=True).add_to(m_loc)
        cmap = {"A": "#c05646", "B": "#d9822b", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}
        for _, r in valid_pts.iterrows():
            g = str(r['定性分級'])
            color = cmap.get(g, '#64748b')
            p_lat, p_lon = r['起點緯度'], r['起點經度']
            gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}"
            popup_html = f"""<div translate='no' class='notranslate' style='font-family:sans-serif; font-size:13.5px; line-height:1.45;'>
<b style='font-size:14.5px; color:#0f172a;'>{r['路線']} {r['里程樁號(起)']}</b><br/>
<b>卡號：</b>{r['口卡編號']}<br/>
<b>定性分級：</b><span style='color:{color}; font-weight:bold;'>{g} 級</span><br/>
<b>構造物：</b>{r.get('邊坡構造物', '自然邊坡')}<br/>
<a href='{gmap_url}' target='_blank' style='display:inline-block; margin-top:6px; padding:4px 9px; background:#4A6B82; color:white; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;'>🧭 導航到此里程</a>
</div>"""
            folium.CircleMarker(location=[p_lat, p_lon], radius=6, popup=folium.Popup(popup_html, max_width=260), color=color, fill=True, fill_color=color, fill_opacity=0.85).add_to(m_loc)
        folium.LayerControl(position="topright", collapsed=True).add_to(m_loc)
        st_folium(m_loc, width="100%", height=530)

# ==============================================================================
# 頁面 4：災害斑點圖
# ==============================================================================
elif st.session_state.bottom_tab == "🔥 災害斑點圖":
    st.markdown("<div class='map-sub-title notranslate' translate='no'>歷次災害斑點圖</div>", unsafe_allow_html=True)
    if not df_disasters.empty:
        c_lat = df_disasters['緯度'].median()
        c_lon = df_disasters['經度'].median()
        m_dis = folium.Map(location=[c_lat, c_lon], zoom_start=11, tiles=None)
        LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=False).add_to(m_dis)
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Earth 衛星空照圖", name="🛰️ Google Earth 衛星圖", overlay=False, control=True).add_to(m_dis)
        folium.TileLayer(tiles="OpenStreetMap", name="🗺️ 標準電子地圖", overlay=False, control=True).add_to(m_dis)
        year_palette = {"113年": "#e63946", "114年": "#f77f00", "112年": "#457b9d", "115年": "#2a9d8f", "其他/歷史": "#6c757d"}
        for yr in sorted(df_disasters['年度'].unique()):
            yr_df = df_disasters[df_disasters['年度'] == yr]
            yr_color = year_palette.get(yr, "#8338ec")
            yr_layer = folium.FeatureGroup(name=f"📍 {yr} ({len(yr_df)}處)", show=True)
            for _, d in yr_df.iterrows():
                d_lat, d_lon = d['緯度'], d['經度']
                d_gurl = f"https://www.google.com/maps/dir/?api=1&destination={d_lat},{d_lon}"
                d_popup = f"""<div translate='no' class='notranslate' style='font-family:sans-serif; font-size:13.5px; line-height:1.45;'>
<span style='background:{yr_color}; color:white; padding:2px 6px; border-radius:3px; font-size:11px; font-weight:bold;'>{yr} 災害斑點</span><br/>
<b style='color:#0f172a; font-size:13.5px; margin-top:4px; display:inline-block;'>{d['災害名稱']}</b><br/>
{d['詳細說明']}<br/>
<a href='{d_gurl}' target='_blank' style='display:inline-block; margin-top:5px; padding:3px 8px; background:#4A6B82; color:white; border-radius:4px; text-decoration:none; font-size:12px; font-weight:bold;'>🧭 導航至此災點</a>
</div>"""
                folium.CircleMarker(location=[d_lat, d_lon], radius=5.5, popup=folium.Popup(d_popup, max_width=260), color="#2b2d42", weight=1, fill=True, fill_color=yr_color, fill_opacity=0.9).add_to(yr_layer)
            yr_layer.add_to(m_dis)
        folium.LayerControl(position="topright", collapsed=True).add_to(m_dis)
        st_folium(m_dis, width="100%", height=620)

    if st.button("⬅️ 返回主畫面 (邊坡清冊)", key="map_bottom_back_btn", use_container_width=True, type="primary"):
        st.session_state.bottom_tab = "📋 邊坡清冊"
        st.session_state.selected_slope_id = None
        st.rerun()

# ==============================================================================
# 頁面 5：全新「📝 養護巡查」獨立作業空間（支援外業草稿暫存與 .doc 匯出）
# ==============================================================================
elif st.session_state.bottom_tab == "📝 養護巡查":
    st.markdown("<div class='system-title notranslate' translate='no'>邊坡養護巡查檢測系統</div>", unsafe_allow_html=True)
    st.caption("📱 外業專用檢測表：支援斷點暫存、接電話防跳出、現場即時相片拍照，並產出公務標準 .doc 檢測文件。")

    # 1. 快速選定口卡編號
    slope_options = df['口卡編號'].dropna().unique().tolist()
    default_idx = 0
    if "target_slope_for_patrol" in st.session_state and st.session_state.target_slope_for_patrol in slope_options:
        default_idx = slope_options.index(st.session_state.target_slope_for_patrol)

    chosen_code = st.selectbox("🎯 巡查目標口卡編號", slope_options, index=default_idx)
    target_row = df[df['口卡編號'] == chosen_code].iloc[0]

    # 自動解析可用構造物
    raw_structs = str(target_row.get('邊坡構造物', '自然邊坡'))
    avail_structs = [s.strip() for s in re.split(r'[,、]', raw_structs) if s.strip()]
    if not avail_structs:
        avail_structs = ["自然邊坡"]
    avail_structs.append("自然邊坡")
    avail_structs = list(dict.fromkeys(avail_structs)) # 去除重複

    chosen_struct = st.selectbox("構造物設施類別", avail_structs)
    tpl_key = match_template(chosen_struct)
    current_tpl = INSPECTION_TEMPLATES[tpl_key]

    st.info(f"📋 目前依據規範載入：**【{current_tpl['title']}】**（自動帶入 {len(current_tpl['items'])} 項公路局標準檢測規範）")

    # 讀取現有草稿（若曾暫存過）
    draft = st.session_state.patrol_draft.get(f"{chosen_code}_{chosen_struct}", {})

    # 表單欄位
    st.markdown("#### 一、 基本檢測環境")
    c1, c2, c3 = st.columns(3)
    with c1:
        f_date = st.date_input("檢測日期", draft.get("date", datetime.date.today()))
    with c2:
        f_weather = st.selectbox("天氣狀況", ["晴", "陰", "雨"], index=["晴", "陰", "雨"].index(draft.get("weather", "晴")))
    with c3:
        f_type = st.selectbox("檢測類別", ["定期檢測", "特別檢測"], index=["定期檢測", "特別檢測"].index(draft.get("type", "定期檢測")))

    c4, c5 = st.columns(2)
    with c4:
        st.text_input("養護單位", value="南澳工務段", disabled=True)
    with c5:
        loc_str = f"{target_row.get('縣市', '宜蘭縣')}{target_row.get('鄉鎮市區', '')} {target_row.get('路線', '')} {target_row.get('里程樁號(起)', '')}"
        st.text_input("檢查位置與里程", value=loc_str, disabled=True)

    st.markdown("#### 二、 現場狀況與地質水文")
    cg1, cg2 = st.columns(2)
    with cg1:
        f_geo = st.selectbox("地質狀況", ["土層邊坡", "岩層邊坡", "礫石層邊坡", "其他地質"], index=["土層邊坡", "岩層邊坡", "礫石層邊坡", "其他地質"].index(draft.get("geo", "土層邊坡")))
    with cg2:
        f_water = st.selectbox("地下水／排水湧水狀況", ["乾燥", "濕潤", "表面水", "湧水"], index=["乾燥", "濕潤", "表面水", "湧水"].index(draft.get("water", "乾燥")))

    cg3, cg4 = st.columns(2)
    with cg3:
        f_drain = st.selectbox("排(洩)水管", ["正常", "阻塞"], index=["正常", "阻塞"].index(draft.get("drain", "正常")))
    with cg4:
        f_disaster = st.selectbox("以往災害歷史", ["無", "有"], index=["無", "有"].index(draft.get("disaster", "無")))

    st.markdown("#### 三、 設施類別檢測項目（依公路局規範）")
    st.caption("結果填寫標準：**○ (正常)** ｜ **× (異常)** ｜ **／ (無此項)**")

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
        
        prev_desc = draft_items.get(iname, {}).get("desc", "")
        desc_val = ""
        if "×" in res_val:
            desc_val = st.text_input(f"【{iname}】異常情形 / 處理說明", value=prev_desc, placeholder="請說明異常狀況與處理建議...", key=f"patrol_desc_{idx}")
        item_results.append((iname, iact, res_val[0], desc_val))
        st.markdown("<hr style='margin: 4px 0 10px 0; border: none; border-top: 1px dashed rgba(255,255,255,0.08);' />", unsafe_allow_html=True)

    st.markdown("#### 四、 現地拍照記錄與署名")
    cp1, cp2 = st.columns(2)
    with cp1:
        f_photos = st.file_uploader("📷 上傳照片 (支援多張)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    with cp2:
        f_camera = st.camera_input("📸 開啟相機直接拍照")

    f_remark = st.text_area("現地綜合備註", value=draft.get("remark", ""), placeholder="其他補充說明...")

    cu1, cu2 = st.columns(2)
    with cu1:
        f_inspector = st.text_input("檢測人員姓名 (必填)", value=draft.get("inspector", ""), placeholder="例如：李工程師")
    with cu2:
        f_supervisor = st.text_input("單位主管 (選填)", value=draft.get("supervisor", ""), placeholder="例如：段長")

    # 外業斷點作業控制列（暫存 vs 產出正式報表）
    st.markdown("---")
    act_col1, act_col2 = st.columns(2)

    with act_col1:
        if st.button("💾 暫存草稿 (防接電話/跳出頁面遺失)", use_container_width=True):
            # 儲存至 Session State
            saved_draft = {
                "date": f_date, "weather": f_weather, "type": f_type,
                "geo": f_geo, "water": f_water, "drain": f_drain, "disaster": f_disaster,
                "remark": f_remark, "inspector": f_inspector, "supervisor": f_supervisor,
                "items": {item[0]: {"res": item[2], "desc": item[3]} for item in item_results}
            }
            st.session_state.patrol_draft[f"{chosen_code}_{chosen_struct}"] = saved_draft
            st.success("✅ 草稿已暫存！即便接電話、關閉頁面或跳到其他分頁，再回來內容都在。")

    with act_col2:
        # 產製報表資料集
        export_filename = f"邊坡口卡編號{chosen_code}-構造物{chosen_struct}.doc"
        report_data = {
            "title": current_tpl["title"],
            "code": chosen_code,
            "date": f_date.strftime("%Y年%m月%d日"),
            "weather": f_weather,
            "unit": "南澳工務段",
            "location": loc_str,
            "geo": f_geo,
            "water": f_water,
            "height": target_row.get("坡高", "—"),
            "slope": target_row.get("坡度", "—"),
            "width": target_row.get("邊坡面寬", "—"),
            "drain": f_drain,
            "disaster": f_disaster,
            "check_rows": item_results,
            "remark": f_remark,
            "inspector": f_inspector,
            "supervisor": f_supervisor
        }

        # 讀取上傳與拍攝之照片 Bytes
        photo_bytes_list = []
        if f_photos:
            for p in f_photos:
                photo_bytes_list.append(p.getvalue())
        if f_camera:
            photo_bytes_list.append(f_camera.getvalue())

        doc_bytes = generate_doc_report(report_data, photo_bytes_list)

        st.download_button(
            label=f"📥 產出並下載 {export_filename}",
            data=doc_bytes,
            file_name=export_filename,
            mime="application/msword",
            type="primary",
            use_container_width=True
        )

# ==============================================================================
# 底部 5 功能導航條（橫式排列：包含全新 📝 養護巡查）
# ==============================================================================
nav_cols = st.columns(5)
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

with nav_cols[4]:
    if st.button("📝 養護巡查", key="nav_btn_5", use_container_width=True, type="primary" if st.session_state.bottom_tab == "📝 養護巡查" else "secondary"):
        st.session_state.bottom_tab = "📝 養護巡查"
        st.rerun()

# 頁尾 LOGO
st.markdown(render_footer(), unsafe_allow_html=True)