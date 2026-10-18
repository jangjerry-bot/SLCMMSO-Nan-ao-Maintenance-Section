# style.py
import os
import base64

def get_theme_css(is_light: bool, show_splash: bool = True) -> str:
    if is_light:
        theme_vars = """
            --bg-main: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --card-bg: #ffffff;
            --card-border: #cbd5e1;
            --input-bg: #ffffff;
            --input-border: #94a3b8;
            --input-text: #0f172a;
            --btn-sec-bg: #ffffff;
            --btn-sec-text: #1e293b;
            --btn-sec-border: #cbd5e1;
            --dock-bg: rgba(255, 255, 255, 0.95);
            --dock-border: #cbd5e1;
            --footer-text: #4A6B82;
            --link-color: #2563eb;
        """
    else:
        theme_vars = """
            --bg-main: #0b0f19;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --card-bg: #1e293b;
            --card-border: #334155;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --input-text: #0f172a;
            --btn-sec-bg: #1e293b;
            --btn-sec-text: #f1f5f9;
            --btn-sec-border: #475569;
            --dock-bg: rgba(15, 23, 42, 0.95);
            --dock-border: #334155;
            --footer-text: #60a5fa;
            --link-color: #60a5fa;
        """

    splash_overlay_html = (
        '<div id="geo-splash-overlay">'
        '<div class="geo-splash-center">'
        '<div class="geo-hud-badge">GEO-NUMERICAL ENGINE // SEEP3D &amp; SLOPE/W</div>'
        '<svg class="geo-splash-svg" viewBox="0 0 360 240" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<defs>'
        '<linearGradient id="spBase" x1="50" y1="125" x2="310" y2="205" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#3f6259"/><stop offset="1" stop-color="#1b2e29"/>'
        '</linearGradient>'
        '<linearGradient id="spPrism" x1="150" y1="55" x2="180" y2="178" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#4A6B82" stop-opacity="0.92"/><stop offset="1" stop-color="#1e293b" stop-opacity="0.98"/>'
        '</linearGradient>'
        '<linearGradient id="spWater" x1="95" y1="75" x2="245" y2="152" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#38bdf8" stop-opacity="0.9"/><stop offset="1" stop-color="#0284c7" stop-opacity="0.6"/>'
        '</linearGradient>'
        '<filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">'
        '<feGaussianBlur stdDeviation="4" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/>'
        '</filter>'
        '</defs>'
        '<g class="geo-mesh-grid" stroke="#475569" stroke-width="0.8" stroke-opacity="0.5">'
        '<path d="M30 160 L180 225 L330 160 L180 95 Z" fill="rgba(15, 23, 42, 0.6)"/>'
        '<path d="M67 144 L217 209"/><path d="M105 127 L255 192"/><path d="M142 111 L292 176"/>'
        '<path d="M105 192 L255 127"/><path d="M67 176 L217 111"/><path d="M142 209 L292 144"/>'
        '</g>'
        '<g class="geo-rain-lines" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="6 10" stroke-linecap="round" opacity="0.7">'
        '<line x1="140" y1="15" x2="120" y2="65" /><line x1="185" y1="10" x2="165" y2="60" />'
        '<line x1="230" y1="15" x2="210" y2="65" /><line x1="270" y1="25" x2="250" y2="75" />'
        '</g>'
        '<path class="geo-base-layer" d="M50 152 L180 208 L310 152 L310 122 L180 178 L50 122 Z" fill="url(#spBase)" stroke="#52796f" stroke-width="1.5"/>'
        '<path class="geo-slope-prism" d="M50 122 L180 178 L310 122 L260 58 L155 58 L50 122 Z" fill="url(#spPrism)" stroke="#64748b" stroke-width="1.5"/>'
        '<path class="geo-seepage-wave" d="M95 115 Q165 155 240 115 L252 80 Q175 112 140 80 Z" fill="url(#spWater)" stroke="#38bdf8" stroke-width="2"/>'
        '<path class="geo-flow-arrows" d="M130 100 Q165 128 215 102" stroke="#bae6fd" stroke-width="2" stroke-dasharray="5 5" stroke-linecap="round"/>'
        '<path class="geo-red-crest" d="M155 58 L260 58 L310 122" stroke="#f87171" stroke-width="2.5" stroke-linecap="round"/>'
        '<path class="geo-red-shear" filter="url(#glowRed)" d="M88 112 Q170 154 248 110" stroke="#ef4444" stroke-width="4" stroke-linecap="round"/>'
        '<line class="geo-slice-line" x1="120" y1="50" x2="120" y2="145" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3 3"/>'
        '</svg>'
        '<div class="geo-splash-title">南澳邊坡全生命週期資料庫</div>'
        '<div class="geo-splash-sub">GEOTECHNICAL LIFECYCLE &amp; SPATIAL INTELLIGENCE</div>'
        '<div class="geo-progress-bar"><div class="geo-progress-fill"></div></div>'
        '</div>'
        '</div>'
    )

    css_template = """
<style>
    :root { __THEME_VARS__ }

    #geo-splash-overlay { position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important; background: radial-gradient(circle at center, #111827 0%, #050811 100%) !important; z-index: 99999999 !important; display: flex !important; justify-content: center !important; align-items: center !important; pointer-events: none !important; animation: splashDismiss 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2.2s forwards !important; }
    @keyframes splashDismiss { 0% { opacity: 1; transform: scale(1); } 99% { opacity: 0; transform: scale(1.03); } 100% { opacity: 0; visibility: hidden; display: none !important; } }
    .geo-splash-center { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; text-align: center !important; padding: 20px !important; }
    .geo-hud-badge { font-family: monospace !important; font-size: 11px !important; color: #38bdf8 !important; background: rgba(56, 189, 248, 0.1) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important; padding: 4px 12px !important; border-radius: 20px !important; letter-spacing: 2px !important; margin-bottom: 10px !important; animation: titleFadeIn 0.5s ease-out !important; }
    .geo-splash-svg { width: clamp(270px, 48vw, 390px) !important; height: auto !important; filter: drop-shadow(0 18px 32px rgba(0, 0, 0, 0.7)) !important; }
    .geo-mesh-grid { animation: meshPop 0.6s ease-out; transform-origin: center; transform-box: fill-box; }
    .geo-base-layer { animation: modelRise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; transform-box: fill-box; }
    .geo-slope-prism { opacity: 0; animation: modelRise 0.6s 0.15s cubic-bezier(0.16, 1, 0.3, 1) forwards; transform-box: fill-box; }
    .geo-rain-lines { animation: rainFall 0.8s linear infinite; }
    .geo-seepage-wave { opacity: 0; animation: waterRise 0.9s 0.3s ease-out forwards, waterPulse 1.5s 1.2s ease-in-out infinite alternate; transform-origin: bottom center; transform-box: fill-box; }
    .geo-flow-arrows { stroke-dashoffset: 40; animation: flowMove 1.2s linear infinite; }
    .geo-red-crest { stroke-dasharray: 220; stroke-dashoffset: 220; animation: drawLine 0.8s 0.4s ease-out forwards; }
    .geo-red-shear { stroke-dasharray: 240; stroke-dashoffset: 240; animation: drawLine 0.9s 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards, shearPulse 0.6s 1.4s ease-in-out infinite alternate; }
    .geo-slice-line { opacity: 0; animation: sliceScan 1.4s 0.5s ease-in-out forwards; }
    .geo-splash-title { color: #f8fafc !important; font-size: clamp(21px, 3vw, 28px) !important; font-weight: 900 !important; letter-spacing: 2.5px !important; margin-top: 14px !important; animation: titleFadeIn 0.7s ease-out !important; }
    .geo-splash-sub { color: #94a3b8 !important; font-size: clamp(10px, 1.3vw, 12px) !important; font-weight: 700 !important; letter-spacing: 2.2px !important; margin-top: 6px !important; animation: titleFadeIn 0.9s ease-out !important; }
    .geo-progress-bar { width: 180px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 3px; margin-top: 16px; overflow: hidden; }
    .geo-progress-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #38bdf8, #ef4444); animation: loadProgress 2.1s cubic-bezier(0.4, 0, 0.2, 1) forwards; }

    @keyframes meshPop { from { transform: scale(0.92); opacity: 0.1; } to { transform: scale(1); opacity: 1; } }
    @keyframes modelRise { from { transform: translateY(22px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    @keyframes rainFall { from { transform: translate(-8px, -12px); } to { transform: translate(8px, 12px); } }
    @keyframes waterRise { from { transform: scaleY(0.2) translateY(15px); opacity: 0; } to { transform: scaleY(1) translateY(0); opacity: 0.95; } }
    @keyframes waterPulse { from { transform: scaleY(1); } to { transform: scaleY(1.06); } }
    @keyframes flowMove { to { stroke-dashoffset: 0; } }
    @keyframes drawLine { to { stroke-dashoffset: 0; } }
    @keyframes shearPulse { from { stroke-width: 3.5; filter: drop-shadow(0 0 4px #ef4444); } to { stroke-width: 5.5; filter: drop-shadow(0 0 14px #ff0000); } }
    @keyframes sliceScan { 0% { opacity: 0; transform: translateX(0); } 20% { opacity: 0.9; } 80% { opacity: 0.9; } 100% { opacity: 0; transform: translateX(115px); } }
    @keyframes loadProgress { 0% { width: 0%; } 100% { width: 100%; } }
    @keyframes titleFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    html, body, [class*="css"] { color: var(--text-main) !important; }
    .stApp { background-color: var(--bg-main) !important; color: var(--text-main) !important; }
    [class*="immersive-translate"], .immersive-translate-target-wrapper { display: none !important; height: 0 !important; }
    #MainMenu, footer { visibility: hidden; }
    
    /* 緊湊型 App-Shell 頂部與底部安全邊距 (預留底部固定導航列 85px 空間) */
    .block-container {
        max-width: 1280px !important;
        width: 100% !important;
        padding-top: clamp(2.8rem, 4.5vh, 3.5rem) !important;
        padding-bottom: 95px !important;
        padding-left: clamp(8px, 2vw, 24px) !important;
        padding-right: clamp(8px, 2vw, 24px) !important;
        margin: 0 auto !important;
    }
    
    /* 頂部緊湊標題列 */
    .system-header-box { display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: flex-start !important; gap: 10px !important; margin: 0 0 8px 0 !important; width: 100% !important; }
    .app-top-logo { width: clamp(42px, 8vw, 60px) !important; height: auto !important; flex-shrink: 0 !important; filter: drop-shadow(0 3px 6px rgba(56, 189, 248, 0.25)) !important; }
    .title-wrapper { display: flex; flex-direction: row; align-items: center; justify-content: flex-start; flex-wrap: wrap; gap: 6px; width: 100%; }
    .system-title { font-size: clamp(17px, 2.6vw, 24px) !important; line-height: 1.2 !important; font-weight: 900 !important; letter-spacing: 0.5px; color: #4A6B82 !important; margin: 0 4px 0 0 !important; white-space: nowrap; }
    
    .manual-link-btn { display: inline-flex; align-items: center; justify-content: center; background-color: #e0f2fe; color: #0369a1 !important; font-size: clamp(10.5px, 1.1vw, 12.5px) !important; font-weight: 800 !important; text-decoration: none !important; padding: 3px 9px; border-radius: 14px; border: 1px solid #bae6fd; transition: all 0.15s ease; white-space: nowrap; }
    .manual-link-btn:hover { background-color: #bae6fd; color: #0c4a6e !important; transform: translateY(-1px); }

    .map-sub-title { font-size: clamp(15px, 2.2vw, 18px) !important; font-weight: 800 !important; color: #4A6B82 !important; text-align: center !important; margin: 0 0 6px 0 !important; }

    /* ===== 核心升級：手機/平板友善之大觸控按鈕與固定底部導航列 (Fixed Bottom App Dock) ===== */
    button { min-height: 44px !important; border-radius: 10px !important; transition: all 0.15s ease !important; }
    button p { font-size: clamp(14px, 1.8vw, 16px) !important; font-weight: 800 !important; line-height: 1.25 !important; }
    
    button[kind="secondary"] { background-color: var(--btn-sec-bg) !important; color: var(--btn-sec-text) !important; border: 1.5px solid var(--btn-sec-border) !important; box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important; }
    button[kind="secondary"]:hover { border-color: #4A6B82 !important; }
    button[kind="primary"] { background-color: #4A6B82 !important; border: 1.5px solid #3E5C76 !important; color: #ffffff !important; box-shadow: 0 4px 10px rgba(74, 107, 130, 0.35) !important; }

    /* 將主導航列釘選於螢幕最底部 (Thumb-Zone Dock) */
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999990 !important;
        background: var(--dock-bg) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border-top: 1.5px solid var(--dock-border) !important;
        padding: 6px clamp(6px, 2vw, 24px) calc(6px + env(safe-area-inset-bottom, 0px)) clamp(6px, 2vw, 24px) !important;
        margin: 0 !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: clamp(4px, 1vw, 10px) !important;
        box-shadow: 0 -4px 18px rgba(0, 0, 0, 0.12) !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) > div {
        flex: 1 1 20% !important;
        min-width: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) button {
        height: 54px !important;
        min-height: 54px !important;
        padding: 4px 2px !important;
        border-radius: 12px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) button p {
        font-size: clamp(11.5px, 1.5vw, 14px) !important;
        white-space: pre-line !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }

    /* 6格分級快篩膠囊列：允許手機端水平強制不換行或緊湊網格 */
    div[data-testid="stHorizontalBlock"]:has(button[key^="badge_btn_"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="badge_btn_"]) > div {
        flex: 1 1 calc(33.33% - 6px) !important;
        min-width: 90px !important;
    }
    @media (min-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(button[key^="badge_btn_"]) > div {
            flex: 1 1 15% !important;
        }
    }

    .route-green-text { font-size: 16.5px !important; color: #059669 !important; font-weight: 900 !important; }
    .detail-green-text { font-size: 20px !important; color: #059669 !important; font-weight: 900 !important; }

    html body .stApp div[data-baseweb="select"], html body .stApp div[data-testid="stTextInput"] div[data-baseweb="base-input"], html body .stApp div[data-testid="stDateInput"] div[data-baseweb="input"], html body .stApp div[data-baseweb="textarea"] textarea { background-color: var(--input-bg) !important; border: 1px solid var(--input-border) !important; border-radius: 8px !important; }
    html body .stApp input[type="text"], html body .stApp textarea { color: #0f172a !important; -webkit-text-fill-color: #0f172a !important; font-size: 15px !important; font-weight: 600 !important; }

    .app-card { background: var(--card-bg) !important; border-radius: 12px; padding: clamp(10px, 1.8vw, 15px); margin-bottom: 8px; border: 1px solid var(--card-border) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
    .detail-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--card-border) !important; font-size: 14px; line-height: 1.4; color: var(--text-main) !important; }
    .detail-label { color: var(--text-muted) !important; font-weight: 600; width: 42%; }
    .detail-value { font-weight: 700; width: 58%; text-align: right; word-break: break-all; color: var(--text-main) !important; }
    
    .badge { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: 13px; font-weight: 800; color: #ffffff !important; }
    .badge-A { background-color: #c05646; } .badge-B { background-color: #d9822b; } .badge-Cplus { background-color: #7c3aed; } .badge-C { background-color: #4A6B82; } .badge-D { background-color: #52796f; } .badge-其他 { background-color: #64748b; }

    .embed-map-box { border-radius: 12px; overflow: hidden; border: 1px solid var(--card-border) !important; margin: 6px 0; }

    .app-official-footer-bottom { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; margin-top: 16px !important; margin-bottom: 12px !important; padding: 6px 10px !important; width: 100% !important; }
    .footer-title-row { display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: center !important; gap: 8px !important; margin-bottom: 4px !important; flex-wrap: nowrap !important; }
    .app-official-logo { height: clamp(20px, 4vw, 28px) !important; width: auto !important; flex-shrink: 0 !important; }
    .app-official-text { font-size: clamp(11px, 2.8vw, 15px) !important; font-weight: 900 !important; color: var(--footer-text) !important; white-space: nowrap !important; }
    .app-official-source { font-size: 11.5px !important; font-weight: 600 !important; color: var(--text-muted) !important; line-height: 1.45 !important; text-align: center !important; }
    .app-official-source a { color: var(--link-color) !important; text-decoration: underline !important; font-weight: 700 !important; }
</style>
"""
    style_part = css_template.replace("__THEME_VARS__", theme_vars)
    return (splash_overlay_html if show_splash else "") + style_part

