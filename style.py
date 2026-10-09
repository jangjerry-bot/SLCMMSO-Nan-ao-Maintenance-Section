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
            --footer-bg: #ffffff;
            --footer-text: #4A6B82;
            --footer-border: #cbd5e1;
        """
    else:
        theme_vars = """
            --bg-main: #0b0f19;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --card-bg: rgba(255, 255, 255, 0.04);
            --card-border: rgba(255, 255, 255, 0.12);
            --input-bg: #1e293b;
            --input-border: #334155;
            --input-text: #f8fafc;
            --btn-sec-bg: #1e293b;
            --btn-sec-text: #f1f5f9;
            --btn-sec-border: #334155;
            --footer-bg: rgba(255, 255, 255, 0.03);
            --footer-text: #4A6B82;
            --footer-border: rgba(255, 255, 255, 0.08);
        """

    script_part = """
<script>
    document.documentElement.setAttribute('translate', 'no');
    document.documentElement.classList.add('notranslate');
    document.body.setAttribute('translate', 'no');
    document.body.classList.add('notranslate');
    const obs = new MutationObserver((mutations) => {
        for (const m of mutations) {
            for (const n of m.addedNodes) {
                if (n.nodeType === 1 && (n.className && String(n.className).includes('immersive-translate'))) {
                    n.remove();
                }
            }
        }
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });
</script>
"""

    style_part = f"""
