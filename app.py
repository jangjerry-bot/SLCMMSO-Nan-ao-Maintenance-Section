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

# 1. 頁面設定 (手機優先)
st.set_page_config(
    page_title="南澳段邊坡生命週期",
    page_icon="⛰️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 注入精緻 CSS (防外掛翻譯 + 手機排版)
st.markdown("""
<script>
    document.documentElement.setAttribute("translate", "no");
    document.documentElement.classList.add("notranslate");
    document.body.setAttribute("translate", "no");
    document.body.classList.add("notranslate");
</script>
<style>
    [class*="immersive-translate"],
    [data-immersive-translate-walked],
    font[class*="immersive-translate"],
    div[class*="immersive-translate"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
    }
    .block-container {
        max-width: 620px !important;
        padding-top: 0.6rem !important;
        padding-bottom: 5.5rem !important;
    }
    #MainMenu, footer { visibility: hidden; }
    .app-card {
        background: #ffffff;
        color: #2c3e50;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #eef2f5;
    }
    @media (prefers-color-scheme: dark) {
        .app-card {
            background: #1e2430;
            color: #e2e8f0;
            border: 1px solid #2d3748;
        }
    }
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(150, 150, 150, 0.15);
        font-size: 14px;
        line-height: 1.4;
    }
    .detail-label { color: #64748b; font-weight: 500; width: 38%; }
    .detail-value { font-weight: 600; width: 62%; text-align: right; word-break: break-all; }
    .badge {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        color: #ffffff;
    }
    .badge-A { background-color: #e53e3e; }
    .badge-B { background-color: #dd6b20; }
    .badge-C { background-color: #3182ce; }
    .badge-D { background-color: #38a169; }
    .badge-其他 { background-color: #718096; }
    .gmap-mini-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: #1a73e8;
        color: #ffffff !important;
        font-weight: bold;
        padding: 9px;
        border-radius: 6px;
        text-decoration: none;
        margin-top: 6px;
        margin-bottom: 12px;
        font-size: 14px;
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

if "bottom_tab" not in st.session_state:
    st.session_state.bottom_tab = "📋 邊坡清冊"
if "selected_slope_id" not in st.session_state:
    st.session_state.selected_slope_id = None

# ==============================================================================
# 功能 1：邊坡清冊與詳細資料 (含構造物分別巡查 + 多圖上傳)
# ==============================================================================
if st.session_state.bottom_tab == "📋 邊坡清冊":
    if st.session_state.selected_slope_id is not None:
        matched = df[df['口卡編號'] == st.session_state.selected_slope_id]
        if not matched.empty:
            row = matched.iloc[0]
            q_grade = str(row['定性分級'])

            if st.button("⬅️ 返回邊坡清冊列表", use_container_width=True):
                st.session_state.selected_slope_id = None
                st.rerun()

            st.markdown(f"""
            <div class="app-card notranslate" translate="no">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; font-size:20px;">📍 {row['路線']} {row['里程樁號(起)']}</h3>
                    <span class="badge badge-{q_grade}">{q_grade} 級</span>
                </div>
                <div style="font-family:monospace; font-size:12px; color:#888; margin-top:4px;">{row['口卡編號']}</div>
                <div style="font-size:12px; color:#888; margin-top:2px;">最近更新：{row.get('最近更新時間', '無')}</div>
                <div style="font-size:14px; font-weight:600; color:#3b82f6; margin-top:6px;">構造物：{row.get('邊坡構造物', '自然邊坡')}</div>
            </div>
            """, unsafe_allow_html=True)

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
                
                st_folium(mini_map, width="100%", height=240, key=f"mini_{row['口卡編號']}")

                gmap_url = f"https://www.google.com/maps/dir/?api=1&destination={r_lat},{r_lon}"
                st.markdown(f'<a href="{gmap_url}" target="_blank" class="gmap-mini-btn notranslate" translate="no">🧭 開啟 Google Maps 路線導航 ({r_lat:.4f}, {r_lon:.4f})</a>', unsafe_allow_html=True)

            st.markdown("#### 📋 邊坡完整屬性資料 (Details)")
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
            <div class="app-card notranslate" translate="no" style="background:rgba(66, 133, 244, 0.08); border-left:4px solid #4285F4; line-height:1.6;">
                {desc_val}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📝 構造物分項巡查與照片上傳 (Form)")
            raw_structs = str(row.get('邊坡構造物', '自然邊坡'))
            split_structs = [s.strip() for s in re.split(r'[,、]', raw_structs) if s.strip()]
            if not split_structs:
                split_structs = ["自然邊坡"]
            split_structs.append("＋ 整體邊坡現況")

            with st.form("inspect_form"):
                st.write("##### 1. 選擇欲維護之構造物")
                selected_struct = st.selectbox("構造物項目", split_structs)

                col_stat, col_qual = st.columns(2)
                with col_stat:
                    new_status = st.selectbox("邊坡管理狀態", ["鎖定管理中", "解除列管", "重點列管"])
                with col_qual:
                    new_qual = st.selectbox("定性分級調整", ["A", "B", "C", "D", "其他"], index=["A","B","C","D","其他"].index(q_grade) if q_grade in ["A","B","C","D","其他"] else 4)

                struct_desc = st.text_area(
                    f"【{selected_struct}】現地狀況與維護描述",
                    placeholder=f"請輸入針對【{selected_struct}】之現況描述..."
                )

                st.write("##### 2. 現地照片採集（支援一次選取多張相片）")
                up_photos = st.file_uploader(
                    f"選取【{selected_struct}】照片 (可一次選取多張)",
                    type=["jpg", "png", "jpeg"],
                    accept_multiple_files=True
                )
                cam_photo = st.camera_input("開啟相機即時拍照")

                if st.form_submit_button("💾 儲存並寫入 Excel 資料庫", type="primary", use_container_width=True):
                    os.makedirs("inspection_photos", exist_ok=True)
                    t_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    saved_count = 0
                    if up_photos:
                        for idx, p_file in enumerate(up_photos):
                            clean_struct = selected_struct.replace(":", "_").replace("/", "_")
                            img_name = f"inspection_photos/{row['口卡編號']}_{clean_struct}_{t_now}_{idx+1}.jpg"
                            Image.open(p_file).save(img_name)
                            saved_count += 1
                    if cam_photo:
                        clean_struct = selected_struct.replace(":", "_").replace("/", "_")
                        cam_name = f"inspection_photos/{row['口卡編號']}_{clean_struct}_{t_now}_cam.jpg"
                        Image.open(cam_photo).save(cam_name)
                        saved_count += 1

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
                    st.success(f"成功更新【{selected_struct}】！共儲存 {saved_count} 張照片。")
                    st.rerun()
    else:
        st.markdown("### 🛣️ 南澳段邊坡生命週期清冊")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            route_list = ["全部路線"] + list(df['路線'].dropna().unique())
            route_filter = st.selectbox("路線選擇", route_list)
        with col_f2:
            qual_list = ["全部分級", "A", "B", "C", "D", "其他"]
            qual_filter = st.selectbox("定性分級篩選", qual_list)

        search_kw = st.text_input("搜尋 (里程 / 卡號 / 地名)", placeholder="例如: 8k+600、隘丁")

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

        st.caption(f"符合條件：**{len(f_df)}** 處邊坡（總資料量：{len(df)} 處）")
        st.markdown("👉 **點擊任一里程按鈕，直接查看邊坡詳細與空照圖：**")

        for r_name in f_df['路線'].dropna().unique():
            sub_df = f_df[f_df['路線'] == r_name]
            with st.expander(f"🛣️ **{r_name}**（{len(sub_df)} 處）", expanded=True):
                for _, r in sub_df.iterrows():
                    grade = str(r['定性分級'])
                    lat_i, lon_i = r.get('起點緯度'), r.get('起點經度')
                    nav_link = f"https://www.google.com/maps/dir/?api=1&destination={lat_i},{lon_i}" if pd.notna(lat_i) and pd.notna(lon_i) else "#"
                    
                    with st.container(border=True):
                        btn_label = f"📍 {r['里程樁號(起)']}  [{grade}級]"
                        if st.button(btn_label, key=f"btn_pick_{r['口卡編號']}", use_container_width=True):
                            st.session_state.selected_slope_id = r['口卡編號']
                            st.rerun()

                        col_c1, col_c2 = st.columns([3, 1])
                        with col_c1:
                            st.caption(f"口卡：`{r['口卡編號']}` ｜ 構造物：`{r.get('邊坡構造物', '自然邊坡')}`")
                        with col_c2:
                            if pd.notna(lat_i) and pd.notna(lon_i):
                                st.markdown(f'<a href="{nav_link}" target="_blank" style="font-size:13px; color:#1a73e8; font-weight:bold; text-decoration:none;">🧭 導航</a>', unsafe_allow_html=True)

# ==============================================================================
# 功能 2：邊坡資料邊坡統計（圓餅圖）
# ==============================================================================
elif st.session_state.bottom_tab == "📊 邊坡統計(圓餅圖)":
    st.markdown("### 📊 邊坡分級數量統計與圓餅圖分析")
    cats = ["A", "B", "C", "D", "其他"]
    c_counts = df['定性分級'].value_counts()
    qual_df = pd.DataFrame({
        "分級": cats,
        "數量": [c_counts.get(c, 0) for c in cats]
    })
    st.write("#### 1. 定性分級數量佔比 (圓餅圖)")
    fig_pie1 = px.pie(
        qual_df, values='數量', names='分級', hole=0.4,
        color='分級',
        color_discrete_map={'A': '#e53e3e', 'B': '#dd6b20', 'C': '#3182ce', 'D': '#38a169', '其他': '#718096'},
        title="定性分級佔比 (A, B, C, D, 其他)"
    )
    fig_pie1.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_pie1.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=320)
    st.plotly_chart(fig_pie1, use_container_width=True)

    fig_bar1 = px.bar(
        qual_df, x="數量", y="分級", orientation="h",
        color="分級",
        color_discrete_map={'A': '#e53e3e', 'B': '#dd6b20', 'C': '#3182ce', 'D': '#38a169', '其他': '#718096'},
        text="數量"
    )
    fig_bar1.update_layout(yaxis=dict(autorange="reversed"), height=240, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_bar1, use_container_width=True)

    st.markdown("---")
    st.write("#### 2. 定量分級數量佔比 (圓餅圖)")
    quant_counts = df['定量分級'].value_counts().reset_index()
    quant_counts.columns = ['定量分級', '數量']
    fig_pie2 = px.pie(
        quant_counts, values='數量', names='定量分級', hole=0.4,
        color='定量分級',
        title="定量分級數量與佔比"
    )
    fig_pie2.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_pie2.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=320)
    st.plotly_chart(fig_pie2, use_container_width=True)

# ==============================================================================
# 功能 3：地圖定位 (Google Earth 衛星底圖)
# ==============================================================================
elif st.session_state.bottom_tab == "🗺️ 地圖定位":
    st.markdown("### 🗺️ 南澳段邊坡空間地圖定位")
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

        cmap = {'A': '#e53e3e', 'B': '#dd6b20', 'C': '#3182ce', 'D': '#38a169', '其他': '#718096'}
        for _, r in valid_pts.iterrows():
            g = str(r['定性分級'])
            color = cmap.get(g, '#718096')
            p_lat, p_lon = r['起點緯度'], r['起點經度']
            g_url = f"https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}"
            popup_html = f"""
            <div translate="no" class="notranslate" style="font-family:sans-serif; font-size:13px; line-height:1.4;">
                <b style="font-size:14px;">{r['路線']} {r['里程樁號(起)']}</b><br/>
                <b>卡號：</b>{r['口卡編號']}<br/>
                <b>定性分級：</b><span style="color:{color}; font-weight:bold;">{g} 級</span><br/>
                <b>構造物：</b>{r.get('邊坡構造物', '自然邊坡')}<br/>
                <a href="{g_url}" target="_blank" style="display:inline-block; margin-top:5px; padding:4px 8px; background:#1a73e8; color:white; border-radius:4px; text-decoration:none; font-weight:bold;">🧭 Google Map 導航</a>
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
        st_folium(m_loc, width="100%", height=500)
    else:
        st.warning("查無經緯度定位資料。")

# ==============================================================================
# 功能 4：災害斑點圖 (KMZ 171 處)
# ==============================================================================
elif st.session_state.bottom_tab == "🔥 災害斑點圖":
    st.markdown(f"### 🔥 南澳段歷次災害斑點專題圖（共 {len(df_disasters)} 處）")
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
                <span style="background:#e53e3e; color:white; padding:2px 5px; border-radius:3px; font-size:11px; font-weight:bold;">歷次災害斑點</span><br/>
                <b style="color:#c53030; font-size:13px; margin-top:4px; display:inline-block;">{d['災害名稱']}</b><br/>
                {d['詳細說明']}<br/>
                <a href="{d_gurl}" target="_blank" style="display:inline-block; margin-top:5px; padding:3px 7px; background:#c53030; color:white; border-radius:4px; text-decoration:none; font-size:12px;">🧭 導航至災點</a>
            </div>
            """
            folium.CircleMarker(
                location=[d_lat, d_lon],
                radius=5,
                popup=folium.Popup(d_popup, max_width=260),
                color="#9b2c2c",
                fill=True,
                fill_color="#ff4d4d",
                fill_opacity=0.9
            ).add_to(m_dis)

        folium.LayerControl(position="topright", collapsed=False).add_to(m_dis)
        st_folium(m_dis, width="100%", height=500)
    else:
        st.warning("查無 KMZ 災害斑點資料。")

# ==============================================================================
# 5. 底部常駐功能導航列 (Fixed Bottom Navigation)
# ==============================================================================
st.markdown("""<div style="height: 60px;"></div>""", unsafe_allow_html=True)

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