def render_top_logo() -> str:
    manual_link_1 = '<span style="color:#ef4444; font-size:11px; font-weight:bold;">⚠️ 缺教學手冊PDF</span>'
    manual_link_2 = '<span style="color:#ef4444; font-size:11px; font-weight:bold;">⚠️ 缺巡檢機制PDF</span>'
    
    try:
        pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        
        for f in pdf_files:
            if '教學手冊' in f or ('手冊' in f and '懶人包' not in f and '路巡' not in f):
                with open(f, "rb") as pdf_file:
                    b64_pdf = base64.b64encode(pdf_file.read()).decode()
                href = f"data:application/pdf;base64,{b64_pdf}"
                manual_link_1 = f'<a href="{href}" download="{f}" target="_blank" class="manual-link-btn">📘 教學手冊</a>'
                break

        for f in pdf_files:
            if '懶人包' in f or '路巡' in f or '巡檢' in f:
                with open(f, "rb") as pdf_file:
                    b64_pdf = base64.b64encode(pdf_file.read()).decode()
                href = f"data:application/pdf;base64,{b64_pdf}"
                manual_link_2 = f'<a href="{href}" download="{f}" target="_blank" class="manual-link-btn">📘 115年巡檢機制</a>'
                break
    except Exception as e:
        manual_link_1 = f'<span style="color:#ef4444; font-size:11px;">⚠️ PDF 異常: {e}</span>'
        manual_link_2 = ""

    return f"""
    <div class="system-header-box notranslate" translate="no">
      <svg class="app-top-logo" viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gB" x1="60" y1="150" x2="340" y2="240" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#52796f" stop-opacity="0.95"/><stop offset="100%" stop-color="#2d4a43" stop-opacity="0.98"/></linearGradient>
          <linearGradient id="gP" x1="160" y1="70" x2="200" y2="210" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#4A6B82" stop-opacity="0.92"/><stop offset="100%" stop-color="#1e293b" stop-opacity="0.98"/></linearGradient>
          <linearGradient id="gS" x1="110" y1="95" x2="280" y2="180" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#38bdf8" stop-opacity="0.85"/><stop offset="100%" stop-color="#0284c7" stop-opacity="0.95"/></linearGradient>
          <filter id="dS" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#000000" flood-opacity="0.18"/></filter>
        </defs>
        <g filter="url(#dS)">
          <g stroke="#94a3b8" stroke-width="1.1" stroke-opacity="0.65"><path d="M40 190 L200 265 L360 190 L200 115 Z" fill="rgba(241, 245, 249, 0.45)"/><path d="M80 171 L240 246"/><path d="M120 153 L280 228"/><path d="M160 134 L320 209"/><path d="M120 228 L280 153"/><path d="M80 209 L240 134"/><path d="M160 246 L320 171"/></g>
          <path d="M20 198 L380 198" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="5 4" stroke-opacity="0.85"/>
          <path d="M60 180 L200 245 L340 180 L340 148 L200 212 L60 148 Z" fill="url(#gB)" stroke="#3f5e56" stroke-width="1.8"/>
          <path d="M60 148 L200 212 L340 148 L288 75 L175 75 L60 148 Z" fill="url(#gP)" stroke="#2b3e4f" stroke-width="2.0"/>
          <path d="M115 135 Q185 180 268 135 L280 98 Q195 130 158 98 Z" fill="url(#gS)" stroke="#0284c7" stroke-width="2.2"/>
          <path d="M175 75 L288 75 L340 148" stroke="#ef4444" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M110 132 Q190 176 276 132" stroke="#dc2626" stroke-width="3.8" stroke-linecap="round"/>
          <path d="M100 144 Q190 194 280 140" stroke="#38bdf8" stroke-width="3.2" stroke-linecap="round"/>
        </g>
      </svg>
      <div class="title-wrapper">
        <div class="system-title">南澳邊坡全生命週期資料庫</div>
        {manual_link_1}
        {manual_link_2}
      </div>
    </div>
    """

