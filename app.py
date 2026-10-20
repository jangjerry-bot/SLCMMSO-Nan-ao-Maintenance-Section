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
import io
import xml.etree.ElementTree as ET
import re
import base64
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# 釋放超大圖檔像素限制，後續透過強制縮圖控制記憶體
Image.MAX_IMAGE_PIXELS = None

os.makedirs(".streamlit", exist_ok=True)
config_path = os.path.join(".streamlit", "config.toml")
config_content = """[theme]
base = "light"
primaryColor = "#f97316"
backgroundColor = "#f1f5f9"
secondaryBackgroundColor = "#ffffff"
textColor = "#0f172a"
"""
if not os.path.exists(config_path) or open(config_path, "r", encoding="utf-8").read() != config_content:
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

import importlib
import style
import inspection_schema
importlib.reload(style)
importlib.reload(inspection_schema)
from style import get_theme_css, render_footer, render_top_logo
from inspection_schema import INSPECTION_TEMPLATES, match_template, generate_doc_report

st.set_page_config(page_title="南澳邊坡防災圖台", page_icon="⛰️", layout="wide", initial_sidebar_state="collapsed")

# ===== 確保所有狀態變數皆已初始化，避免 KeyError 崩潰 =====
if "theme_mode" not in st.session_state: st.session_state.theme_mode = "☀️ 淺色"
if "bottom_tab" not in st.session_state: st.session_state.bottom_tab = "📋 邊坡清冊"
if "selected_slope_id" not in st.session_state: st.session_state.selected_slope_id = None
if "active_grade_detail" not in st.session_state: st.session_state.active_grade_detail = None
if "patrol_draft" not in st.session_state: st.session_state.patrol_draft = {}
if "priority_mode" not in st.session_state: st.session_state.priority_mode = False
if "last_clicked_coords" not in st.session_state: st.session_state.last_clicked_coords = "經緯度：121.80200 24.46500"

is_light = ("淺色" in st.session_state.theme_mode)
plotly_font_color = "#0f172a" if is_light else "#f8fafc"

if "splash_shown" not in st.session_state:
    st.markdown(get_theme_css(is_light, show_splash=True), unsafe_allow_html=True)
    st.session_state.splash_shown = True
else:
    st.markdown(get_theme_css(is_light, show_splash=False), unsafe_allow_html=True)

header_titles = {
    "📋 邊坡清冊": "南澳邊坡清冊快搜",
    "📊 定量定性": "邊坡分級統計情報",
    "🗺️ 地圖定位": "邊坡防災圖台",
    "🔥 災害斑點圖": "災害與敏感區圖台",
    "📝 養護巡查": "外業養護巡查表單"
}
st.markdown(render_top_logo(header_titles.get(st.session_state.bottom_tab, "南澳邊坡防災圖台")), unsafe_allow_html=True)

# 底部導航列 CSS 定位錨點
st.markdown('<div id="bottom-nav-anchor"></div>', unsafe_allow_html=True)
tabs_meta = [
    ("📋 邊坡清冊", "🏠\n首頁清冊"),
    ("🗺️ 地圖定位", "🗺️\n邊坡地圖"),
    ("🔥 災害斑點", "⚠️\n災害疊圖"),
    ("📊 定量定性", "📊\n分級情報"),
    ("📝 養護巡查", "📝\n巡查填報")
]
nav_cols = st.columns(5)
for i, (tab_key, tab_label) in enumerate(tabs_meta):
    with nav_cols[i]:
        is_cur = (st.session_state.bottom_tab == tab_key or (tab_key == "🔥 災害斑點" and st.session_state.bottom_tab == "🔥 災害斑點圖"))
        if st.button(tab_label, key=f"nav_btn_{i+1}", use_container_width=True, type="primary" if is_cur else "secondary"):
            st.session_state.bottom_tab = "🔥 災害斑點圖" if tab_key == "🔥 災害斑點" else tab_key
            if tab_key != "📋 邊坡清冊":
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
    df['定性分級'] = df['定性分級'].fillna('其他').astype(str).str.strip().str.upper()
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

def find_spatial_overlay_files():
    geo_files = []
    debris_files = []
    for root_dir, _, files in os.walk('.'):
        if '.git' in root_dir or '__pycache__' in root_dir:
            continue
        for f in sorted(files):
            fl = f.lower()
            full_p = os.path.join(root_dir, f) if root_dir != '.' else f
            if (fl.endswith('.kmz') or fl.endswith('.kml')) and f != KMZ_FILE and '歷次災害' not in f:
                if any(k in fl for k in ['土石流', '溪流', '1753', 'debris', 'df']):
                    debris_files.append(full_p)
                elif any(k in fl for k in ['敏感', '地質', 'gsb', 'geo', 'sensitive', 'part']):
                    geo_files.append(full_p)
                else:
                    # 若有其他未知命名的 KMZ，若非敏感區則歸入土石流備用
                    if geo_files and not debris_files:
                        debris_files.append(full_p)
                    else:
                        geo_files.append(full_p)
    return geo_files, debris_files

