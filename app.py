import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os
import datetime
import zipfile
import xml.etree.ElementTree as ET
import re
from PIL import Image

# 1. 頁面設定
st.set_page_config(
    page_title="南澳段邊坡管理系統",
    page_icon="⛰️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 注入精準專業 CSS（適配手機防遮擋、隱藏簡體翻譯、精緻卡片）
st.markdown("""
<script>
    document.documentElement.setAttribute("translate", "no");
    document.documentElement.classList.add("notranslate");
    document.body.setAttribute("translate", "no");
    document.body.classList.add("notranslate");
</script>
<style>
    /* 徹底隱藏翻譯外掛注入的黃色虛線框 */
    [class*="immersive-translate"],
    [data-immersive-translate-walked],
    font[class*="immersive-translate"],
    div[class*="immersive-translate"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        opacity: 0 !important;
    }

    /* 頂部安全距離加大，徹底解決手機與電腦端標題被遮蓋問題 */
    .block-container {
        max-width: 600px !important;
        padding-top: 3.2rem !important;
        padding-bottom: 5.5rem !important;
    }
    
    /* 專業工程儀表板標題字級 */
    .system-title {
        font-size: 19px !important;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 邊坡精緻緊湊卡片 */
    .app-card {
        background: #1e2430;
        color: #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        border: 1px solid #2d3748;
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 13.5px;
        line-height: 1.4;
    }
    .detail-label { color: #94a3b8; font-weight: 500; width: 40%; }
    .detail-value { font-weight: 600; width: 60%; text-align: right; word-break: break-all; }

    /* 分級徽章 */
    .badge {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: bold;
        color: #ffffff;
    }
    .badge-A { background-color: #ef4444; }
    .badge-B { background-color: #f97316; }
    .badge-C { background-color: #3b82f6; }
    .badge-D { background-color: #22c55e; }
    .badge-其他 { background-color: #64748b; }

    .gmap-mini-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: #2563eb;
        color: #ffffff !important;
        font-weight: bold;
        padding: 8px;
        border-radius: 6px;
        text-decoration: none;
        margin-top: 6px;
        margin-bottom: 10px;
        font-size: 13.5px;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "邊坡資料.xlsx" if os.path.exists("邊坡資料.xlsx") else "1.邊坡資料(11505).xlsx"
KMZ_FILE = "南澳段歷次災害-(更新斑點圖使用).kmz"

# 3. 讀取 Excel 資料
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_excel(DATA_FILE)
    df['起點緯度'] = pd.to_numeric(df['起點緯度'], errors='coerce')
    df['起點經度'] = pd.to_numeric(df['起點經度'], errors='coerce')
    df['定性分級'] = df['定性分級'].fillna('其他').astype(str).str.strip()
    df['定量分級'] = df['定量分級'].fillna('未施作定量評估').astype(str).str.strip()
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
            if coord_node is not None and coord_node.text:
                parts = coord_node.text.strip().split()[0].split(',')
                if len(parts) >= 2:
                    disasters.append({
                        "災害名稱": name,
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

# Session State 控制頁面狀態
if "bottom_tab" not in st.session_state:
    st.session_state.bottom_tab = "📋 邊坡清冊"
if "selected_slope_id" not in st.session_state:
    st.session_state.selected_slope_id = None

# ==============================================================================
# 需求 2 & 3：全站「返回首頁 / 主畫面」按鈕機制
# ==============================================================================
is_sub_view = (st.session_state.bottom_tab != "📋 邊坡清冊") or (st.session_state.selected_slope_id is not None)

if is_sub_view:
    col_back1, col_back2 = st.columns([3, 1])
    with col_back1:
        if st.button("⬅️ 返回邊坡清冊主畫面", key="top_back_btn", use_container_width=True, type="primary"):
            st.session_state.bottom_tab = "📋 邊坡清冊"
            st.session_state.selected_slope_id = None
            st.rerun()
    with col_back2:
        st.caption("")

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

            st.markdown(f"""
            <div class="app-card notranslate" translate="no">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:17px; font-weight:700;">📍 {row['路線']} {row['里程樁號(起)']}</span>
                    <span class="badge badge-{q_grade}">{q_grade} 級</span>
                </div>
                <div style="font-family:monospace; font-size:12px; color:#94a3b8; margin-top:3px;">{row['口卡編號']}</div>
                <div style="font-size:12px; color:#94a3b8; margin-top:2px;">最近更新：{row.get('最近更新時間', '無')}</div>
                <div style="font-size:13.5px; font-weight:600; color:#38bdf8; margin-top:4px;">構造物：{row.get('邊坡構造物', '自然邊坡')}</div>
            </div>
            """, unsafe_allow_html=True)

            # 該里程專屬 Google 衛星空照圖
            r_lat, r_lon = row.get('起點緯度'), row.get('起點經度')
            if pd.notna(r_lat) and pd.notna(r_lon):
                mini_map = folium.Map(
                    location=[r_lat, r_lon],
                    zoom_start=16,
                    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                    attr="Google Satellite"
                )
                folium.Marker(
                    location=[r_lat, r_lon],
                    tooltip=f"{row['路線']} {row['里程樁號(起)']}",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(mini_map)
                
                st_folium(mini_map, width="100%", height=220, key=f"mini_{row['口卡編號']}")

                gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={r_lat},{r_lon}"
                st.markdown(f'<a href="{gmap_url}" target="_blank" class="gmap-mini-btn notranslate" translate="no">🧭 開啟 Google Maps 路線導航 ({r_lat:.4f}, {r_lon:.4f})</a>', unsafe_allow_html=True)

            # 完整屬性資料清冊 (Details)
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
                ("定量分級", str(row.get('定量分級', '未施作定量評估'))),
                ("災害歷史", str(row.get('災害歷史', '無'))),
                ("資料建立日期", str(row.get('資料建立日期', '無'))),
                ("監測情形", str(row.get('監測情形', '無'))),
                ("監測辦理方式", str(row.get('監測辦理方式', '無'))),
                ("附近地名", str(row.get('附近地名', '無'))),
            ]

            rows_html = "".join([f'<div class="detail-row"><span class="detail-label">{k}</span><span class="detail-value">{v}</span></div>' for k, v in detail_fields])
            st.markdown(f'<div class="app-card notranslate" translate="no">{rows_html}</div>', unsafe_allow_html=True)

            st.markdown("**現地狀況描述：**")
            desc_val = str(row.get('現地狀況描述', '無描述紀錄'))
            st.markdown(f"""
            <div class="app-card notranslate" translate="no" style="background:rgba(59, 130, 246, 0.08); border-left:3px solid #3b82f6; line-height:1.5; font-size:13.5px;">
                {desc_val}
            </div>
            """, unsafe_allow_html=True)

            # 構造物巡查與多照片上傳 Form
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
                up_photos = st.file_uploader(f"選取照片 (支援一次多張)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
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
                    combined_desc = f"{new_entry}\n{old_desc}".strip() if new_entry else old_desc

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
        # 需求 1：精簡專業的標題比例
        st.markdown('<div class="system-title">🛣️ 南澳工務段 邊坡清冊</div>', unsafe_allow_html=True)

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

        st.caption(f"符合條件邊坡：**{len(f_df)}** 處（總資產：{len(df)} 處）")

        # 需求 4：單一頁面頂多呈現 10 筆，其餘用開關展開或滾動
        for r_name in f_df['路線'].dropna().unique():
            sub_df = f_df[f_df['路線'] == r_name]
            total_sub = len(sub_df)
            
            with st.expander(f"🛣️ **{r_name}**（共 {total_sub} 處）", expanded=True):
                # 超過 10 筆時提供展示控制
                show_all = False
                if total_sub > 10:
                    show_all = st.checkbox(f"展開全部 {total_sub} 筆（預設僅顯示前 10 筆）", key=f"chk_{r_name}")
                
                display_df = sub_df if show_all else sub_df.head(10)

                for _, r in display_df.iterrows():
                    grade = str(r['定性分級'])
                    with st.container(border=True):
                        # 點擊直接進詳細頁面
                        btn_label = f"📍 {r['里程樁號(起)']}  [{grade}級]"
                        if st.button(btn_label, key=f"pick_{r['口卡編號']}", use_container_width=True):
                            st.session_state.selected_slope_id = r['口卡編號']
                            st.rerun()

                        # 需求 5：刪除下方「導航」文字，保持版面極簡
                        st.caption(f"卡號：`{r['口卡編號']}` ｜ 構造：`{r.get('邊坡構造物', '自然邊坡')[:14]}`")

# ==============================================================================
# 頁面 2：邊坡統計（圓餅圖）
# ==============================================================================
elif st.session_state.bottom_tab == "📊 邊坡統計(圓餅圖)":
    st.markdown('<div class="system-title">📊 邊坡分級統計分析</div>', unsafe_allow_html=True)
    
    cats = ["A", "B", "C", "D", "其他"]
    c_counts = df['定性分級'].value_counts()
    qual_df = pd.DataFrame({
        "分級": cats,
        "數量": [c_counts.get(c, 0) for c in cats]
    })
    
    st.write("##### 定性分級數量佔比 (圓餅圖)")
    fig_pie1 = px.pie(
        qual_df, values='數量', names='分級', hole=0.45,
        color='分級',
        color_discrete_map={'A': '#ef4444', 'B': '#f97316', 'C': '#3b82f6', 'D': '#22c55e', '其他': '#64748b'},
    )
    fig_pie1.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_pie1.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=290)
    st.plotly_chart(fig_pie1, use_container_width=True)

    st.write("##### 定量分級數量佔比 (圓餅圖)")
    quant_counts = df['定量分級'].value_counts().reset_index()
    quant_counts.columns = ['定量分級', '數量']
    fig_pie2 = px.pie(
        quant_counts, values='數量', names='定量分級', hole=0.45,
        color='定量分級'
    )
    fig_pie2.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_pie2.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=290)
    st.plotly_chart(fig_pie2, use_container_width=True)

# ==============================================================================
# 頁面 3：地圖定位 (Google Earth 衛星空照底圖)
# ==============================================================================
elif st.session_state.bottom_tab == "🗺️ 地圖定位":
    st.markdown('<div class="system-title">🗺️ 邊坡空間地圖定位</div>', unsafe_allow_html=True)
    valid_pts = df.dropna(subset=['起點緯度', '起點經度'])
    
    if not valid_pts.empty:
        c_lat = valid_pts['起點緯度'].median()
        c_lon = valid_pts['起點經度'].median()
        m_loc = folium.Map(location=[c_lat, c_lon], zoom_start=11, tiles=None)

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

        cmap = {'A': '#ef4444', 'B': '#f97316', 'C': '#3b82f6', 'D': '#22c55e', '其他': '#64748b'}
        for _, r in valid_pts.iterrows():
            g = str(r['定性分級'])
            color = cmap.get(g, '#64748b')
            p_lat, p_lon = r['起點緯度'], r['起點經度']
            g_url = f"https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}"
            popup_html = f"""
            <div translate="no" class="notranslate" style="font-family:sans-serif; font-size:13px; line-height:1.4;">
                <b style="font-size:14px;">{r['路線']} {r['里程樁號(起)']}</b><br/>
                <b>卡號：</b>{r['口卡編號']}<br/>
                <b>定性分級：</b><span style="color:{color}; font-weight:bold;">{g} 級</span><br/>
                <b>構造物：</b>{r.get('邊坡構造物', '自然邊坡')}<br/>
                <a href="{g_url}" target="_blank" style="display:inline-block; margin-top:5px; padding:4px 8px; background:#2563eb; color:white; border-radius:4px; text-decoration:none; font-weight:bold;">🧭 Google Map 導航</a>
            </div>
            """
            folium.CircleMarker(
                location=[p_lat, p_lon],
                radius=6,
                popup=folium.Popup(popup_html, max_width=260),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85
            ).add_to(m_loc)

        folium.LayerControl(position="topright", collapsed=False).add_to(m_loc)
        st_folium(m_loc, width="100%", height=480)

# ==============================================================================
# 頁面 4：災害斑點圖 (KMZ 171 處)
# ==============================================================================
elif st.session_state.bottom_tab == "🔥 災害斑點圖":
    st.markdown(f'<div class="system-title">🔥 歷次災害斑點專題圖（{len(df_disasters)} 處）</div>', unsafe_allow_html=True)
    if not df_disasters.empty:
        c_lat = df_disasters['緯度'].median()
        c_lon = df_disasters['經度'].median()
        m_dis = folium.Map(location=[c_lat, c_lon], zoom_start=11, tiles=None)

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

        for _, d in df_disasters.iterrows():
            d_lat, d_lon = d['緯度'], d['經度']
            d_gurl = f"https://www.google.com/maps/dir/?api=1&destination={d_lat},{d_lon}"
            d_popup = f"""
            <div translate="no" class="notranslate" style="font-family:sans-serif; font-size:13px; line-height:1.4;">
                <span style="background:#ef4444; color:white; padding:2px 5px; border-radius:3px; font-size:11px; font-weight:bold;">歷次災害斑點</span><br/>
                <b style="color:#b91c1c; font-size:13px; margin-top:4px; display:inline-block;">{d['災害名稱']}</b><br/>
                {d['詳細說明']}<br/>
                <a href="{d_gurl}" target="_blank" style="display:inline-block; margin-top:5px; padding:3px 7px; background:#b91c1c; color:white; border-radius:4px; text-decoration:none; font-size:12px;">🧭 導航至災點</a>
            </div>
            """
            folium.CircleMarker(
                location=[d_lat, d_lon],
                radius=5,
                popup=folium.Popup(d_popup, max_width=260),
                color="#7f1d1d",
                fill=True,
                fill_color="#f87171",
                fill_opacity=0.9
            ).add_to(m_dis)

        folium.LayerControl(position="topright", collapsed=False).add_to(m_dis)
        st_folium(m_dis, width="100%", height=480)

# ==============================================================================
# 5. 底部常駐功能導航列 (Fixed Bottom Navigation)
# ==============================================================================
st.markdown("""<div style="height: 50px;"></div>""", unsafe_allow_html=True)

nav_cols = st.columns(4)
with nav_cols[0]:
    if st.button("📋 邊坡清冊", use_container_width=True, type="primary" if st.session_state.bottom_tab == "📋 邊坡清冊" else "secondary"):
        st.session_state.bottom_tab = "📋 邊坡清冊"
        st.rerun()

with nav_cols[1]:
    if st.button("📊 統計圓餅圖", use_container_width=True, type="primary" if st.session_state.bottom_tab == "📊 邊坡統計(圓餅圖)" else "secondary"):
        st.session_state.bottom_tab = "📊 邊坡統計(圓餅圖)"
        st.session_state.selected_slope_id = None
        st.rerun()

with nav_cols[2]:
    if st.button("🗺️ 地圖定位", use_container_width=True, type="primary" if st.session_state.bottom_tab == "🗺️ 地圖定位" else "secondary"):
        st.session_state.bottom_tab = "🗺️ 地圖定位"
        st.session_state.selected_slope_id = None
        st.rerun()

with nav_cols[3]:
    if st.button("🔥 災害斑點圖", use_container_width=True, type="primary" if st.session_state.bottom_tab == "🔥 災害斑點圖" else "secondary"):
        st.session_state.bottom_tab = "🔥 災害斑點圖"
        st.session_state.selected_slope_id = None
        st.rerun()