def render_footer() -> str:
    logo_svg = '<svg class="app-official-logo notranslate" viewBox="0 0 818 138" fill="none" xmlns="http://www.w3.org/2000/svg" translate="no"><path d="M409 69C409 30.89 439.89 0 478 0C516.11 0 547 30.89 547 69C547 107.11 516.11 138 478 138C439.89 138 409 107.11 409 69Z" fill="#E62117"/><path d="M478 14C447.62 14 423 38.62 423 69C423 99.38 447.62 124 478 124C508.38 124 533 99.38 533 69C533 38.62 508.38 14 478 14ZM478 110C455.36 110 437 91.64 437 69C437 46.36 455.36 28 478 28C500.64 28 519 46.36 519 69C519 91.64 500.64 110 478 110Z" fill="white"/><path d="M0 24L380 24C395 24 402 36 388 48L70 48C50 48 30 40 0 24Z" fill="#1E50A2"/><path d="M818 24L438 24C423 24 416 36 430 48L748 48C768 48 788 40 818 24Z" fill="#1E50A2"/><path d="M60 56L370 56C382 56 388 66 376 76L120 76C100 76 80 70 60 56Z" fill="#0080FF"/><path d="M758 56L448 56C436 56 430 66 442 76L698 76C718 76 738 70 758 56Z" fill="#0080FF"/><path d="M120 86L360 86C370 86 375 94 365 102L170 102C150 102 135 96 120 86Z" fill="#00BFFF"/><path d="M698 86L458 86C448 86 443 94 453 102L648 102C668 102 683 96 698 86Z" fill="#00BFFF"/></svg>'
    
    logo_render = logo_svg
    for possible_logo in ["LOGO.webp", "LOGO.png", "logo.png", "logo.webp"]:
        if os.path.exists(possible_logo):
            try:
                with open(possible_logo, "rb") as f:
                    b64_val = base64.b64encode(f.read()).decode()
                    ext = "webp" if possible_logo.endswith("webp") else "png"
                    logo_render = f'<img class="app-official-logo notranslate" src="data:image/{ext};base64,{b64_val}" alt="公路局LOGO" translate="no" />'
                    break
            except Exception:
                pass

    footer_html = (
        "<div class='app-official-footer-bottom notranslate' translate='no'>"
        "  <div class='footer-title-row'>"
        f"    {logo_render}"
        "    <span class='app-official-text notranslate' translate='no'>交通部公路局東區養護工程分局南澳工務段</span>"
        "  </div>"
        "  <div class='app-official-source notranslate' translate='no'>"
        "    資料來源：<a href='https://slope.thb.gov.tw/thbslope' target='_blank'>邊坡全生命週期管理系統</a> ｜ "
        "    <a href='https://eroad.thb.gov.tw/DGOHForeground/Map/Index' target='_blank'>圖說公路平台</a>"
        "  </div>"
        "</div>"
    )
    return footer_html