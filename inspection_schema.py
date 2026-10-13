# inspection_schema.py
import base64

INSPECTION_TEMPLATES = {
    "岩(地)錨(格梁)": {
        "title": "表A3-6 岩（地）錨（格梁）護坡設施",
        "category_col_header": "設施類別",
        "category_name": "岩(地)錨(格梁)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "items": [
            ("1.材料老化程度、斷裂、腐蝕及損壞情形", "更換"),
            ("2.變形", "填補換修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("3.本體結構損壞", "整修或拆除更新，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("4.附屬結構物損壞", "換修或拆除更新"),
            ("5.基礎損壞", "查明原因，並整修或拆除重建基礎"),
            ("6.背面堆積土，超載", "開挖移除"),
            ("7.空洞", "填補整平，以防雨水入滲"),
            ("8.混凝土表面剝落", "填補整修，以防雨水入滲"),
            ("9.框梁鬆脫、填敷材料突出、下沉、有孔隙", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("10.擠(鼓)出、隆起、鬆動", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("11.裂縫、龜裂", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("12.接縫異樣、接縫不符合", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("13.剝落", "填補整修"),
            ("14.鋼筋曝露、銹蝕", "填補混凝土"),
            ("15.回填材料流失", "填補回填材料，並覆以保護材料"),
            ("16.結構之整體沉陷、移動", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，或於擋土牆背側開挖解壓，以增加其穩定性"),
            ("17.結構之整體傾倒(斜)", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並加強持續觀測，另考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，以增加其穩定性"),
            ("18.地(岩)錨預力損失", "調整地(岩)錨預力或補強"),
            ("19.地(岩)錨預力抗張材(鋼腱)斷裂", "增補地錨，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("20.地(岩)錨錨頭脫落、變形或銹蝕", "採用保護蓋或混凝土加以保護"),
            ("21.沖刷", "鋪設臨時性覆蓋物，如：帆布等"),
            ("22.排(洩)水管、坡面排水、湧水", "疏通或補設排水管；檢查湧水之水質，改善或加設截、排水設施，必要時加強水位觀測"),
            ("23.發現深層滑動現象", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並持續觀測，必要時需疏散居民，進行大規模整治")
        ]
    },
    "自然邊坡": {
        "title": "表A3-1 自然邊坡",
        "category_col_header": "設施類別",
        "category_name": "自然邊坡",
        "dim_title": "邊坡形狀",
        "dim_h_label": "高度",
        "dim_w_label": "邊坡面寬",
        "items": [
            ("1.整體邊坡滑動、崩塌", "依破壞機制及滑動規模，選擇適當工法修復"),
            ("2.局部滑動、崩塌", "依破壞機制及滑動規模，選擇適當工法修復"),
            ("3.落石", "清除落石，必要時依坡面狀況選擇適當工法修復"),
            ("4.沖刷、蝕溝", "加強截、排水設施；填補或修築保護措施"),
            ("5.植生生長不良、枯死", "補植"),
            ("6.排(洩)水管、坡面排水、湧水", "疏通或補設排水管；檢查湧水之水質，改善或加設截、排水設施，必要時加強水位觀測")
        ]
    }
}

def match_template(struct_name):
    for k in INSPECTION_TEMPLATES.keys():
        if k in str(struct_name):
            return k
    return "自然邊坡"

def generate_doc_report(data, photos):
    chk_reg = "■" if data.get('type') == "定期檢測" else "□"
    chk_spc = "■" if data.get('type') == "特別檢測" else "□"

    # ===== 1. 抓取整體備註，確保無論寫什麼都帶入 =====
    remark_val = data.get('remark', '').strip()
    
    html_head = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{data.get('title')}</title>
    <style>
        @page {{ size: A4 portrait; margin: 1.5cm 1.5cm 1.5cm 1.5cm; }}
        body {{ font-family: "標楷體", "DFKai-SB", "PMingLiU", serif; color: #000; line-height: 1.35; margin: 0; padding: 0; }}
        table {{ width: 100% !important; max-width: 100% !important; border-collapse: collapse !important; table-layout: fixed !important; margin: 0; }}
        td, th {{ border: 1px solid #000; padding: 4px 4px; font-size: 12px; word-wrap: break-word; overflow: hidden; }}
        .header-title {{ font-size: 17.5px; font-weight: bold; text-align: center; margin-bottom: 6px; }}
        .meta-line {{ font-size: 12px; margin-bottom: 5px; white-space: nowrap; }}
    </style>
</head>
<body>
    <div class="header-title">{data.get('title')}（{chk_reg}定期{chk_spc}特別）檢測表</div>
    <div class="meta-line">
        口卡編號：{data.get('code', '')}；日期：{data.get('date', '')}；天氣狀況(晴/陰/雨)：{data.get('weather', '')}
    </div>
    <table>
        <colgroup>
            <col style="width: 12%;">
            <col style="width: 12%;">
            <col style="width: 11%;">
            <col style="width: 15%;">
            <col style="width: 14%;">
            <col style="width: 11%;">
            <col style="width: 12%;">
            <col style="width: 13%;">
        </colgroup>
        <tr><td style="text-align:center; font-weight:bold;">養護單位</td><td colspan="7">{data.get('unit', '')}</td></tr>
        <tr>
            <td style="text-align:center; font-weight:bold;">檢查位置</td><td colspan="3">{data.get('location', '')}</td>
            <td style="text-align:center; font-weight:bold;">里 程</td><td colspan="3">□北下(西向)、□南上(東向)</td>
        </tr>
        <tr>
            <td rowspan="5" style="text-align:center; vertical-align:middle; font-weight:bold; letter-spacing:4px;">現 場<br>狀 況</td>
            <td style="font-weight:bold;">地質狀況</td><td colspan="6">■{data.get('geo', '土層邊坡')} □岩層邊坡 □礫石層邊坡 □其他地質，說明：</td>
        </tr>
        <tr>
            <td style="font-weight:bold;">{data.get('dim_title', '設施形狀')}</td>
            <td style="font-weight:bold; text-align:center;">{data.get('dim_h_label', '高度')}</td><td>{data.get('height', '')} 公尺</td>
            <td style="font-weight:bold; text-align:center;">坡度(坡距比)</td><td style="text-align:center;">{data.get('slope', '')}</td>
            <td style="font-weight:bold; text-align:center;">{data.get('dim_w_label', '設施面寬')}</td><td>{data.get('width', '')} 公尺</td>
        </tr>
        <tr>
            <td rowspan="2" style="font-weight:bold; vertical-align:middle;">地下水狀況</td>
            <td style="font-weight:bold; text-align:center;">排水湧水</td><td>■{data.get('water', '乾燥')} □濕潤<br>□表面水 □湧水</td>
            <td style="font-weight:bold; text-align:center;">湧水位置</td><td></td>
            <td style="font-weight:bold; text-align:center;">湧水量</td><td>約&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;公升/分</td>
        </tr>
        <tr>
            <td colspan="2" style="font-weight:bold; text-align:center;">湧水之地質狀況</td><td></td>
            <td style="font-weight:bold; text-align:center;">調查時間</td><td>{data.get('survey_month', '')}月</td>
            <td colspan="2">降雨後 {data.get('rain_days', '3')} 日</td>
        </tr>
        <tr>
            <td style="font-weight:bold;">排(洩)水管</td><td colspan="6">■{data.get('drain', '正常')} □阻塞</td>
        </tr>
        <tr><td style="text-align:center; font-weight:bold;">監測系統</td><td colspan="7">■無 □有，項目說明：</td></tr>
        <tr>
            <td style="text-align:center; font-weight:bold;">監測情形</td><td colspan="3">□無 ■有：□自行量測 ■委外量測</td>
            <td style="text-align:center; font-weight:bold;">監測頻率</td><td colspan="3">□每月 □每季 □每半年 ■每年 □其他</td>
        </tr>
        <tr>
            <td style="text-align:center; font-weight:bold;">災害歷史</td>
            <td style="font-weight:bold; text-align:center;">以往災害</td><td colspan="2">■無 □有</td>
            <td style="text-align:center; font-weight:bold;">鄰近災害</td><td colspan="3">■無 □有，說明：</td>
        </tr>
    </table>
"""

    html_items = f"""
    <table style="margin-top: -1px;">
        <colgroup>
            <col style="width: 9%;">
            <col style="width: 25%;">
            <col style="width: 24%;">
            <col style="width: 8%;">
            <col style="width: 15%;">
            <col style="width: 19%;">
        </colgroup>
        <thead>
            <tr style="text-align:center; font-weight:bold; background:#f2f2f2;">
                <td>{data.get('category_col_header', '設施類別')}</td>
                <td>檢查項目</td>
                <td>養護措施</td>
                <td>檢查結果</td>
                <td>處理情形</td>
                <td>注意事項</td>
            </tr>
        </thead>
        <tbody>
"""
    rows = data.get('check_rows', [])
    rcount = len(rows)
    for i, row in enumerate(rows):
        iname, iact, ires, idesc = row
        res_char = "○" if "○" in ires else ("×" if "×" in ires else "／")
        html_items += "<tr>"
        if i == 0:
            html_items += f'<td rowspan="{rcount}" style="border:1px solid #000; text-align:center; vertical-align:middle; font-weight:bold; width:9%; letter-spacing:2px;">(請自填)</td>'
        html_items += f'<td style="border:1px solid #000; font-size:12px; padding:4px 5px;">{iname}</td>'
        html_items += f'<td style="border:1px solid #000; font-size:12px; padding:4px 5px;">{iact}</td>'
        html_items += f'<td style="border:1px solid #000; text-align:center; font-size:15px; font-weight:bold; width:8%;">{res_char}</td>'
        html_items += f'<td style="border:1px solid #000; font-size:12px; padding:4px 5px; width:15%;">{idesc}</td>'
        if i == 0:
            html_items += f'<td rowspan="{rcount}" style="border:1px solid #000; vertical-align:top; font-size:11px; width:19%; line-height:1.42; padding:5px;">一、檢查結果應記錄(正常)(○)、(異常)(×)、(無此項)(／)；發現異常情形，應於備註欄註記。<br><br>二、設施異常時，應即設法處理，或將檢查表簽請核辦。</td>'
        html_items += "</tr>"

    html_items += f"""
        <tr><td style="text-align:center; font-weight:bold;">備 註</td><td colspan="5" style="font-size:11.5px; padding:4px 6px;">{remark_val}</td></tr>
        <tr><td colspan="6" style="padding:6px 10px;"><span style="font-weight:bold;">檢測人員：</span>{data.get('inspector', '')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="font-weight:bold;">單位主管：</span>{data.get('supervisor', '')}</td></tr>
    </table>
"""

    # ===== 2. 組合照片表底部備註條款 =====
    remark_html = "1.如有需要，可另外加頁以容納更多圖片。<br>2.記錄照片應於上次檢查時所拍攝之同一位置拍攝。"
    # 如果使用者有填寫「自訂現地備註」，我們強力置入在照片下方，絕對不會漏看！
    if remark_val:
        remark_html += f"<br><br><span style='font-weight:bold; color:#0f172a;'>【現地綜合備註】：</span>{remark_val}"

    html_photos = f"""
        <div style="page-break-before:always; margin-top:20px;"></div>
        <div style="text-align:center; font-size:16px; font-weight:bold; margin-bottom:5px;">
            {data.get('title')}（{chk_reg}定期{chk_spc}特別）檢測附件圖片說明表
        </div>
        <div style="font-size:12px; margin-bottom:4px;">
            口卡編號：{data.get('code', '')}；日期：{data.get('date', '')}；天氣狀況(晴/陰/雨)：{data.get('weather', '')}
        </div>
        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="border:1px solid #000; width:12%; text-align:center; font-weight:bold; background:#fafafa;">養護單位</td>
                <td style="border:1px solid #000; width:38%;">{data.get('unit', '')}</td>
                <td style="border:1px solid #000; width:12%; text-align:center; font-weight:bold; background:#fafafa;">檢測位置</td>
                <td style="border:1px solid #000; width:38%;">{data.get('location', '')}</td>
            </tr>
        </table>
"""
    if photos:
        for idx, photo_data in enumerate(photos):
            
            # ===== 3. 解開 Tuple 取出影像與對應的「異常說明」 =====
            if isinstance(photo_data, tuple):
                p_bytes, p_desc = photo_data
            else:
                p_bytes, p_desc = photo_data, ""
                
            b64_img = base64.b64encode(p_bytes).decode()
            
            html_photos += f"""
            <table style="width:100%; border-collapse:collapse; margin-top:12px; page-break-inside:avoid;">
                <tr>
                    <td style="border:1px solid #000; width:15%; text-align:center; font-weight:bold; padding:6px; font-size:14px;">編號</td>
                    <td style="border:1px solid #000; width:85%; text-align:center; font-weight:bold; padding:6px; letter-spacing:2px; font-size:14px;">紀 錄 圖 片</td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; text-align:center; vertical-align:middle; font-size:14px; font-weight:bold;">{idx+1}</td>
                    <td style="border:1px solid #000; text-align:center; padding:10px;">
                        <img src="data:image/jpeg;base64,{b64_img}" style="max-height: 350px; max-width: 95%; object-fit: contain;">
                    </td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; text-align:center; font-weight:bold; letter-spacing:4px; padding:18px 0; font-size:14px;">說 明</td>
                    <td style="border:1px solid #000; padding:18px; font-size:14px; text-align:left; vertical-align:middle; font-weight:bold; color:#0f172a;">{p_desc}</td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; text-align:center; font-weight:bold; letter-spacing:4px; padding:10px 0; font-size:14px;">備 註</td>
                    <td style="border:1px solid #000; padding:8px 10px; font-size:12px; line-height:1.6; text-align:left;">
                        {remark_html}
                    </td>
                </tr>
            </table>
            """
    else:
        html_photos += "<p style='font-size:12px; text-align:center; margin-top:20px;'>(本次巡查無拍攝照片)</p>"

    html_end = "</body></html>"
    full_html = html_head + html_items + html_photos + html_end
    
    return "\ufeff".encode('utf-8') + full_html.encode('utf-8')