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
        '<stop stop-color="#52796f" stop-opacity="0.95"/><stop offset="1" stop-color="#2d4a43" stop-opacity="0.95"/>'
        '</linearGradient>'
        '<linearGradient id="splashGradPrism" x1="150" y1="55" x2="170" y2="168" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#4A6B82" stop-opacity="0.9"/><stop offset="1" stop-color="#1e293b" stop-opacity="0.95"/>'
        '</linearGradient>'
        '<linearGradient id="splashGradSeepage" x1="95" y1="75" x2="235" y2="142" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#38bdf8" stop-opacity="0.85"/><stop offset="1" stop-color="#0284c7" stop-opacity="0.95"/>'
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
    :root { __THEME_VARS__ }

    #geo-splash-overlay { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: #0b0f19 !important; z-index: 99999999 !important; display: flex !important; justify-content: center !important; align-items: center !important; pointer-events: none !important; animation: splashDismiss 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2.4s forwards !important; }
    @keyframes splashDismiss { 0% { opacity: 1; visibility: visible; } 99% { opacity: 0; visibility: visible; } 100% { opacity: 0; visibility: hidden; display: none !important; } }
    .geo-splash-center { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; text-align: center !important; padding: 20px !important; }
    .geo-splash-svg { width: clamp(260px, 46vw, 380px) !important; height: auto !important; filter: drop-shadow(0 14px 28px rgba(0, 0, 0, 0.6)) !important; }
    .geo-splash-title { color: #f8fafc !important; font-size: clamp(20px, 2.8vw, 26px) !important; font-weight: 900 !important; letter-spacing: 2px !important; margin-top: 18px !important; animation: titleFadeIn 0.8s ease-out !important; }
    .geo-splash-sub { color: #38bdf8 !important; font-size: clamp(10.5px, 1.4vw, 12.5px) !important; font-weight: 700 !important; letter-spacing: 2.4px !important; margin-top: 6px !important; animation: titleFadeIn 1.0s ease-out !important; }

    .geo-mesh-grid { animation: meshPop 0.8s ease-out; transform-origin: center; transform-box: fill-box; }
    .geo-red-axis { animation: meshPop 0.6s ease-out; transform-origin: center; transform-box: fill-box; }
    .geo-base-layer, .geo-slope-prism, .geo-seepage-mass { animation: modelRise 0.8s cubic-bezier(0.16, 1, 0.3, 1); transform-box: fill-box; }
    .geo-red-crest { stroke-dasharray: 200; stroke-dashoffset: 200; animation: drawLine 1.1s 0.1s ease-in-out forwards; filter: drop-shadow(0 0 6px #ef4444); }
    .geo-red-shear { stroke-dasharray: 220; stroke-dashoffset: 220; animation: drawLine 1.1s 0.2s ease-in-out forwards; filter: drop-shadow(0 0 8px #dc2626); }
    .geo-slip-stream { stroke-dasharray: 260; stroke-dashoffset: 260; animation: drawLine 1.2s 0.3s ease-in-out forwards; filter: drop-shadow(0 0 7px #38bdf8); }
    .geo-slip-stream-sub { stroke-dasharray: 180; stroke-dashoffset: 180; animation: drawLine 1.0s 0.4s ease-in-out forwards; filter: drop-shadow(0 0 5px #0ea5e9); }

    @keyframes drawLine { to { stroke-dashoffset: 0; } }
    @keyframes modelRise { from { transform: translateY(12px); opacity: 0.2; } to { transform: translateY(0); opacity: 1; } }
    @keyframes meshPop { from { transform: scale(0.92); opacity: 0.1; } to { transform: scale(1); opacity: 1; } }
    @keyframes titleFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    html, body, [class*="css"] { color: var(--text-main) !important; }
    .stApp { background-color: var(--bg-main) !important; color: var(--text-main) !important; }
    [class*="immersive-translate"], .immersive-translate-target-wrapper { display: none !important; height: 0 !important; }
    #MainMenu, footer { visibility: hidden; }
    
    .block-container { max-width: 100% !important; width: 100% !important; padding-top: clamp(1rem, 2.5vh, 2.5rem) !important; padding-bottom: clamp(2.5rem, 4vh, 3.5rem) !important; padding-left: clamp(10px, 2.5vw, 32px) !important; padding-right: clamp(10px, 2.5vw, 32px) !important; margin: 0 auto !important; }
    
    /* ===== 全新升級：頂部標題與 3D LOGO 排版 ===== */
    .system-header-box { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; gap: 8px !important; margin-top: 0px !important; margin-bottom: 20px !important; width: 100% !important; text-align: center !important; }
    
    /* 將 3D LOGO 大幅放大，使其更具視覺張力 */
    .app-top-logo { width: clamp(80px, 14vw, 120px) !important; height: auto !important; margin-bottom: 2px !important; flex-shrink: 0 !important; filter: drop-shadow(0 4px 12px rgba(56, 189, 248, 0.35)) !important; }
    
    /* 標題與手冊連結的排版 */
    .title-wrapper { display:flex; flex-direction:column; align-items:center; justify-content:center; width: 100%; }
    .system-title { font-size: clamp(22px, 3.2vw, 32px) !important; line-height: 1.3 !important; font-weight: 900 !important; letter-spacing: 1.5px; color: #4A6B82 !important; margin: 0 !important; text-align: center !important; }
    
    /* 改良版的膠囊按鈕式連結，置中對齊 */
    .manual-link-btn { display: inline-flex; align-items: center; justify-content: center; background-color: #e0f2fe; color: #0369a1 !important; font-size: clamp(13px, 1.6vw, 15px) !important; font-weight: 800 !important; text-decoration: none !important; padding: 6px 18px; border-radius: 20px; margin-top: 10px; border: 1px solid #bae6fd; transition: all 0.2s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .manual-link-btn:hover { background-color: #bae6fd; color: #0c4a6e !important; transform: translateY(-1px); box-shadow: 0 3px 5px rgba(0,0,0,0.1); }

    .map-sub-title { font-size: clamp(16px, 2.4vw, 20px) !important; line-height: 1.3 !important; font-weight: 800 !important; letter-spacing: 0.8px; color: #4A6B82 !important; text-align: center !important; display: block !important; width: 100%; margin-top: 0px !important; margin-bottom: 6px !important; }

    button p { font-size: 16px !important; }
    .route-green-text { font-size: 18px !important; color: #059669 !important; font-weight: 900 !important; }
    .detail-green-text { font-size: 22px !important; color: #059669 !important; font-weight: 900 !important; }

    html body .stApp div[data-baseweb="select"], html body .stApp div[data-testid="stTextInput"] div[data-baseweb="base-input"], html body .stApp div[data-testid="stDateInput"] div[data-baseweb="input"], html body .stApp div[data-baseweb="textarea"] textarea { background-color: var(--input-bg) !important; border: 1px solid var(--input-border) !important; border-radius: 8px !important; }
    html body .stApp input[type="text"], html body .stApp textarea { color: #0f172a !important; -webkit-text-fill-color: #0f172a !important; font-size: 15px !important; font-weight: 600 !important; }

    .app-card { background: var(--card-bg) !important; border-radius: 12px; padding: clamp(12px, 2vw, 18px); margin-bottom: 12px; border: 1px solid var(--card-border) !important; }
    .detail-row { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid var(--card-border) !important; font-size: clamp(14px, 1.7vw, 15px); line-height: 1.45; color: var(--text-main) !important; }
    .detail-label { color: var(--text-muted) !important; font-weight: 600; width: 40%; }
    .detail-value { font-weight: 600; width: 60%; text-align: right; word-break: break-all; color: var(--text-main) !important; }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 14px; font-weight: 800; color: #ffffff !important; }
    .badge-A { background-color: #c05646; } .badge-B { background-color: #d9822b; } .badge-C { background-color: #4A6B82; } .badge-D { background-color: #52796f; } .badge-其他 { background-color: #64748b; }

    .embed-map-box { border-radius: 12px; overflow: hidden; border: 1px solid var(--card-border) !important; margin: 12px 0; }
    button[kind="secondary"] { background-color: var(--btn-sec-bg) !important; color: var(--btn-sec-text) !important; border: 1px solid var(--btn-sec-border) !important; font-weight: 800 !important; }
    button[kind="primary"] { background-color: #4A6B82 !important; border-color: #3E5C76 !important; color: #ffffff !important; font-weight: 800 !important; }

    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: clamp(4px, 1vw, 10px) !important; width: 100% !important; margin-top: 4px !important; margin-bottom: 16px !important; }
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) > div { flex: 1 1 20% !important; min-width: 0 !important; }

    .app-official-footer-bottom { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; margin-top: 30px !important; margin-bottom: 26px !important; padding: 8px 12px !important; background: transparent !important; border: none !important; width: 100% !important; }
    .footer-title-row { display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: center !important; gap: 8px !important; margin-bottom: 8px !important; flex-wrap: nowrap !important; width: 100% !important; }
    .app-official-logo { height: clamp(24px, 5.0vw, 36px) !important; width: auto !important; flex-shrink: 0 !important; }
    .app-official-text { font-size: clamp(11.5px, 3.2vw, 17px) !important; font-weight: 900 !important; color: var(--footer-text) !important; white-space: nowrap !important; letter-spacing: 0px !important; }
    .app-official-source { font-size: 13px !important; font-weight: 600 !important; color: var(--text-muted) !important; line-height: 1.6 !important; text-align: center !important; }
    .app-official-source a { color: var(--link-color) !important; text-decoration: underline !important; font-weight: 700 !important; margin-left: 4px !important; }

    .pwa-download-btn { display: flex; align-items: center; justify-content: center; width: 100%; height: 44px; background-color: #4A6B82; color: #ffffff !important; font-size: 16px; font-weight: 800; border-radius: 8px; text-decoration: none !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 8px; }
    .pwa-download-btn:hover { background-color: #3E5C76; }
</style>
"""
    style_part = css_template.replace("__THEME_VARS__", theme_vars)
    return splash_overlay_html + style_part

def render_top_logo() -> str:
    import os, base64
    
    manual_link = '<div style="color:#ef4444; font-size:12px; font-weight:bold; margin-top:6px;">⚠️ 尚未偵測到手冊檔案 (請確認 GitHub 目錄下有包含「手冊」二字的 pdf 檔)</div>'
    
    try:
        for f in os.listdir('.'):
            if '手冊' in f and f.lower().endswith('.pdf'):
                with open(f, "rb") as pdf_file:
                    b64_pdf = base64.b64encode(pdf_file.read()).decode()
                href = f"data:application/pdf;base64,{b64_pdf}"
                manual_link = f'<a href="{href}" download="{f}" target="_blank" class="manual-link-btn">📘 下載操作與養護巡查作業教學手冊</a>'
                break
    except Exception as e:
        manual_link = f'<div style="color:#ef4444; font-size:12px; margin-top:6px;">⚠️ 手冊讀取失敗: {e}</div>'

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
        {manual_link}
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
        "    本網頁資料來源：邊坡全生命週期管理系統 <a href='https://slope.thb.gov.tw/thbslope' target='_blank' rel='noopener noreferrer'>https://slope.thb.gov.tw/thbslope</a><br/>"
        "    公路局圖說公路平台-圖台 <a href='https://eroad.thb.gov.tw/DGOHForeground/Map/Index' target='_blank' rel='noopener noreferrer'>https://eroad.thb.gov.tw/DGOHForeground/Map/Index</a>"
        "  </div>"
        "</div>"
    )
    return footer_html