<style>
    :root {{
        {theme_vars}
    }}

    .stApp {{
        background-color: var(--bg-main) !important;
        color: var(--text-main) !important;
    }}

    [class*="immersive-translate"], .immersive-translate-target-wrapper {{ display: none !important; height: 0 !important; }}
    #MainMenu, footer {{ visibility: hidden; }}
    
    /* 滿版響應式設計：去除寬度限制，隨裝置全寬延展 */
    .block-container {{
        max-width: 100% !important;
        width: 100% !important;
        padding-top: clamp(3.2rem, 5vh, 4.5rem) !important;
        padding-bottom: clamp(3.5rem, 6vh, 5rem) !important;
        padding-left: clamp(12px, 2.5vw, 36px) !important;
        padding-right: clamp(12px, 2.5vw, 36px) !important;
        margin: 0 auto !important;
    }}
    
    .system-title {{
        font-size: clamp(22px, 3.2vw, 30px) !important;
        line-height: 1.35 !important;
        font-weight: 900 !important;
        letter-spacing: 1.2px;
        color: #4A6B82 !important;
        text-align: center !important;
        display: block !important;
        width: 100%;
        margin-top: 4px !important;
        margin-bottom: 16px !important;
    }}

    .map-sub-title {{
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
    }}

    /* ==========================================================================
       全站所有輸入框、下拉選單、文字標籤全面穿透重置（徹底杜絕黑底吃字）
       ========================================================================== */
    
    /* 1. 所有輸入元件上方的標籤文字 (Label) */
    div[data-testid^="st"] label,
    div[data-testid^="st"] label p,
    div[data-testid^="st"] label span,
    div[data-baseweb="form-control-label"] {{
        color: var(--text-main) !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
    }}

    /* 2. 下拉選單 (Selectbox) - 強制外框與各層容器洗白 */
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[role="combobox"],
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div[role="combobox"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }}
    /* 下拉選單內部顯示文字與箭頭圖示 */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
    div[data-baseweb="select"] * {{
        color: var(--input-text) !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        fill: var(--input-text) !important;
    }}

    /* 下拉選單展開時的浮動選項清單 (Popover / Menu) */
    div[data-baseweb="popover"],
    ul[data-baseweb="menu"],
    div[data-baseweb="menu"] {{
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
    }}
    li[data-baseweb="menu-item"] {{
        background-color: var(--card-bg) !important;
        color: var(--text-main) !important;
    }}
    li[data-baseweb="menu-item"]:hover {{
        background-color: var(--btn-sec-bg) !important;
    }}

    /* 3. 文字輸入框 (TextInput) - 強制洗白底色與輸入文字 */
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"] input,
    input[type="text"] {{
        background-color: transparent !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
    }}
    /* 輸入框預設提示文字 (Placeholder) */
    input::placeholder, textarea::placeholder {{
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        font-weight: 500 !important;
    }}

    /* 4. 禁用/唯讀輸入框 (Disabled Inputs) */
    input:disabled,
    div[data-baseweb="input"] input:disabled {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        opacity: 0.95 !important;
        cursor: not-allowed;
    }}

    /* 5. 日期選擇器 (DateInput) */
    div[data-testid="stDateInput"] > div,
    div[data-testid="stDateInput"] div[data-baseweb="input"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stDateInput"] input {{
        background-color: transparent !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
    }}

    /* 6. 多行文字備註框 (TextArea) */
    div[data-testid="stTextArea"] > div,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] textarea {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }}

    /* 7. 單選選項 (Radio) */
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] p {{
        color: var(--text-main) !important;
        font-weight: 700 !important;
        font-size: clamp(13px, 1.8vw, 15px) !important;
    }}

    /* 8. 折疊展開區塊 (Expander) */
    div[data-testid="stExpander"] {{
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }}
    div[data-testid="stExpander"] summary {{
        background-color: var(--card-bg) !important;
        color: var(--text-main) !important;
    }}
    div[data-testid="stExpander"] summary:hover {{
        background-color: var(--btn-sec-bg) !important;
    }}
    div[data-testid="stExpander"] summary * {{
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }}

    /* 9. 卡片容器與細節列 */
    .app-card {{
        background: var(--card-bg) !important;
        border-radius: 12px;
        padding: clamp(12px, 2vw, 18px);
        margin-bottom: 12px;
        border: 1px solid var(--card-border) !important;
    }}
    .detail-row {{
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid var(--card-border) !important;
        font-size: clamp(13px, 1.7vw, 14.5px);
        line-height: 1.45;
        color: var(--text-main) !important;
    }}
    .detail-label {{ color: var(--text-muted) !important; font-weight: 600; width: 40%; }}
    .detail-value {{ font-weight: 600; width: 60%; text-align: right; word-break: break-all; color: var(--text-main) !important; }}

    /* 10. 分級徽章 */
    .badge {{
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: clamp(11px, 1.4vw, 12.5px);
        font-weight: 700;
        color: #ffffff !important;
    }}
    .badge-A {{ background-color: #c05646; }}
    .badge-B {{ background-color: #d9822b; }}
    .badge-C {{ background-color: #4A6B82; }}
    .badge-D {{ background-color: #52796f; }}
    .badge-其他 {{ background-color: #64748b; }}

    .embed-map-box {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--card-border) !important;
        margin: 12px 0;
    }}

    /* 按鈕樣式 */
    button[kind="secondary"] {{
        background-color: var(--btn-sec-bg) !important;
        color: var(--btn-sec-text) !important;
        border: 1px solid var(--btn-sec-border) !important;
        font-weight: 700 !important;
    }}
    button[kind="primary"] {{
        background-color: #4A6B82 !important;
        border-color: #3E5C76 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    /* A B C D 級高對比彩色實體按鈕 */
    button[key="badge_btn_A"] {{ background-color: #c05646 !important; border: 1px solid #991b1b !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_B"] {{ background-color: #d9822b !important; border: 1px solid #c2410c !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_C"] {{ background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_D"] {{ background-color: #059669 !important; border: 1px solid #047857 !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_其他"] {{ background-color: #475569 !important; border: 1px solid #334155 !important; color: #ffffff !important; font-weight: 800 !important; }}

    /* 底部 5 顆功能按鈕容器：響應式滿版單行排列 */
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: clamp(4px, 1vw, 10px) !important;
        width: 100% !important;
        margin-top: 22px !important;
        margin-bottom: 12px !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) > div {{
        flex: 1 1 20% !important;
        min-width: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) button {{
        padding-left: clamp(2px, 0.6vw, 8px) !important;
        padding-right: clamp(2px, 0.6vw, 8px) !important;
        font-size: clamp(12px, 1.4vw, 15px) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        height: clamp(38px, 4.8vh, 44px) !important;
    }}

    /* 單位識別頁尾 */
    .app-official-footer-bottom {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
        padding: clamp(10px, 1.8vw, 16px) !important;
        background: var(--footer-bg) !important;
        border-radius: 12px !important;
        border: 1px solid var(--footer-border) !important;
        width: 100% !important;
    }}
    .footer-title-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }}
    .app-official-logo {{ 
        height: clamp(20px, 2.6vw, 26px) !important; 
        width: auto !important; 
        display: inline-block !important; 
        vertical-align: middle !important; 
    }}
    .app-official-text {{
        font-size: clamp(13px, 1.6vw, 15px) !important;
        font-weight: 800 !important;
        color: var(--footer-text) !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        line-height: clamp(20px, 2.6vw, 26px) !important;
    }}
    .app-official-source {{
        font-size: clamp(10.5px, 1.3vw, 12px) !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        margin-top: 4px !important;
        letter-spacing: 0.4px !important;
    }}
</style>
"""
    return script_part + style_part

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
        "  <div class='app-official-source notranslate' translate='no'>本網頁資料來源：邊坡全生命週期管理系統</div>"
        "</div>"
    )
    return footer_html