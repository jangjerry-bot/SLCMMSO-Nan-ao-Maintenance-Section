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
            --card-border: #e2e8f0;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --input-text: #0f172a;
            --btn-sec-bg: #ffffff;
            --btn-sec-text: #1e293b;
            --btn-sec-border: #cbd5e1;
            --dock-bg: #ffffff;
            --dock-border: #e2e8f0;
            --dock-inactive: #94a3b8;
            --dock-active: #f97316;
            --topbar-bg: #1b2a47;
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
            --dock-bg: #111827;
            --dock-border: #1f2937;
            --dock-inactive: #64748b;
            --dock-active: #fb923c;
            --topbar-bg: #0f172a;
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

    #geo-splash-overlay { position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important; background: radial-gradient(circle at center, #111827 0%, #050811 100%) !important; z-index: 99999999 !important; display: flex !important; justify-content: center !important; align-items: center !important; pointer-events: none !important; animation: splashDismiss 0.5s cubic-bezier(0.4, 0, 0.2, 1) 1.8s forwards !important; }
    @keyframes splashDismiss { 0% { opacity: 1; transform: scale(1); } 99% { opacity: 0; transform: scale(1.03); } 100% { opacity: 0; visibility: hidden; display: none !important; } }
    .geo-splash-center { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; text-align: center !important; padding: 20px !important; }
    .geo-hud-badge { font-family: monospace !important; font-size: 11px !important; color: #38bdf8 !important; background: rgba(56, 189, 248, 0.1) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important; padding: 4px 12px !important; border-radius: 20px !important; letter-spacing: 2px !important; margin-bottom: 10px !important; }
    .geo-splash-svg { width: clamp(250px, 45vw, 360px) !important; height: auto !important; filter: drop-shadow(0 18px 32px rgba(0, 0, 0, 0.7)) !important; }
    .geo-base-layer { animation: modelRise 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; transform-box: fill-box; }
    .geo-slope-prism { opacity: 0; animation: modelRise 0.5s 0.1s cubic-bezier(0.16, 1, 0.3, 1) forwards; transform-box: fill-box; }
    .geo-rain-lines { animation: rainFall 0.8s linear infinite; }
    .geo-seepage-wave { opacity: 0; animation: waterRise 0.7s 0.2s ease-out forwards; transform-origin: bottom center; transform-box: fill-box; }
    .geo-red-crest { stroke-dasharray: 220; stroke-dashoffset: 220; animation: drawLine 0.7s 0.3s ease-out forwards; }
    .geo-red-shear { stroke-dasharray: 240; stroke-dashoffset: 240; animation: drawLine 0.8s 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
    .geo-splash-title { color: #f8fafc !important; font-size: clamp(20px, 3vw, 26px) !important; font-weight: 900 !important; letter-spacing: 2.5px !important; margin-top: 12px !important; }
    .geo-splash-sub { color: #94a3b8 !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 2px !important; margin-top: 4px !important; }
    .geo-progress-bar { width: 160px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 3px; margin-top: 14px; overflow: hidden; }
    .geo-progress-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #38bdf8, #f97316); animation: loadProgress 1.7s cubic-bezier(0.4, 0, 0.2, 1) forwards; }

    @keyframes modelRise { from { transform: translateY(18px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    @keyframes rainFall { from { transform: translate(-6px, -10px); } to { transform: translate(6px, 10px); } }
    @keyframes waterRise { from { transform: scaleY(0.2) translateY(12px); opacity: 0; } to { transform: scaleY(1) translateY(0); opacity: 0.95; } }
    @keyframes drawLine { to { stroke-dashoffset: 0; } }
    @keyframes loadProgress { 0% { width: 0%; } 100% { width: 100%; } }

    html, body, [class*="css"] { color: var(--text-main) !important; }
    .stApp { background-color: var(--bg-main) !important; color: var(--text-main) !important; }
    [class*="immersive-translate"], .immersive-translate-target-wrapper { display: none !important; height: 0 !important; }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden !important; height: 0 !important; }
    
    /* 預留頂部深藍 App Bar (54px) 與底部白底橘線導航列 (76px) 的安全空間 */
    .block-container {
        max-width: 1100px !important;
        width: 100% !important;
        padding-top: 62px !important;
        padding-bottom: 88px !important;
        padding-left: clamp(8px, 2vw, 20px) !important;
        padding-right: clamp(8px, 2vw, 20px) !important;
        margin: 0 auto !important;
    }

    /* ===== 1. 截圖風格：頂部固定深海軍藍 App Bar (Top App Bar) ===== */
    .mobile-app-topbar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 52px !important;
        background-color: var(--topbar-bg) !important;
        color: #ffffff !important;
        z-index: 999980 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 14px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.22) !important;
    }
    .topbar-left { display: flex; align-items: center; gap: 8px; }
    .topbar-title {
        font-size: clamp(16px, 2.5vw, 19px) !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: 1px !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    .topbar-right { display: flex; align-items: center; gap: 6px; }
    .topbar-pill-btn {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.14);
        color: #f8fafc !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        padding: 4px 9px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        white-space: nowrap;
        transition: background 0.15s;
    }
    .topbar-pill-btn:hover { background: rgba(255, 255, 255, 0.26); }

    /* ===== 2. 截圖風格：完美釘選於手機畫面最下方的「白底 + 頂部橘線導航列」 ===== */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor),
    div.element-container:has(#bottom-nav-anchor) {
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
    }

    /* 透過 #bottom-nav-anchor 強制鎖定緊隨其後的 stHorizontalBlock 釘在畫面底部 */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"],
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        z-index: 999995 !important;
        background-color: var(--dock-bg) !important;
        border-top: 1px solid var(--dock-border) !important;
        padding: 0 clamp(2px, 3vw, 40px) env(safe-area-inset-bottom, 4px) clamp(2px, 3vw, 40px) !important;
        margin: 0 !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        justify-content: space-around !important;
        gap: 0px !important;
        box-shadow: 0 -3px 14px rgba(0, 0, 0, 0.08) !important;
    }

    /* 強制手機端 5 個按鈕絕對水平並排 (絕不垂直堆疊！) */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 20% !important;
        width: 20% !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 底部導航按鈕本體：去除外框，模擬原生 iOS/Android Tab Bar */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button,
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        height: 60px !important;
        min-height: 60px !important;
        background: transparent !important;
        border: none !important;
        border-top: 3.5px solid transparent !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 4px 0 2px 0 !important;
        margin: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.12s ease !important;
    }

    /* 未選中狀態 (灰色圖示與文字) */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button[kind="secondary"] p,
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button[kind="secondary"] p {
        color: var(--dock-inactive) !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        white-space: pre-line !important;
        text-align: center !important;
        margin: 0 !important;
        filter: grayscale(100%) opacity(0.72) !important;
    }

    /* 選中狀態 (完全比照截圖：頂部亮橘色橫條 + 橘色文字與圖示！) */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button[kind="primary"],
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: linear-gradient(180deg, rgba(249, 115, 22, 0.08) 0%, transparent 100%) !important;
        border-top: 3.5px solid var(--dock-active) !important;
    }
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button[kind="primary"] p,
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button[kind="primary"] p {
        color: var(--dock-active) !important;
        font-size: 12px !important;
        font-weight: 900 !important;
        line-height: 1.25 !important;
        white-space: pre-line !important;
        text-align: center !important;
        margin: 0 !important;
        filter: none !important;
    }

    /* 將第一行 Emoji 圖示放大為 20px，第二行文字維持 12px */
    div[data-testid="stElementContainer"]:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button p::first-line,
    div.element-container:has(#bottom-nav-anchor) + div[data-testid="stHorizontalBlock"] button p::first-line {
        font-size: 20px !important;
        line-height: 24px !important;
    }

    /* ===== 3. 截圖風格：懸浮圓角搜尋框與一般內容按鈕 ===== */
    .floating-search-bar {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 10px 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--card-border);
        margin-bottom: 10px;
    }

    /* 6格分級快篩按鈕：手機端 3x2 網格、平板 6x1 並排，超大好按 */
    div[data-testid="stElementContainer"]:has(#grade-pills-anchor) + div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        margin-top: 4px !important;
    }
    div[data-testid="stElementContainer"]:has(#grade-pills-anchor) + div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 calc(33.33% - 6px) !important;
        min-width: 88px !important;
    }
    @media (min-width: 768px) {
        div[data-testid="stElementContainer"]:has(#grade-pills-anchor) + div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 15% !important;
        }
    }

    /* 一般業務按鈕樣式 */
    button[kind="secondary"] { background-color: var(--btn-sec-bg) !important; color: var(--btn-sec-text) !important; border: 1.5px solid var(--btn-sec-border) !important; font-weight: 800 !important; border-radius: 10px !important; min-height: 42px !important; }
    button[kind="primary"] { background-color: #4A6B82 !important; border: 1.5px solid #3E5C76 !important; color: #ffffff !important; font-weight: 800 !important; border-radius: 10px !important; min-height: 42px !important; }

    .route-green-text { font-size: 16.5px !important; color: #059669 !important; font-weight: 900 !important; }
    .detail-green-text { font-size: 19px !important; color: #059669 !important; font-weight: 900 !important; }

    html body .stApp div[data-baseweb="select"], html body .stApp div[data-testid="stTextInput"] div[data-baseweb="base-input"], html body .stApp div[data-testid="stDateInput"] div[data-baseweb="input"], html body .stApp div[data-baseweb="textarea"] textarea { background-color: var(--input-bg) !important; border: 1px solid var(--input-border) !important; border-radius: 10px !important; }
    html body .stApp input[type="text"], html body .stApp textarea { color: #0f172a !important; -webkit-text-fill-color: #0f172a !important; font-size: 15px !important; font-weight: 600 !important; }

    .app-card { background: var(--card-bg) !important; border-radius: 12px; padding: 12px 14px; margin-bottom: 8px; border: 1px solid var(--card-border) !important; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
    .detail-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--card-border) !important; font-size: 14px; line-height: 1.4; color: var(--text-main) !important; }
    .detail-label { color: var(--text-muted) !important; font-weight: 600; width: 42%; }
    .detail-value { font-weight: 700; width: 58%; text-align: right; word-break: break-all; color: var(--text-main) !important; }
    
    .badge { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: 13px; font-weight: 800; color: #ffffff !important; }
    .badge-A { background-color: #c05646; } .badge-B { background-color: #d9822b; } .badge-Cplus { background-color: #7c3aed; } .badge-C { background-color: #4A6B82; } .badge-D { background-color: #52796f; } .badge-其他 { background-color: #64748b; }

    .embed-map-box { border-radius: 12px; overflow: hidden; border: 1px solid var(--card-border) !important; margin: 6px 0; }
    .coord-status-bar { background: rgba(15, 23, 42, 0.82); color: #f8fafc; font-family: monospace; font-size: 12.5px; font-weight: 700; padding: 5px 12px; border-radius: 6px; text-align: right; margin-top: -6px; margin-bottom: 6px; }

    .app-official-footer-bottom { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; margin-top: 10px !important; margin-bottom: 6px !important; padding: 4px 8px !important; width: 100% !important; }
    .footer-title-row { display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: center !important; gap: 6px !important; margin-bottom: 2px !important; flex-wrap: nowrap !important; }
    .app-official-logo { height: 20px !important; width: auto !important; flex-shrink: 0 !important; }
    .app-official-text { font-size: clamp(11px, 2.5vw, 13.5px) !important; font-weight: 900 !important; color: var(--footer-text) !important; white-space: nowrap !important; }
    .app-official-source { font-size: 11px !important; font-weight: 600 !important; color: var(--text-muted) !important; text-align: center !important; }
    .app-official-source a { color: var(--link-color) !important; text-decoration: underline !important; }
</style>
"""
    style_part = css_template.replace("__THEME_VARS__", theme_vars)
    return (splash_overlay_html if show_splash else "") + style_part

def render_top_logo(active_title: str = "南澳邊坡防災圖台") -> str:
    manual_link_1 = ""
    manual_link_2 = ""
    try:
        pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        for f in pdf_files:
            if '教學手冊' in f or ('手冊' in f and '懶人包' not in f and '路巡' not in f):
                with open(f, "rb") as pdf_file:
                    b64_pdf = base64.b64encode(pdf_file.read()).decode()
                manual_link_1 = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{f}" target="_blank" class="topbar-pill-btn">📘 手冊</a>'
                break
        for f in pdf_files:
            if '懶人包' in f or '路巡' in f or '巡檢' in f:
                with open(f, "rb") as pdf_file:
                    b64_pdf = base64.b64encode(pdf_file.read()).decode()
                manual_link_2 = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{f}" target="_blank" class="topbar-pill-btn">📘 115巡檢</a>'
                break
    except Exception:
        pass

    return f"""
    <div class="mobile-app-topbar notranslate" translate="no">
      <div class="topbar-left">
        <span style="font-size:20px; line-height:1;">☰</span>
        <span class="topbar-title">{active_title}</span>
      </div>
      <div class="topbar-right">
        {manual_link_1}
        {manual_link_2}
      </div>
    </div>
    """

def render_footer() -> str:
    return (
        "<div class='app-official-footer-bottom notranslate' translate='no'>"
        "  <div class='footer-title-row'>"
        "    <span class='app-official-text'>交通部公路局東區養護工程分局南澳工務段</span>"
        "  </div>"
        "</div>"
    )