@st.cache_data
def load_kmz_overlay(file_list, remove_white_bg=False, clip_to_nanao=False):
    overlays = []
    polygons = []
    if not file_list:
        return overlays, polygons

    def strip_tag(tag):
        return tag.split('}')[-1] if '}' in tag else tag

    def find_child_text(elem, target_tag):
        for child in elem.iter():
            if strip_tag(child.tag) == target_tag and child.text:
                return child.text.strip()
        return None

    for file_path in file_list:
        if not os.path.exists(file_path):
            continue
        try:
            namelist = []
            z = None
            kml_roots = []
            if file_path.lower().endswith('.kmz'):
                z = zipfile.ZipFile(file_path, 'r')
                namelist = z.namelist()
                kmls = [f for f in namelist if f.lower().endswith('.kml')]
                for k in kmls:
                    try:
                        kml_roots.append(ET.fromstring(z.read(k)))
                    except Exception:
                        pass
            else:
                kml_roots.append(ET.parse(file_path).getroot())

            for root in kml_roots:
                # 1. 解析 GroundOverlay 柵格影像
                for elem in root.iter():
                    if strip_tag(elem.tag) == 'GroundOverlay':
                        ov_name = find_child_text(elem, 'name') or f"空間圖層 ({os.path.basename(file_path)})"
                        href = find_child_text(elem, 'href')
                        north = find_child_text(elem, 'north')
                        south = find_child_text(elem, 'south')
                        east = find_child_text(elem, 'east')
                        west = find_child_text(elem, 'west')

                        if not (north and south and east and west):
                            quad_coords = None
                            for sub in elem.iter():
                                if strip_tag(sub.tag) == 'LatLonQuad':
                                    quad_coords = find_child_text(sub, 'coordinates')
                                    break
                            if quad_coords:
                                lats, lons = [], []
                                for pt in quad_coords.split():
                                    parts = pt.split(',')
                                    if len(parts) >= 2:
                                        lons.append(float(parts[0]))
                                        lats.append(float(parts[1]))
                                if lats and lons:
                                    north, south = max(lats), min(lats)
                                    east, west = max(lons), min(lons)

                        if href and north and south and east and west:
                            href_clean = href.replace('\\', '/')
                            raw_img_bytes = None
                            if z is not None:
                                matched_img = None
                                if href_clean in namelist:
                                    matched_img = href_clean
                                else:
                                    base_href = os.path.basename(href_clean)
                                    for name_in_zip in namelist:
                                        if os.path.basename(name_in_zip) == base_href:
                                            matched_img = name_in_zip
                                            break
                                if matched_img:
                                    raw_img_bytes = z.read(matched_img)
                            else:
                                dir_base = os.path.dirname(file_path)
                                cand_path = os.path.join(dir_base, href_clean)
                                if os.path.exists(cand_path):
                                    raw_img_bytes = open(cand_path, "rb").read()
                                elif os.path.exists(href_clean):
                                    raw_img_bytes = open(href_clean, "rb").read()

                            if raw_img_bytes:
                                img = Image.open(io.BytesIO(raw_img_bytes)).convert("RGBA")
                                img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)

                                if remove_white_bg:
                                    arr = np.array(img)
                                    white_mask = (arr[:, :, 0] > 235) & (arr[:, :, 1] > 235) & (arr[:, :, 2] > 235)
                                    arr[white_mask, 3] = 0
                                    img = Image.fromarray(arr)
                                    del arr, white_mask

                                buf = io.BytesIO()
                                img.save(buf, format="PNG", optimize=False)
                                b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
                                overlays.append({
                                    "name": ov_name,
                                    "image_uri": f"data:image/png;base64,{b64_str}",
                                    "bounds": [[float(south), float(west)], [float(north), float(east)]]
                                })
                                del img, buf, raw_img_bytes

                # 2. 解析向量 Placemark (支援 Polygon / LineString / MultiGeometry 與南澳轄區空間裁切)
                for elem in root.iter():
                    if strip_tag(elem.tag) == 'Placemark':
                        pm_name = find_child_text(elem, 'name') or "圖資範圍"
                        pm_desc = find_child_text(elem, 'description') or ""
                        # 擷取 SimpleData 屬性作為補充說明（公部門土石流 KML 常將溪流編號放於 SimpleData）
                        if not pm_desc:
                            s_data = []
                            for sd in elem.iter():
                                if strip_tag(sd.tag) in ['SimpleData', 'Data'] and sd.text:
                                    k_attr = sd.attrib.get('name', '')
                                    if k_attr:
                                        s_data.append(f"{k_attr}: {sd.text.strip()}")
                            if s_data:
                                pm_desc = "<br>".join(s_data[:8])

                        for sub in elem.iter():
                            st_tag = strip_tag(sub.tag)
                            if st_tag in ['Polygon', 'LineString']:
                                coord_text = find_child_text(sub, 'coordinates')
                                if coord_text:
                                    pts = []
                                    for token in re.split(r'\s+', coord_text.strip()):
                                        if not token:
                                            continue
                                        c_parts = token.split(',')
                                        if len(c_parts) >= 2:
                                            try:
                                                lon_v, lat_v = float(c_parts[0]), float(c_parts[1])
                                                pts.append([lat_v, lon_v])
                                            except ValueError:
                                                pass
                                    if len(pts) >= 2:
                                        if clip_to_nanao:
                                            lat0, lon0 = pts[0][0], pts[0][1]
                                            # 僅保留宜蘭、南澳、蘇花廊道周邊範圍 (緯度 24.0~24.9, 經度 121.3~122.1)，大幅提升效能
                                            if not (24.0 <= lat0 <= 24.9 and 121.3 <= lon0 <= 122.1):
                                                continue
                                        polygons.append({
                                            "name": pm_name,
                                            "desc": pm_desc,
                                            "type": st_tag,
                                            "locations": pts
                                        })
            if z is not None:
                z.close()
        except Exception as e:
            st.error(f"解析圖資 ({file_path}) 時發生異常: {e}")

    return overlays, polygons

def add_spatial_layer_to_map(folium_map, overlays, polygons, layer_name="空間圖層", color_hex="#d97706", opacity=0.70, show_default=True):
    if not overlays and not polygons:
        return
    fg = folium.FeatureGroup(name=layer_name, show=show_default)
    for ov in overlays:
        folium.raster_layers.ImageOverlay(
            image=ov["image_uri"],
            bounds=ov["bounds"],
            opacity=opacity,
            interactive=True,
            cross_origin=False,
            zindex=2
        ).add_to(fg)

    for poly in polygons:
        popup_txt = f"<b>{poly['name']}</b><br>{poly['desc']}"
        if poly["type"] == "Polygon":
            folium.Polygon(
                locations=poly["locations"],
                color=color_hex,
                weight=2.5,
                fill=True,
                fill_color=color_hex,
                fill_opacity=opacity * 0.5,
                popup=folium.Popup(popup_txt, max_width=320)
            ).add_to(fg)
        else:
            folium.PolyLine(
                locations=poly["locations"],
                color=color_hex,
                weight=3.5,
                opacity=opacity,
                popup=folium.Popup(popup_txt, max_width=320)
            ).add_to(fg)
    fg.add_to(folium_map)

@st.cache_data
def load_mileages():
    target_file = "省道里程坐標(里程牌標誌).csv"
    if os.path.exists(target_file):
        try:
            df_csv = pd.read_csv(target_file, encoding='big5hkscs')
            df_m = pd.DataFrame()
            df_m['Route'] = df_csv['公路編號'].astype(str) + '線'
            df_m['lat'] = df_csv['坐標-N-WGS84']
            df_m['lon'] = df_csv['坐標-E-WGS84']
            df_m['名稱'] = df_m['Route'] + ' ' + df_csv['起點樁號'].astype(str)
            
            def parse_m(val):
                if pd.isna(val): return None
                m = re.match(r'(\d+)[Kk]\+?(\d+)?', str(val).strip())
                if m:
                    km = int(m.group(1))
                    meters = int(m.group(2)) if m.group(2) else 0
                    return km * 1000 + meters
                return None
                
            df_m['Meters'] = df_csv['起點樁號'].apply(parse_m)
            df_m = df_m.dropna(subset=['Route', 'Meters', 'lat', 'lon']).reset_index(drop=True)
            return df_m, False, target_file
        except Exception as e:
            st.error(f"解析里程 CSV 檔案失敗: {e}")
            pass
            
    return pd.DataFrame(), False, target_file

