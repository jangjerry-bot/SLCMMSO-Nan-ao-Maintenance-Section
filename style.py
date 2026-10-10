# style.py
import os
import base64

def get_theme_css(is_light: bool) -> str:
    if is_light:
        theme_vars = """
            --bg-main: #f8fafc;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --card-bg: #ffffff;
            --card-border: #cbd5e1;
            --input-bg: #ffffff;
            --input-border: #94a3b8;
            --input-text: #0f172a;
            --btn-sec-bg: #f1f5f9;
            --btn-sec-text: #0f172a;
            --btn-sec-border: #cbd5e1;
            --footer-text: #4A6B82;
            --link-color: #2563eb;
        """
    else:
        theme_vars = """
            --bg-main: #0b0f19;
            --text-main: #f8fafc;
            --text-muted: #64748b;
            --card-bg: rgba(255, 255, 255, 0.04);
            --card-border: rgba(255, 255, 255, 0.12);
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --input-text: #64748b;
            --btn-sec-bg: #1e293b;
            --btn-sec-text: #f1f5f9;
            --btn-sec-border: #334155;
            --footer-text: #4A6B82;
            --link-color: #60a5fa;
        """

    splash_overlay_html = (
        '<div id="geo-splash-overlay">'
        '<div class="geo-splash-center">'
        '<svg class="geo-splash-svg" viewBox="0 0 340 220" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<defs>'
        '<linearGradient id="splashGradBase" x1="50" y1="115" x2="290" y2="195" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#52796f" stop-opacity="0.9"/>'
        '<stop offset="1" stop-color="#2d4a43" stop-opacity="0.95"/>'
        '</linearGradient>'
        '<linearGradient id="splashGradPrism" x1="150" y1="55" x2="170" y2="168" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#4A6B82" stop-opacity="0.88"/>'
        '<stop offset="1" stop-color="#1e293b" stop-opacity="0.95"/>'
        '</linearGradient>'
        '<linearGradient id="splashGradSeepage" x1="95" y1="75" x2="235" y2="142" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#38bdf8" stop-opacity="0.8"/>'
        '<stop offset="1" stop-color="#0284c7" stop-opacity="0.95"/>'
        '</linearGradient>'
        '</defs>'
        '<g class="geo-mesh-grid" stroke="#64748b" stroke-width="0.9" stroke-opacity="0.45">'
        '<path d="M30 150 L170 212 L310 150 L170 88 Z" fill="rgba(241, 245, 249, 0.25)"/>'
        '<path d="M65 134 L205 197"/><path d="M100 119 L240 181"/><path d="M135 103 L275 166"/>'
        '<path d="M100 181 L240 119"/><path d="M65 166 L205 103"/><path d="M135 197 L275 134"/>'
        '</g>'
        '<path class="geo-red-axis" d="M15 156 L325 156" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="0.75"/>'
        '<path class="geo-base-layer" d="M50 142 L170 195 L290 142 L290 115 L170 168 L50 115 Z" fill="url(#splashGradBase)" stroke="#52796f" stroke-width="1.6"/>'
        '<path class="geo-slope-prism" d="M50 115 L170 168 L290 115 L245 55 L150 55 L50 115 Z" fill="url(#splashGradPrism)" stroke="#3E5C76" stroke-width="1.8"/>'
        '<path class="geo-seepage-mass" d="M95 105 Q155 142 225 105 L235 75 Q165 102 135 75 Z" fill="url(#splashGradSeepage)" stroke="#0284c7" stroke-width="2"/>'
        '<path class="geo-red-crest" d="M150 55 L245 55 L290 115" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round"/>'
        '<path class="geo-red-shear" d="M90 102 Q160 138 232 102" stroke="#dc2626" stroke-width="3.2" stroke-linecap="round"/>'
        '<path class="geo-slip-stream" d="M85 112 Q158 152 235 108" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>'
        '<path class="geo-slip-stream-sub" d="M110 90 Q160 122 210 90" stroke="#0ea5e9" stroke-width="1.8" stroke-linecap="round"/>'
        '</svg>'
        '<div class="geo-splash-title">南澳邊坡全生命週期資料庫</div>'
        '<div class="geo-splash-sub">3D SLOPE LIFECYCLE MANAGEMENT SYSTEM</div>'
        '</div>'
        '</div>'
    )

    css_template = """
<style>
    :root {
        __THEME_VARS__
    }

    #geo-splash-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: #0b0f19 !important;
        z-index: 99999999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        pointer-events: none !important;
        animation: splashDismiss 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2.4s forwards !important;
    }
    @keyframes splashDismiss {
        0% { opacity: 1; visibility: visible; }
        99% { opacity: 0; visibility: visible; }
        100% { opacity: 0; visibility: hidden; display: none !important; }
    }

    .geo-splash-center {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 20px !important;
    }
    .geo-splash-svg {
        width: clamp(260px, 46vw, 380px) !important;
        height: auto !important;
        filter: drop-shadow(0 14px 28px rgba(0, 0, 0, 0.55)) !important;
    }
    .geo-splash-title {
        color: #f8fafc !important;
        font-size: clamp(20px, 2.8vw, 26px) !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        margin-top: 18px !important;
        animation: titleFadeIn 0.8s ease-out !important;
    }
    .geo-splash-sub {
        color: #38bdf8 !important;
        font-size: clamp(10.5px, 1.4vw, 12.5px) !important;
        font-weight: 700 !important;
        letter-spacing: 2.4px !important;
        margin-top: 6px !important;
        animation: titleFadeIn 1.0s ease-out !important;
    }

    .geo-mesh-grid { animation: meshPop 0.8s ease-out; }
    .geo-red-axis { animation: meshPop 0.6s ease-out; }
    .geo-base-layer, .geo-slope-prism, .geo-seepage-mass { animation: modelRise 0.8s cubic-bezier(0.16, 1, 0.3, 1); }

    .geo-red-crest {
        stroke-dasharray: 200;
        stroke-dashoffset: 200;
        animation: drawLine 1.1s 0.1s ease-in-out forwards;
        filter: drop-shadow(0 0 6px #ef4444);
    }
    .geo-red-shear {
        stroke-dasharray: 220;
        stroke-dashoffset: 220;
        animation: drawLine 1.1s 0.2s ease-in-out forwards;
        filter: drop-shadow(0 0 8px #dc2626);
    }
    .geo-slip-stream {
        stroke-dasharray: 260;
        stroke-dashoffset: 260;
        animation: drawLine 1.2s 0.3s ease-in-out forwards;
        filter: drop-shadow(0 0 7px #38bdf8);
    }
    .geo-slip-stream-sub {
        stroke-dasharray: 180;
        stroke-dashoffset: 180;
        animation: drawLine 1.0s 0.4s ease-in-out forwards;
        filter: drop-shadow(0 0 5px #0ea5e9);
    }

    @keyframes drawLine { to { stroke-dashoffset: 0; } }
    @keyframes modelRise { from { transform: translateY(12px); opacity: 0.2; } to { transform: translateY(0); opacity: 1; } }
    @keyframes meshPop { from { transform: scale(0.92); opacity: 0.1; } to { transform: scale(1); opacity: 1; } }
    @keyframes titleFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    html, body, [class*="css"] {
        color: var(--text-main) !important;
    }

    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-main) !important;
    }

    [class*="immersive-translate"], .immersive-translate-target-wrapper { display: none !important; height: 0 !important; }
    #MainMenu, footer { visibility: hidden; }
    
    .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding-top: clamp(2rem, 3.5vh, 3.5rem) !important;
        padding-bottom: clamp(2.5rem, 4vh, 3.5rem) !important;
        padding-left: clamp(10px, 2.5vw, 32px) !important;
        padding-right: clamp(10px, 2.5vw, 32px) !important;
        margin: 0 auto !important;
    }
    
    /* 頂部 LOGO 與標題水平並排 */
    .system-header-box {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: clamp(8px, 1.2vw, 14px) !important;
        margin-top: 2px !important;
        margin-bottom: 12px !important;
        width: 100% !important;
    }
    .app-top-logo {
        width: clamp(38px, 4.2vw, 52px) !important;
        height: auto !important;
        margin-bottom: 0px !important;
        flex-shrink: 0 !important;
        filter: drop-shadow(0 3px 8px rgba(56, 189, 248, 0.25)) !important;
    }
    .system-title {
        font-size: clamp(20px, 2.8vw, 28px) !important;
        line-height: 1.3 !important;
        font-weight: 900 !important;
        letter-spacing: 1.2px;
        color: #4A6B82 !important;
        text-align: left !important;
        display: inline-block !important;
        margin: 0 !important;
    }

    .map-sub-title {
        font-size: clamp(16px, 2.4vw, 20px) !important;
        line-height: 1.3 !important;
        font-weight: 800 !important;
        letter-spacing: 0.8px;
        color: #4A6B82 !important;
        text-align: center !important;
        display: block !important;
        width: 100%;
        margin-top: 0px !important;
        margin-bottom: 6px !important;
    }

    html body .stApp div[data-testid^="st"] label,
    html body .stApp div[data-testid^="st"] label p,
    html body .stApp div[data-testid^="st"] label span {
        color: var(--text-main) !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    html body .stApp div[data-testid="stSelectbox"] div[data-baseweb="select"],
    html body .stApp div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    html body .stApp div[data-testid="stSelectbox"] div[role="combobox"],
    html body .stApp div[data-baseweb="select"],
    html body .stApp div[data-baseweb="select"] > div {
        background-color: var(--input-bg) !important;
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }

    html body .stApp div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
    html body .stApp div[data-baseweb="select"] * {
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        fill: var(--text-muted) !important;
    }

    html body .stApp div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    html body .stApp div[data-testid="stTextInput"] div[data-baseweb="input"],
    html body .stApp div[data-baseweb="base-input"],
    html body .stApp div[data-baseweb="input"] {
        background-color: var(--input-bg) !important;
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }
    html body .stApp div[data-testid="stTextInput"] input,
    html body .stApp div[data-baseweb="input"] input,
    html body .stApp input[type="text"] {
        background-color: transparent !important;
        background: transparent !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
    }
    html body .stApp input::placeholder,
    html body .stApp textarea::placeholder {
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="popover"],
    ul[data-baseweb="menu"],
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
    }
    li[data-baseweb="menu-item"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background-color: #f1f5f9 !important;
    }

    html body .stApp input:disabled,
    html body .stApp div[data-baseweb="input"] input:disabled {
        background-color: var(--input-bg) !important;
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        opacity: 0.95 !important;
        cursor: not-allowed;
    }

    html body .stApp div[data-testid="stDateInput"] div[data-baseweb="input"] {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }
    html body .stApp div[data-testid="stDateInput"] input {
        background-color: transparent !important;
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }

    html body .stApp div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    html body .stApp div[data-baseweb="textarea"] textarea {
        background-color: var(--input-bg) !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }

    html body .stApp div[data-testid="stRadio"] label,
    html body .stApp div[data-testid="stRadio"] p {
        color: var(--text-main) !important;
        font-weight: 700 !important;
        font-size: clamp(13px, 1.8vw, 15px) !important;
    }

    div[data-testid="stExpander"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: var(--card-bg) !important;
        color: var(--text-main) !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: var(--btn-sec-bg) !important;
    }
    div[data-testid="stExpander"] summary * {
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }

    .app-card {
        background: var(--card-bg) !important;
        border-radius: 12px;
        padding: clamp(12px, 2vw, 18px);
        margin-bottom: 12px;
        border: 1px solid var(--card-border) !important;
    }
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid var(--card-border) !important;
        font-size: clamp(13px, 1.7vw, 14.5px);
        line-height: 1.45;
        color: var(--text-main) !important;
    }
    .detail-label { color: var(--text-muted) !important; font-weight: 600; width: 40%; }
    .detail-value { font-weight: 600; width: 60%; text-align: right; word-break: break-all; color: var(--text-main) !important; }

    .badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: clamp(11px, 1.4vw, 12.5px);
        font-weight: 700;
        color: #ffffff !important;
    }
    .badge-A { background-color: #c05646; }
    .badge-B { background-color: #d9822b; }
    .badge-C { background-color: #4A6B82; }
    .badge-D { background-color: #52796f; }
    .badge-其他 { background-color: #64748b; }

    .embed-map-box {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--card-border) !important;
        margin: 12px 0;
    }

    button[kind="secondary"] {
        background-color: var(--btn-sec-bg) !important;
        color: var(--btn-sec-text) !important;
        border: 1px solid var(--btn-sec-border) !important;
        font-weight: 700 !important;
    }
    button[kind="primary"] {
        background-color: #4A6B82 !important;
        border-color: #3E5C76 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    button[key="badge_btn_A"] { background-color: #c05646 !important; border: 1px solid #991b1b !important; color: #ffffff !important; font-weight: 800 !important; }
    button[key="badge_btn_B"] { background-color: #d9822b !important; border: 1px solid #c2410c !important; color: #ffffff !important; font-weight: 800 !important; }
    button[key="badge_btn_C"] { background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; color: #ffffff !important; font-weight: 800 !important; }
    button[key="badge_btn_D"] { background-color: #059669 !important; border: 1px solid #047857 !important; color: #ffffff !important; font-weight: 800 !important; }
    button[key="badge_btn_其他"] { background-color: #475569 !important; border: 1px solid #334155 !important; color: #ffffff !important; font-weight: 800 !important; }

    /* 頂部 5 大功能導航按鈕容器 */
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: clamp(4px, 1vw, 10px) !important;
        width: 100% !important;
        margin-top: 4px !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) > div {
        flex: 1 1 20% !important;
        min-width: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) button {
        padding-left: clamp(2px, 0.5vw, 6px) !important;
        padding-right: clamp(2px, 0.5vw, 6px) !important;
        font-size: clamp(12px, 1.35vw, 15px) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        height: clamp(38px, 4.5vh, 44px) !important;
    }

    /* 最底端頁尾：無邊框極簡自然懸浮 */
    .app-official-footer-bottom {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 22px !important;
        margin-bottom: 26px !important;
        padding: 8px 12px !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .footer-title-row {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        width: 100% !important;
        text-align: center !important;
    }
    .app-official-logo { 
        height: clamp(28px, 4.0vw, 36px) !important; 
        width: auto !important; 
        display: inline-block !important; 
        vertical-align: middle !important; 
    }
    .app-official-text {
        font-size: clamp(13.5px, 1.8vw, 16.5px) !important;
        font-weight: 800 !important;
        color: var(--footer-text) !important;
        letter-spacing: 0.5px !important;
        line-height: 1.4 !important;
        text-align: center !important;
    }
    .app-official-source {
        font-size: clamp(11px, 1.3vw, 12.5px) !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        margin-top: 6px !important;
        letter-spacing: 0.3px !important;
        text-align: center !important;
        line-height: 1.4 !important;
        width: 100% !important;
        word-break: break-word !important;
    }
    .app-official-source a {
        color: var(--link-color) !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
        margin-left: 3px !important;
    }

    @media (max-width: 480px) {
        .footer-title-row {
            flex-direction: column !important;
            gap: 6px !important;
        }
        .app-official-logo {
            height: 28px !important;
        }
        .app-official-text {
            font-size: 13.5px !important;
        }
    }
</style>
"""
    style_part = css_template.replace("__THEME_VARS__", theme_vars)
    return splash_overlay_html + style_part

def render_top_logo() -> str:
    return """
    <div class="system-header-box notranslate" translate="no">
      <svg class="app-top-logo" viewBox="0 0 120 90" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 65 L60 88 L110 65 L110 52 L60 75 L10 52 Z" fill="#52796f" opacity="0.9"/>
        <path d="M10 52 L60 75 L110 52 L95 24 L55 24 L10 52 Z" fill="#4A6B82" opacity="0.95"/>
        <path d="M30 48 Q55 64 85 48 L90 35 Q60 48 48 35 Z" fill="#38bdf8" opacity="0.85"/>
        <path d="M55 24 L95 24 L110 52" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M26 51 Q58 68 92 49" stroke="#dc2626" stroke-width="2.2" stroke-linecap="round"/>
      </svg>
      <div class="system-title">南澳邊坡全生命週期資料庫</div>
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
        "    本網頁資料來源：邊坡全生命週期管理系統 "
        "    <a href='https://slope.thb.gov.tw/thbslope' target='_blank' rel='noopener noreferrer'>"
        "      https://slope.thb.gov.tw/thbslope"
        "    </a>"
        "  </div>"
        "</div>"
    )
    return footer_html