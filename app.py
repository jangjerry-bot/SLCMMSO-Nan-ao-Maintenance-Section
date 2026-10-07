import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

st.set_page_config(
    page_title="南澳工務段 邊坡生命週期維護系統",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. 資料載入與快取機制
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    # 確保經緯度欄位為數值格式
    df['起點緯度'] = pd.to_numeric(df['起點緯度'], errors='coerce')
    df['起點經度'] = pd.to_numeric(df['起點經度'], errors='coerce')
    df['定量分級'] = df['定量分級'].fillna('未分級')
    df['定性分級'] = df['定性分級'].fillna('未分級')
    return df

try:
    df_raw = load_data("邊坡資料.xlsx")
except Exception as e:
    st.error(f"資料讀取失敗，請確認檔案路徑是否正確：{e}")
    st.stop()

# 2. 側邊欄多條件動態篩選
st.sidebar.title("邊坡檢索與篩選")

routes = ['全部'] + sorted(list(df_raw['路線'].dropna().unique()))
selected_route = st.sidebar.selectbox("路線選擇", routes)

qual_grades = ['全部'] + sorted(list(df_raw['定性分級'].astype(str).unique()))
selected_qual = st.sidebar.selectbox("定性分級", qual_grades)

monitor_levels = ['全部'] + sorted(list(df_raw['監控等級'].dropna().unique()))
selected_monitor = st.sidebar.selectbox("監控等級", monitor_levels)

search_keyword = st.sidebar.text_input("口卡編號 / 地名關鍵字搜尋")

# 資料過濾邏輯
filtered_df = df_raw.copy()
if selected_route != '全部':
    filtered_df = filtered_df[filtered_df['路線'] == selected_route]
if selected_qual != '全部':
    filtered_df = filtered_df[filtered_df['定性分級'] == selected_qual]
if selected_monitor != '全部':
    filtered_df = filtered_df[filtered_df['監控等級'] == selected_monitor]
if search_keyword:
    filtered_df = filtered_df[
        filtered_df['口卡編號'].astype(str).str.contains(search_keyword, case=False, na=False) |
        filtered_df['附近地名'].astype(str).str.contains(search_keyword, case=False, na=False)
    ]

# 主標題與關鍵指標
st.title("南澳工務段 邊坡生命週期管理系統")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("邊坡總數", f"{len(filtered_df)} 處")
col_m2.metric("A 級/重點監控", f"{len(filtered_df[filtered_df['定性分級'] == 'A'])} 處")
col_m3.metric("地錨結構邊坡", f"{len(filtered_df[filtered_df['邊坡構造物'].astype(str).str.contains('錨', na=False)])} 處")
col_m4.metric("列管案件數", f"{len(filtered_df[filtered_df['專案列管案件'].notna()])} 處")

tab_dashboard, tab_map, tab_records, tab_inspect = st.tabs(["📊 統計分級儀表板", "🗺️ GIS 地圖定位", "📋 邊坡清冊詳細資料", "📝 現地巡查回報"])

# --- Tab 1: 統計圖表 ---
with tab_dashboard:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("邊坡定性分級分布")
        qual_counts = filtered_df['定性分級'].value_counts().reset_index()
        qual_counts.columns = ['定性分級', '數量']
        fig_qual = px.bar(
            qual_counts, x='數量', y='定性分級', orientation='h',
            color='定性分級', text='數量',
            color_discrete_map={'A': '#EF553B', 'B': '#FFA15A', 'C': '#636EFA', 'D': '#00CC96'}
        )
        st.plotly_chart(fig_qual, use_container_width=True)

    with col_chart2:
        st.subheader("邊坡定量分級分布")
        quant_counts = filtered_df['定量分級'].value_counts().reset_index()
        quant_counts.columns = ['定量分級', '數量']
        fig_quant = px.bar(
            quant_counts, x='定量分級', y='數量',
            color='定量分級', text='數量',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_quant, use_container_width=True)

# --- Tab 2: GIS 地圖定位 ---
with tab_map:
    st.subheader("邊坡空間位置分布")
    valid_geo = filtered_df.dropna(subset=['起點緯度', '起點經度'])
    
    if not valid_geo.empty:
        center_lat = valid_geo['起點緯度'].median()
        center_lon = valid_geo['起點經度'].median()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap")
        
        # 標註點位顏色對照
        color_map = {'A': 'red', 'B': 'orange', 'C': 'blue', 'D': 'green', '未分級': 'gray'}
        
        for _, row in valid_geo.iterrows():
            grade = str(row['定性分級'])
            marker_color = color_map.get(grade, 'cadetblue')
            popup_html = f"""
            <b>卡號：</b>{row['口卡編號']}<br>
            <b>路線：</b>{row['路線']} ({row['里程樁號(起)']} ~ {row['里程樁號(迄)']})<br>
            <b>定性分級：</b>{grade}<br>
            <b>構造物：</b>{row.get('邊坡構造物', '無')}<br>
            <b>現況：</b>{str(row.get('現地狀況描述', '無'))[:50]}...
            """
            folium.CircleMarker(
                location=[row['起點緯度'], row['起點經度']],
                radius=6,
                popup=folium.Popup(popup_html, max_width=300),
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.8
            ).add_to(m)
            
        st_folium(m, width="100%", height=550)
    else:
        st.warning("目前篩選條件下無有效經緯度資料。")

# --- Tab 3: 詳細清冊 ---
with tab_records:
    st.subheader("邊坡詳細屬性表")
    display_cols = ['口卡編號', '路線', '里程樁號(起)', '里程樁號(迄)', '定性分級', '定量分級', '監控等級', '邊坡構造物', '附近地名', '最近更新時間']
    st.dataframe(filtered_df[display_cols], use_container_width=True)

# --- Tab 4: 現地巡查記錄 ---
with tab_inspect:
    st.subheader("現地巡查紀錄與現況更新")
    selected_slope = st.selectbox("選擇欲維護之口卡編號", filtered_df['口卡編號'].unique())
    slope_info = filtered_df[filtered_df['口卡編號'] == selected_slope].iloc[0]
    
    with st.form("inspection_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("路線與里程", value=f"{slope_info['路線']} {slope_info['里程樁號(起)']}", disabled=True)
            new_status = st.selectbox("安全狀態調整", ["正常", "注意", "警戒", "已通報補強"])
        with col2:
            st.text_input("目前構造物", value=str(slope_info.get('邊坡構造物', '')), disabled=True)
            photo = st.camera_input("現地拍照上傳")
            
        description = st.text_area("現地現況描述更新", value=str(slope_info.get('現地狀況描述', '')))
        submitted = st.form_submit_button("儲存回報紀錄")
        
        if submitted:
            st.success(f"已記錄口卡編號 {selected_slope} 之現況。")