df = load_data()
df_disasters = load_kmz()
df_mileages, is_network_link, found_mileage_file = load_mileages()
geo_files, debris_files = find_spatial_overlay_files()

if df.empty:
    st.error(f"找不到邊坡資料檔案：{DATA_FILE}")
    st.stop()

def get_decimal_from_dms(dms, ref):
    try:
        dec = float(dms[0]) + float(dms[1])/60.0 + float(dms[2])/3600.0
        return -dec if ref in ['S', 'W'] else dec
    except: return None

def extract_gps(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif = image._getexif()
        if not exif: return None, None
        geotags = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo' and idx in exif:
                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]: geotags[val] = exif[idx][key]
                break
        if 'GPSLatitude' in geotags and 'GPSLongitude' in geotags:
            lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags.get('GPSLatitudeRef', 'N'))
            lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags.get('GPSLongitudeRef', 'E'))
            return lat, lon
    except Exception:
        pass
    return None, None

def get_interpolated_mileage(lat, lon, df_m):
    if df_m.empty or 'Route' not in df_m.columns: return "計算失敗", 0
    lat1, lon1 = np.radians(lat), np.radians(lon)
    lat2, lon2 = np.radians(df_m['lat']), np.radians(df_m['lon'])
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2)**2
    distances = 2 * np.arcsin(np.sqrt(a)) * 6371000
    
    A = df_m.loc[distances.idxmin()]
    route_A = A['Route']
    if not route_A: return A['名稱'], distances.min()

    df_r = df_m[df_m['Route'] == route_A].copy()
    df_r['dist'] = distances[df_r.index]
    df_r = df_r.sort_values('dist')
    
    if len(df_r) < 2: return A['名稱'], distances.min()
    B = df_r.iloc[1]

    dx_AB, dy_AB = B['lon'] - A['lon'], B['lat'] - A['lat']
    dx_AC, dy_AC = lon - A['lon'], lat - A['lat']
    len2 = dx_AB**2 + dy_AB**2
    if len2 == 0: return A['名稱'], distances.min()
    
    t = max(-1.0, min(1.0, (dx_AC * dx_AB + dy_AC * dy_AB) / len2))
    im = A['Meters'] + t * (B['Meters'] - A['Meters'])
    return f"{route_A} {int(im//1000)}k+{int(im%1000):03d}", distances.min()

def create_photos_zip(photos, prefix_name):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, photo_data in enumerate(photos):
            p_bytes = photo_data[0] if isinstance(photo_data, tuple) else photo_data
            zip_file.writestr(f"{prefix_name}-{i+1}.jpg", p_bytes)
    return zip_buffer.getvalue()

