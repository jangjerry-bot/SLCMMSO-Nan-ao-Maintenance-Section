import os
import base64

def get_theme_css(is_light: bool) -> str:
    if is_light:
        theme_vars = """
            --bg-main: #f8fafc;
            --text-main: #0f172a;
            --text-muted: #475569;
            --card-bg: #ffffff;
            --card-border: #cbd5e1;
            --btn-sec-bg: #e2e8f0;
            --btn-sec-text: #0f172a;
            --btn-sec-border: #94a3b8;
            --footer-bg: #f1f5f9;
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
            --btn-sec-bg: #1e293b;
            --btn-sec-text: #f1f5f9;
            --btn-sec-border: #334155;
            --footer-bg: rgba(255, 255, 255, 0.03);
            --footer-text: #4A6B82;
            --footer-border: rgba(255, 255, 255, 0.08);
        """

    return f"""
<script>
    document.documentElement.setAttribute('translate', 'no');
    document.documentElement.classList.add('notranslate');
    document.body.setAttribute('translate', 'no');
    document.body.classList.add('notranslate');
    const obs = new MutationObserver((mutations) => {{
        for (const m of mutations) {{
            for (const n of m.addedNodes) {{
                if (n.nodeType === 1 && (n.className && String(n.className).includes('immersive-translate'))) {{
                    n.remove();
                }}
            }}
        }}
    }});
    obs.observe(document.documentElement, {{ childList: true, subtree: true }});
</script>
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
    
    .block-container {{
        max-width: 860px !important;
        padding-top: 4.8rem !important;
        padding-bottom: 4.5rem !important;
        margin: 0 auto !important;
    }}
    
    .system-title {{
        font-size: 26px !important;
        line-height: 1.4 !important;
        font-weight: 900 !important;
        letter-spacing: 1.2px;
        color: #4A6B82 !important;
        text-align: center !important;
        display: block !important;
        width: 100%;
        margin-top: 4px !important;
        margin-bottom: 18px !important;
    }}

    .map-sub-title {{
        font-size: 18px !important;
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

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] p {{
        color: var(--text-main) !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
    }}

    .app-card {{
        background: var(--card-bg) !important;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        border: 1px solid var(--card-border) !important;
    }}
    .detail-row {{
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid var(--card-border) !important;
        font-size: 14px;
        line-height: 1.45;
        color: var(--text-main) !important;
    }}
    .detail-label {{ color: var(--text-muted) !important; font-weight: 500; width: 40%; }}
    .detail-value {{ font-weight: 600; width: 60%; text-align: right; word-break: break-all; color: var(--text-main) !important; }}

    .badge {{
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11.5px;
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

    button[key="badge_btn_A"] {{ background-color: #c05646 !important; border: 1px solid #991b1b !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_B"] {{ background-color: #d9822b !important; border: 1px solid #c2410c !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_C"] {{ background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_D"] {{ background-color: #059669 !important; border: 1px solid #047857 !important; color: #ffffff !important; font-weight: 800 !important; }}
    button[key="badge_btn_其他"] {{ background-color: #475569 !important; border: 1px solid #334155 !important; color: #ffffff !important; font-weight: 800 !important; }}

    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        width: 100% !important;
        margin-top: 20px !important;
        margin-bottom: 12px !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) > div {{
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key^="nav_btn_"]) button {{
        padding-left: 2px !important;
        padding-right: 2px !important;
        font-size: 13px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        height: 38px !important;
    }}

    .app-official-footer-bottom {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
        padding: 12px 14px !important;
        background: var(--footer-bg) !important;
        border-radius: 10px !important;
        border: 1px solid var(--footer-border) !important;
    }}
    .footer-title-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }}
    .app-official-logo {{ height: 22px !important; width: auto !important; display: inline-block !important; vertical-align: middle !important; }}
    .app-official-text {{
        font-size: 13.5px !important;
        font-weight: 800 !important;
        color: var(--footer-text) !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        line-height: 22px !important;
    }}
    .app-official-source {{
        font-size: 11px !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        margin-top: 4px !important;
        letter-spacing: 0.4px !important;
    }}
</style>
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

    return f"""
<div class='app-official-footer-bottom notranslate' translate='no'>
  <div class='footer-title-row'>
    {logo_render}
    <span class='app-official-text notranslate' translate='no'>交通部公路局東區養護工程分局南澳工務段</span>
  </div>
  <div class='app-official-source notranslate' translate='no'>本網頁資料來源：邊坡全生命週期管理系統</div>
</div>
"""