# ==============================================================================
# 頁面 1：邊坡清冊
# ==============================================================================
if st.session_state.bottom_tab == "📋 邊坡清冊":
    if st.session_state.selected_slope_id is not None:
        act_top1, act_top2 = st.columns([1, 1.3])
        with act_top1:
            if st.button("⬅️ 返回邊坡清冊", key="detail_back_btn", use_container_width=True, type="secondary"):
                st.session_state.selected_slope_id = None
                st.rerun()
        with act_top2:
            if st.button("📝 填寫此邊坡「養護巡查表」", key="top_go_patrol_btn", type="primary", use_container_width=True):
                st.session_state.bottom_tab = "📝 養護巡查"
                st.session_state.target_slope_for_patrol = st.session_state.selected_slope_id
                st.rerun()

        matched = df[df['口卡編號'] == st.session_state.selected_slope_id]
        if not matched.empty:
            row = matched.iloc[0]
            q_grade = str(row['定性分級'])
            q_grade_cls = q_grade.replace("+", "plus")
            r_lat, r_lon = row.get('起點緯度'), row.get('起點經度')

            d_col_left, d_col_right = st.columns([1.05, 0.95])
            with d_col_left:
                card_top = f"""<div class='app-card notranslate' translate='no'>
<div style='display:flex; justify-content:space-between; align-items:center;'>
<span class='detail-green-text'>📍 {row['路線']} {row['里程樁號(起)']}</span>
<span class='badge badge-{q_grade_cls}'>{q_grade} 級</span>
</div>
<div style='font-family:monospace; font-size:13px; color:var(--text-muted); margin-top:2px;'>口卡：{row['口卡編號']}</div>
<div style='font-size:14.5px; font-weight:800; color:#4A6B82; margin-top:4px;'>構造物：{row.get('邊坡構造物', '自然邊坡')}</div>
</div>"""
                st.markdown(card_top, unsafe_allow_html=True)

                if pd.notna(r_lat) and pd.notna(r_lon):
                    gmap_nav_url = f"https://www.google.com/maps/dir/?api=1&destination={r_lat},{r_lon}"
                    gmap_street_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={r_lat},{r_lon}&heading=0&pitch=0&fov=90"
                    nav_btns = f"""<div style='display:flex; gap:8px; margin: 6px 0;' class='notranslate' translate='no'>
<a href='{gmap_nav_url}' target='_blank' style='flex:1; text-align:center; padding:11px 8px; background:#4A6B82; color:white; font-weight:800; border-radius:10px; text-decoration:none; font-size:15px;'>🧭 Google 導航</a>
<a href='{gmap_street_url}' target='_blank' style='flex:1; text-align:center; padding:11px 8px; background:#059669; color:white; font-weight:800; border-radius:10px; text-decoration:none; font-size:15px;'>🛣️ 現地街景</a>
</div>"""
                    st.markdown(nav_btns, unsafe_allow_html=True)
                    embed_map = f"""<div class='embed-map-box notranslate' translate='no'>
<iframe width='100%' height='550' frameborder='0' scrolling='no' src='https://maps.google.com/maps?q={r_lat},{r_lon}&t=k&z=17&ie=UTF8&iwloc=&output=embed'></iframe>
</div>"""
                    st.markdown(embed_map, unsafe_allow_html=True)

            with d_col_right:
                detail_fields = [
                    ("邊坡狀態 / 工務段", f"{row.get('邊坡狀態', '無')} / {row.get('工務段', '南澳工務段')}"),
                    ("里程區間", f"{row.get('里程樁號(起)', '')} ～ {row.get('里程樁號(迄)', '')}"),
                    ("起點經緯度", f"{r_lon:.5f}, {r_lat:.5f}" if pd.notna(r_lat) else "無"),
                    ("邊坡方向", str(row.get('邊坡方向', '無'))),
                    ("坡高 / 坡度 / 面寬", f"{row.get('坡高', '')}m / {row.get('坡度', '')}° / {row.get('邊坡面寬', '')}m"),
                    ("定性 / RHRS定量分級", f"{q_grade}級 / {row.get('定量分級', '未施作')}"),
                    ("災害歷史 / 附近地名", f"{row.get('災害歷史', '無')} / {row.get('附近地名', '無')}"),
                ]
                rows_html = "".join([f"<div class='detail-row'><span class='detail-label'>{k}</span><span class='detail-value'>{v}</span></div>" for k, v in detail_fields])
                st.markdown(f"<div class='app-card notranslate' translate='no'>{rows_html}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='app-card notranslate' translate='no' style='background:var(--card-bg); border-left:4px solid #4A6B82; line-height:1.6; font-size:14px; height:415px; overflow-y:auto;'><b>現地狀況描述：</b><br><div style='margin-top:6px;'>{row.get('現地狀況描述', '無描述紀錄')}</div></div>", unsafe_allow_html=True)
    else:
        with st.container(border=True):
            c_f1, c_f2, c_f3, c_f4 = st.columns([1.1, 1.1, 1.8, 1.1])
            with c_f1:
                route_list = ["全部路線"] + list(df['路線'].dropna().unique())
                route_filter = st.selectbox("路線篩選", route_list, label_visibility="collapsed")
            with c_f2:
                qual_filter = st.selectbox("分級篩選", ["全部分級", "A", "B", "C+", "C", "D", "其他"], label_visibility="collapsed")
            with c_f3:
                search_kw = st.text_input("搜尋", placeholder="🔍 搜尋里程(8k+600)、地名、岩錨...", label_visibility="collapsed")
                search_kw_clean = search_kw.strip() if search_kw else ""
            with c_f4:
                priority_toggle = st.checkbox("🚨 震度4級快篩", value=st.session_state.priority_mode, help="篩選 A、B 級且具 RHRS 定量評估之優先關注邊坡")
                if priority_toggle != st.session_state.priority_mode:
                    st.session_state.priority_mode = priority_toggle
                    st.rerun()

            f_df = df.copy()
            if route_filter != "全部路線": f_df = f_df[f_df['路線'] == route_filter]
            if qual_filter != "全部分級": f_df = f_df[f_df['定性分級'] == qual_filter]
            if st.session_state.priority_mode:
                f_df = f_df[f_df['定性分級'].isin(["A", "B"]) & (f_df['定量分級'] != "未施作")]

            if search_kw_clean:
                match_cond = (
                    f_df['口卡編號'].astype(str).str.contains(search_kw_clean, case=False, na=False) |
                    f_df['里程樁號(起)'].astype(str).str.contains(search_kw_clean, case=False, na=False) |
                    f_df['里程樁號(迄)'].astype(str).str.contains(search_kw_clean, case=False, na=False) |
                    f_df['附近地名'].astype(str).str.contains(search_kw_clean, case=False, na=False)
                )
                if '邊坡構造物' in f_df.columns:
                    match_cond |= f_df['邊坡構造物'].astype(str).str.contains(search_kw_clean, case=False, na=False)
                if '邊坡方向' in f_df.columns:
                    match_cond |= f_df['邊坡方向'].astype(str).str.contains(search_kw_clean, case=False, na=False)
                f_df = f_df[match_cond]

            q_counts = f_df['定性分級'].value_counts()
            st.markdown('<div id="grade-pills-anchor"></div>', unsafe_allow_html=True)
            grade_categories = ["A", "B", "C+", "C", "D", "其他"]
            b_cols = st.columns(6)
            for idx, g in enumerate(grade_categories):
                with b_cols[idx]:
                    is_active_g = (st.session_state.active_grade_detail == g)
                    if st.button(f"{g}級 ({q_counts.get(g, 0)})", key=f"badge_btn_{g}", use_container_width=True, type="primary" if is_active_g else "secondary"):
                        st.session_state.active_grade_detail = g if not is_active_g else None
                        st.rerun()

        if st.session_state.priority_mode:
            st.warning("🚨 **【震度4級優先關注邊坡應變模式】** 已過濾出 A、B 級且具 RHRS 定量評估之高風險邊坡。")

        display_target_df = f_df[f_df['定性分級'] == st.session_state.active_grade_detail] if st.session_state.active_grade_detail else f_df
        header_hint = f"📌【{st.session_state.active_grade_detail}級】篩選結果" if st.session_state.active_grade_detail else "📋 邊坡資產快速點選艙"
        st.caption(f"{header_hint}（共 **{len(display_target_df)}** 處，可直接於下方獨立視窗內滑動點選）：")

        with st.container(height=500, border=True):
            grid_cols = st.columns(2)
            for idx, (_, r) in enumerate(display_target_df.iterrows()):
                grade = str(r['定性分級'])
                quant_g = r.get('定量分級', '未施作')
                struct_short = str(r.get('邊坡構造物', '自然邊坡'))[:12]
                with grid_cols[idx % 2]:
                    with st.container(border=True):
                        c_card1, c_card2 = st.columns([0.62, 0.38])
                        with c_card1:
                            st.markdown(f"<span class='route-green-text'>📍 {r['路線']} {r['里程樁號(起)']}</span>", unsafe_allow_html=True)
                            st.caption(f"`{grade}級` ｜ `{struct_short}`")
                        with c_card2:
                            if st.button("🔍 檢視", key=f"pick_{r['口卡編號']}", use_container_width=True, type="primary"):
                                st.session_state.selected_slope_id = r['口卡編號']
                                st.rerun()

# ==============================================================================
# 頁面 2：定量定性分級統計
# ==============================================================================
elif st.session_state.bottom_tab == "📊 定量定性":
    c_t1, c_t2 = st.columns([0.6, 0.4])
    with c_t1:
        st.markdown("<div class='map-sub-title notranslate' translate='no' style='text-align:left;'>📊 邊坡定量與定性分級統計儀表板</div>", unsafe_allow_html=True)
    with c_t2:
        chart_type = st.radio("圖表模式", ["📊 長條圖", "🍩 圓餅圖"], horizontal=True, index=0, label_visibility="collapsed")

    stat_col1, stat_col2 = st.columns(2)

    with stat_col1:
        with st.container(border=True):
            st.markdown("**1. 定性分級統計（含115年修訂 C+ 級）**")
            qual_df_raw = df.copy()
            qual_df_raw['定性分級'] = qual_df_raw['定性分級'].replace({"其他": "其他(廢線)"})
            qual_order = ["A", "B", "C+", "C", "D", "其他(廢線)"]
            c_counts = qual_df_raw['定性分級'].value_counts()
            qual_df = pd.DataFrame({
                "分級": qual_order, "數量": [c_counts.get(c, 0) for c in qual_order],
                "圖例標籤": [f"{c} ({c_counts.get(c, 0)})" for c in qual_order]
            })
            qual_color = {
                f"A ({c_counts.get('A', 0)})": "#c05646", f"B ({c_counts.get('B', 0)})": "#d9822b",
                f"C+ ({c_counts.get('C+', 0)})": "#7c3aed", f"C ({c_counts.get('C', 0)})": "#4A6B82",
                f"D ({c_counts.get('D', 0)})": "#52796f", f"其他(廢線) ({c_counts.get('其他(廢線)', 0)})": "#64748b"
            }
            if "圓餅圖" in chart_type:
                fig_qual = px.pie(qual_df, values='數量', names='圖例標籤', hole=0.45, color='圖例標籤', color_discrete_map=qual_color, category_orders={"圖例標籤": qual_df['圖例標籤'].tolist()})
                fig_qual.update_traces(textposition='inside', textinfo='label', textfont_size=15, sort=False)
            else:
                fig_qual = px.bar(qual_df, x="圖例標籤", y="數量", text="數量", color="圖例標籤", color_discrete_map=qual_color, category_orders={"圖例標籤": qual_df['圖例標籤'].tolist()})
                fig_qual.update_traces(textposition='outside', textfont_size=15)
            fig_qual.update_layout(margin=dict(l=5, r=5, t=15, b=5), height=320, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color, size=14))
            st.plotly_chart(fig_qual, use_container_width=True)

    with stat_col2:
        with st.container(border=True):
            st.markdown("**2. RHRS 落石風險定量分級統計**")
            quant_order = ["第1級", "第2級", "第3級", "第4級", "第5級"]
            q_counts = df['定量分級'].value_counts()
            quant_df = pd.DataFrame({
                "RHRS定量分級": quant_order, "數量": [q_counts.get(c, 0) for c in quant_order],
                "圖例標籤": [f"{c} ({q_counts.get(c, 0)})" for c in quant_order]
            })
            quant_color = {
                f"第1級 ({q_counts.get('第1級', 0)})": "#1e40af", f"第2級 ({q_counts.get('第2級', 0)})": "#3b82f6", 
                f"第3級 ({q_counts.get('第3級', 0)})": "#f97316", f"第4級 ({q_counts.get('第4級', 0)})": "#ef4444", 
                f"第5級 ({q_counts.get('第5級', 0)})": "#b91c1c"
            }
            if "圓餅圖" in chart_type:
                fig_quant = px.pie(quant_df, values='數量', names='圖例標籤', hole=0.45, color='圖例標籤', color_discrete_map=quant_color, category_orders={"圖例標籤": quant_df['圖例標籤'].tolist()})
                fig_quant.update_traces(textposition='inside', textinfo='label', textfont_size=15, sort=False)
            else:
                fig_quant = px.bar(quant_df, x="圖例標籤", y="數量", text="數量", color="圖例標籤", color_discrete_map=quant_color, category_orders={"圖例標籤": quant_df['圖例標籤'].tolist()})
                fig_quant.update_traces(textposition='outside', textfont_size=15)
            fig_quant.update_layout(margin=dict(l=5, r=5, t=15, b=5), height=320, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=plotly_font_color, size=14))
            st.plotly_chart(fig_quant, use_container_width=True)

# ==============================================================================
# 頁面 3：地圖定位 
# ==============================================================================
elif st.session_state.bottom_tab == "🗺️ 地圖定位":
    search_res_ph = st.empty()
    valid_pts = df.dropna(subset=['起點緯度', '起點經度'])

    if not valid_pts.empty:
        m_loc = folium.Map(location=[valid_pts['起點緯度'].median(), valid_pts['起點經度'].median()], zoom_start=11, tiles=None)
        
        loc_options = {"enableHighAccuracy": True, "timeout": 10000, "maximumAge": 0}
        loc_strings = {"title": "📍 定位您的位置", "popup": "您目前的位置", "outsideMapBoundsMsg": "您位於地圖邊界之外", "error": "定位失敗：請確認手機已開啟GPS定位權限。"}
        LocateControl(auto_start=False, flyTo=True, locateOptions=loc_options, strings=loc_strings).add_to(m_loc)
        
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Earth", name="🛰️ 衛星空照圖").add_to(m_loc)
        folium.TileLayer(tiles="OpenStreetMap", name="🗺️ 標準電子地圖").add_to(m_loc)

        if geo_files:
            gs_ov, gs_poly = load_kmz_overlay(geo_files, remove_white_bg=True, clip_to_nanao=False)
            add_spatial_layer_to_map(m_loc, gs_ov, gs_poly, layer_name="🧱 南澳工務段地質敏感區", color_hex="#d97706", opacity=0.65, show_default=False)
        if debris_files:
            db_ov, db_poly = load_kmz_overlay(debris_files, remove_white_bg=True, clip_to_nanao=True)
            add_spatial_layer_to_map(m_loc, db_ov, db_poly, layer_name="🌊 115年度土石流潛勢溪流圖", color_hex="#0284c7", opacity=0.75, show_default=False)

        cmap = {"A": "#c05646", "B": "#d9822b", "C+": "#7c3aed", "C": "#4A6B82", "D": "#52796f", "其他": "#64748b"}
        for _, r in valid_pts.iterrows():
            g = str(r['定性分級'])
            p_lat, p_lon = r['起點緯度'], r['起點經度']
            nav_url = f"https://www.google.com/maps/dir/?api=1&destination={p_lat},{p_lon}"
            street_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={p_lat},{p_lon}&heading=0&pitch=0&fov=90"
            popup_html = f"""<div style='font-size:14.5px; line-height:1.6; min-width:240px; white-space:nowrap;'>
<b style='font-size:16px; color:#0f172a;'>{r['路線']} {r['里程樁號(起)']}</b><br/>
<b>卡號：</b>{r['口卡編號']}<br/>
<b>分級：</b><span style='color:{cmap.get(g, "#64748b")}; font-weight:bold;'>{g} 級</span>（RHRS: {r.get('定量分級', '未施作')}）<br/>
<b>構造：</b>{r.get('邊坡構造物', '自然邊坡')}<br/>
<div style='margin-top:8px;'>
  <a href='{nav_url}' target='_blank' style='display:inline-block; padding:6px 12px; background:#4A6B82; color:white; border-radius:6px; text-decoration:none; font-weight:bold;'>🧭 導航</a>
  <a href='{street_url}' target='_blank' style='display:inline-block; margin-left:6px; padding:6px 12px; background:#059669; color:white; border-radius:6px; text-decoration:none; font-weight:bold;'>🛣️ 街景</a>
</div>
</div>"""
            folium.CircleMarker(location=[p_lat, p_lon], radius=6.5, popup=folium.Popup(popup_html, max_width=380), color=cmap.get(g, '#64748b'), fill=True, fill_opacity=0.88).add_to(m_loc)
        
        # 修正：預設隱藏圖層控制器
        folium.LayerControl(position="topright", collapsed=True).add_to(m_loc)
        
        map_output = st_folium(m_loc, width="100%", height=540)
        if map_output and map_output.get("last_clicked"):
            c_lat, c_lon = map_output["last_clicked"]["lat"], map_output["last_clicked"]["lng"]
            if not df_mileages.empty:
                near_name, dist = get_interpolated_mileage(c_lat, c_lon, df_mileages)
                search_res_ph.success(f"🎯 **點圖定位分析**：此位置最接近 **{near_name}**（誤差約 {dist:.0f} 公尺）")

# ==============================================================================
# 頁面 4：災害斑點圖 
# ==============================================================================
elif st.session_state.bottom_tab == "🔥 災害斑點圖":
    with st.container(border=True):
        ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4 = st.columns([1.1, 1.2, 1.3, 1.2])
        with ctrl_c1:
            show_geo_layer = st.checkbox("🧱 地質敏感區底圖", value=True)
        with ctrl_c2:
            show_debris_layer = st.checkbox("🌊 土石流潛勢溪流", value=True)
        with ctrl_c3:
            transparent_white = st.checkbox("✨ 濾除圖資白底", value=True)
        with ctrl_c4:
            geo_opacity = st.slider("🎚️ 圖層透明度", min_value=0.10, max_value=1.00, value=0.65, step=0.05)

        if show_debris_layer and not debris_files:
            st.caption("⚠️ **系統提示**：目前專案目錄中尚未偵測到「土石流潛勢溪流」KMZ/KML 檔案，請確認該檔案已上傳至 GitHub 專案根目錄。")

    gs_overlays, gs_polygons = load_kmz_overlay(geo_files, remove_white_bg=transparent_white, clip_to_nanao=False) if geo_files else ([], [])
    db_overlays, db_polygons = load_kmz_overlay(debris_files, remove_white_bg=transparent_white, clip_to_nanao=True) if debris_files else ([], [])

    search_res_ph = st.empty()
    
    if not df_disasters.empty or gs_overlays or db_overlays or gs_polygons or db_polygons:
        default_lat = df_disasters['緯度'].median() if not df_disasters.empty else 24.465
        default_lon = df_disasters['經度'].median() if not df_disasters.empty else 121.802
        m_dis = folium.Map(location=[default_lat, default_lon], zoom_start=11, tiles=None)
        
        loc_options = {"enableHighAccuracy": True, "timeout": 10000, "maximumAge": 0}
        loc_strings = {"title": "📍 定位您的位置", "popup": "您目前的位置", "outsideMapBoundsMsg": "您位於地圖邊界之外", "error": "定位失敗"}
        LocateControl(auto_start=False, flyTo=True, locateOptions=loc_options, strings=loc_strings).add_to(m_dis)
        
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Earth", name="🛰️ 衛星空照圖").add_to(m_dis)
        folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}", attr="Google Terrain", name="⛰️ 地形等高線圖").add_to(m_dis)
        folium.TileLayer(tiles="OpenStreetMap", name="🗺️ 標準電子地圖").add_to(m_dis)
        
        if show_geo_layer and (gs_overlays or gs_polygons):
            add_spatial_layer_to_map(m_dis, gs_overlays, gs_polygons, layer_name="🧱 南澳工務段地質敏感區", color_hex="#d97706", opacity=geo_opacity, show_default=True)

        if show_debris_layer and (db_overlays or db_polygons):
            add_spatial_layer_to_map(m_dis, db_overlays, db_polygons, layer_name="🌊 115年度土石流潛勢溪流圖", color_hex="#0284c7", opacity=min(1.0, geo_opacity + 0.15), show_default=True)

        yp = {"112年": "#457b9d", "113年": "#e63946", "114年": "#f77f00", "115年": "#2a9d8f"}
        if not df_disasters.empty:
            for yr in sorted(df_disasters['年度'].unique()):
                fg = folium.FeatureGroup(name=f"📍 {yr}災害點位 ({len(df_disasters[df_disasters['年度'] == yr])}處)", show=True)
                for _, d in df_disasters[df_disasters['年度'] == yr].iterrows():
                    nav_url = f"https://www.google.com/maps/dir/?api=1&destination={d['緯度']},{d['經度']}"
                    street_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={d['緯度']},{d['經度']}&heading=0&pitch=0&fov=90"
                    popup_html = f"""<div style='font-size:14.5px; line-height:1.6; min-width:240px;'>
<span style='background:{yp.get(yr, "#8338ec")}; color:white; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:12px;'>{yr}</span><br/>
<b style='font-size:16px; color:#0f172a; display:block; margin-top:6px;'>{d['災害名稱']}</b>
<div style='margin-top:4px; white-space:normal; word-wrap:break-word; color:#334155;'>{d['詳細說明']}</div>
<div style='margin-top:10px;'>
  <a href='{nav_url}' target='_blank' style='display:inline-block; padding:6px 12px; background:#4A6B82; color:white; border-radius:6px; text-decoration:none; font-weight:bold;'>🧭 導航</a>
  <a href='{street_url}' target='_blank' style='display:inline-block; margin-left:6px; padding:6px 12px; background:#059669; color:white; border-radius:6px; text-decoration:none; font-weight:bold;'>🛣️ 街景</a>
</div>
</div>"""
                    folium.CircleMarker(
                        location=[d['緯度'], d['經度']], radius=6.5, popup=folium.Popup(popup_html, max_width=400),
                        color="#ffffff", weight=1.5, fill=True, fill_color=yp.get(yr, "#8338ec"), fill_opacity=0.95
                    ).add_to(fg)
                fg.add_to(m_dis)
        
        # 修正：將自訂圖例改為可點擊展開的摺疊選單，預設隱藏不佔空間
        legend_html = '''
        <div style="position: fixed; bottom: 20px; right: 20px; background-color: rgba(255,255,255,0.94); z-index:9999; border-radius: 8px; border: 2px solid #cbd5e1; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
            <details style="padding: 8px 10px; cursor: pointer;">
                <summary style="margin: 0; font-weight: 900; font-size: 13.5px; color:#0f172a; list-style: none; outline: none;"><span style="margin-right:4px;">🗺️</span> 委員審查圖例</summary>
                <div style="margin-top: 6px; border-top:1px solid #cbd5e1; padding-top:6px; min-width: 160px;">
                    <p style="margin: 2px 0; font-size: 12.5px; font-weight:bold; color:#0f172a;"><span style="color: #457b9d;">●</span> 112年 ｜ <span style="color: #e63946;">●</span> 113年</p>
                    <p style="margin: 2px 0; font-size: 12.5px; font-weight:bold; color:#0f172a;"><span style="color: #f77f00;">●</span> 114年 ｜ <span style="color: #2a9d8f;">●</span> 115年</p>
                    <p style="margin: 4px 0 2px 0; font-size: 11.5px; font-weight:bold; color:#b45309; background:#fef3c7; padding:2px 4px; border-radius:3px; display:inline-block;">🧱 南澳地質敏感區</p><br>
                    <p style="margin: 2px 0 0 0; font-size: 11.5px; font-weight:bold; color:#0369a1; background:#e0f2fe; padding:2px 4px; border-radius:3px; display:inline-block;">🌊 土石流潛勢溪流圖</p>
                </div>
            </details>
        </div>
        '''
        m_dis.get_root().html.add_child(folium.Element(legend_html))
        
        # 修正：預設隱藏圖層控制器
        folium.LayerControl(position="topright", collapsed=True).add_to(m_dis)
        
        map_output = st_folium(m_dis, width="100%", height=520)
        if map_output and map_output.get("last_clicked"):
            c_lat, c_lon = map_output["last_clicked"]["lat"], map_output["last_clicked"]["lng"]
            if not df_mileages.empty:
                near_name, dist = get_interpolated_mileage(c_lat, c_lon, df_mileages)
                search_res_ph.success(f"🎯 **點圖定位分析**：此位置最接近 **{near_name}**（誤差約 {dist:.0f} 公尺）｜ 座標：({c_lat:.5f}, {c_lon:.5f})")

# ==============================================================================
# 頁面 5：養護巡查
# ==============================================================================
elif st.session_state.bottom_tab == "📝 養護巡查":
    slope_opts = df['口卡編號'].dropna().unique().tolist()
    def_idx = slope_opts.index(st.session_state.target_slope_for_patrol) if "target_slope_for_patrol" in st.session_state and st.session_state.target_slope_for_patrol in slope_opts else 0

    with st.container(border=True):
        top_p1, top_p2 = st.columns([0.55, 0.45])
        with top_p1:
            chosen_code = st.selectbox("🎯 巡查目標口卡編號", slope_opts, index=def_idx)
            target_row = df[df['口卡編號'] == chosen_code].iloc[0]
        with top_p2:
            raw_s = str(target_row.get('邊坡構造物', '自然邊坡'))
            avail_s = list(dict.fromkeys([s.strip() for s in re.split(r'[,、]', raw_s) if s.strip()] + ["自然邊坡"]))
            chosen_struct = st.selectbox("🏗️ 構造物設施類別", avail_s)
            current_tpl = INSPECTION_TEMPLATES[match_template(chosen_struct)]

    draft = st.session_state.patrol_draft.get(f"{chosen_code}_{chosen_struct}", {})
    gps_info_ph = st.empty()

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "① 基本環境與現況",
        f"② 設施項目檢測 ({len(current_tpl['items'])}項)",
        "③ 綜合備註與署名"
    ])

    with sub_tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1: f_date = st.date_input("檢測日期", draft.get("date", datetime.date.today()))
        with c2: mile_text_ph = st.empty()
        with c3: f_weather = st.selectbox("天氣狀況", ["晴", "陰", "雨"], index=["晴", "陰", "雨"].index(draft.get("weather", "晴")))
        with c4: f_type = st.selectbox("檢測類別", ["定期檢測", "特別檢測"], index=["定期檢測", "特別檢測"].index(draft.get("type", "定期檢測")))

        cg1, cg2, cg3, cg4 = st.columns(4)
        with cg1: f_geo = st.selectbox("地質狀況", ["土層邊坡", "岩層邊坡", "礫石層邊坡", "其他地質"], index=["土層邊坡", "岩層邊坡", "礫石層邊坡", "其他地質"].index(draft.get("geo", "土層邊坡")))
        with cg2: f_water = st.selectbox("地下水／湧水", ["乾燥", "濕潤", "表面水", "湧水"], index=["乾燥", "濕潤", "表面水", "湧水"].index(draft.get("water", "乾燥")))
        with cg3: f_drain = st.selectbox("排(洩)水管", ["正常", "阻塞"], index=["正常", "阻塞"].index(draft.get("drain", "正常")))
        with cg4: f_disaster = st.selectbox("以往災害歷史", ["無", "有"], index=["無", "有"].index(draft.get("disaster", "無")))

    with sub_tab2:
        q_col1, q_col2 = st.columns([0.65, 0.35])
        with q_col1:
            st.caption("📱 僅需針對異常或欲拍照項目展開操作（內部視窗獨立捲動，不影響底欄按鈕）：")
        with q_col2:
            if st.button("⚡ 一鍵全設為「○ 正常」", use_container_width=True):
                for idx in range(len(current_tpl["items"])):
                    st.session_state[f"patrol_res_{chosen_code}_{idx}"] = "○ 正常"
                st.rerun()

        item_results = []
        draft_items = draft.get("items", {})
        all_item_photos = []
        photo_lat, photo_lon = None, None

        with st.container(height=420, border=True):
            for idx, (iname, iact) in enumerate(current_tpl["items"]):
                res_key = f"patrol_res_{chosen_code}_{idx}"
                prev_res = draft_items.get(iname, {}).get("res", "○ 正常")
                if res_key not in st.session_state:
                    st.session_state[res_key] = prev_res if prev_res in ["○ 正常", "× 異常", "／ 無此項"] else "○ 正常"

                with st.container(border=True):
                    ci1, ci2 = st.columns([0.52, 0.48])
                    with ci1:
                        st.markdown(f"**{iname}**")
                        st.caption(f"養護措施：{iact}")
                    with ci2:
                        res_val = st.radio("結果", ["○ 正常", "× 異常", "／ 無此項"], horizontal=True, key=res_key, label_visibility="collapsed")
                        desc_val = st.text_input("異常說明", value=draft_items.get(iname, {}).get("desc", ""), key=f"patrol_desc_{chosen_code}_{idx}", placeholder="✏️ 請輸入異常狀況...") if "×" in res_val else ""

                    with st.expander("📸 點擊開啟相機／上傳此項目特寫照片", expanded=("×" in res_val)):
                        up_files = st.file_uploader("上傳照片", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=f"photo_item_{chosen_code}_{idx}", label_visibility="collapsed")
                        if up_files:
                            for f in up_files:
                                img_bytes = f.getvalue()
                                if "×" in res_val and desc_val:
                                    p_desc = f"【{iname}】異常說明：{desc_val}"
                                elif "×" in res_val:
                                    p_desc = f"【{iname}】異常"
                                elif "／" in res_val:
                                    p_desc = f"【{iname}】無此項"
                                else:
                                    p_desc = f"【{iname}】現況正常"
                                all_item_photos.append((img_bytes, p_desc))
                                if photo_lat is None:
                                    photo_lat, photo_lon = extract_gps(img_bytes)

                item_results.append((iname, iact, res_val[0], desc_val))

    with sub_tab3:
        date_str = f"{f_date.year - 1911}年{f_date.month:02d}月{f_date.day:02d}日"
        t1 = f"經本段{date_str}巡檢{chosen_struct}設施結構大致完整良好。"
        t2 = f"經本段{date_str}巡檢{chosen_struct}林相完整，植生良好無坡面沖刷情形。"
        t3 = f"經本段{date_str}巡檢{chosen_struct}大致完整且植生生長良好。"
        t4 = f"經本段{date_str}巡檢{chosen_struct}大致完整良好且洩水孔排水功能暢通。"
        t_custom = "✏️ 自訂輸入其他內容..."

        remark_sel = st.selectbox("快速套用備註模版", [t1, t2, t3, t4, t_custom])
        if remark_sel == t_custom:
            f_remark = st.text_area("自訂現地備註", value=draft.get("remark", ""), height=90)
        else:
            f_remark = remark_sel

        cu1, cu2 = st.columns(2)
        with cu1: f_inspector = st.text_input("檢測人員姓名 (必填)", value=draft.get("inspector", ""), placeholder="例如：李工程師")
        with cu2: f_supervisor = st.text_input("單位主管 (選填)", value=draft.get("supervisor", "段長"), placeholder="例如：段長")

    mile_text = target_row.get('里程樁號(起)', '')
    if photo_lat and photo_lon and not df_mileages.empty:
        mile_text, dist = get_interpolated_mileage(photo_lat, photo_lon, df_mileages)
        gps_info_ph.success(f"📍 已由照片解析 GPS ({photo_lat:.4f}, {photo_lon:.4f})，空間幾何內插定位：**{mile_text}**")
    with mile_text_ph:
        st.text_input("里程樁號 (圖資定位)", value=mile_text, disabled=True)

    export_name_doc = f"邊坡口卡編號{chosen_code}-構造物{chosen_struct}.doc"
    export_name_zip = f"{chosen_code}_照片打包.zip"
    
    report_data = {
        "title": current_tpl.get("title"), "category_col_header": current_tpl.get("category_col_header"),
        "category_name": current_tpl.get("category_name"), "dim_title": current_tpl.get("dim_title"),
        "dim_h_label": current_tpl.get("dim_h_label"), "dim_w_label": current_tpl.get("dim_w_label"),
        "code": chosen_code, "date": f"{f_date.year - 1911}年{f_date.month:02d}月{f_date.day:02d}日", "weather": f_weather, "type": f_type,
        "unit": "南澳工務段", "location": f"{target_row.get('鄉鎮市區', '蘇澳鎮')} {target_row.get('路線', '')} {mile_text}",
        "direction": target_row.get("方向", "北下"), "geo": f_geo, "height": target_row.get("坡高", "30"),
        "slope": target_row.get("坡度", "85"), "width": target_row.get("邊坡面寬", "200"), "water": f_water,
        "drain": f_drain, "survey_month": f_date.month, "rain_days": "3", "check_rows": item_results,
        "remark": f_remark.strip(), "inspector": f_inspector, "supervisor": f_supervisor
    }
    doc_bytes = generate_doc_report(report_data, all_item_photos)
    b64_doc = base64.b64encode(doc_bytes).decode()
    b64_zip = base64.b64encode(create_photos_zip(all_item_photos, f"{chosen_code}_{chosen_struct}")).decode() if all_item_photos else None

    act_col1, act_col2, act_col3 = st.columns(3)
    btn_style = (
        "display: flex; align-items: center; justify-content: center; width: 100%; "
        "padding: 0.35rem 0.75rem; min-height: 44px; "
        "background-color: var(--btn-sec-bg); color: var(--btn-sec-text); "
        "border: 1.5px solid var(--btn-sec-border); border-radius: 10px; "
        "text-decoration: none; font-size: 15px; font-weight: 800; box-shadow: 0 1px 2px rgba(0,0,0,0.04);"
    )
    
    with act_col1:
        if st.button("💾 暫存草稿", use_container_width=True):
            st.session_state.patrol_draft[f"{chosen_code}_{chosen_struct}"] = {
                "date": f_date, "weather": f_weather, "type": f_type, "geo": f_geo, "water": f_water,
                "drain": f_drain, "disaster": f_disaster, "remark": f_remark, "inspector": f_inspector,
                "supervisor": f_supervisor, "items": {item[0]: {"res": item[2], "desc": item[3]} for item in item_results}
            }
            st.toast("✅ 草稿已成功暫存！")

    with act_col2:
        st.markdown(f'<a href="data:application/msword;base64,{b64_doc}" download="{export_name_doc}" target="_blank" style="{btn_style}">📥 產出檢測表 (.doc)</a>', unsafe_allow_html=True)

    with act_col3:
        if b64_zip:
            st.markdown(f'<a href="data:application/zip;base64,{b64_zip}" download="{export_name_zip}" target="_blank" style="{btn_style}">📦 下載照片 ({len(all_item_photos)}張)</a>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="{btn_style} opacity: 0.45; cursor: not-allowed;">📦 尚無照片可打包</div>', unsafe_allow_html=True)

# 頁尾
st.markdown(render_footer(), unsafe_allow_html=True)