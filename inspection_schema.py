# inspection_schema.py
import datetime
import base64
import re

# 公路局 8 大邊坡設施檢查規範表 (表 A3-1 ~ 表 A3-8) 完整逐字資料庫
INSPECTION_TEMPLATES = {
    "自然邊坡": {
        "title": "表A3-1 自然邊坡",
        "category_col_header": "邊坡類別",
        "category_name": "植生邊坡",
        "dim_title": "邊坡形狀",
        "dim_h_label": "坡高",
        "dim_w_label": "邊坡面寬",
        "remark_default": "人工可及，以人工檢測為原則；人工不可及，以其它科技方法（如UAV）代替。",
        "items": [
            ("1.崩落", "清除崩塌土石"),
            ("2.裂縫、鼓出、坍陷", "坡面整平及裂縫填補，以防雨水入滲"),
            ("3.表土剝落、雨蝕溝", "檢查坡面風化程度、侵蝕狀況，並將坡面整平、加強植生，另應檢查坡面周圍排水設施之排水情形，必要時改善或加設截、排水設施"),
            ("4.平臺上堆積物", "清除堆積物"),
            ("5.湧水", "檢查湧水之水質，改善或加設截、排水設施"),
            ("6.樹木傾倒、雜草異常茂盛", "清除傾木及雜草，以免影響行車安全視距"),
            ("7.植生枯損", "再植生、追肥或使用其他方法外，對植生被覆狀況應充分掌握"),
            ("8.行車目視可及範圍內垃圾堆積", "清除"),
            ("9.鬆動浮石、滾石", "挖除浮石、滾石，並依邊坡現況設置落石防護設施"),
            ("10.坡頂與坡面截水、排水設施", "裂縫修補、截排水設施破壞修復、淤塞清除"),
            ("11.非法耕作及佔有", "予以制止、排除及復舊")
        ]
    },
    "防石柵": {
        "title": "表A3-2 防石柵設施",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "人工可及，以人工檢測為原則；人工不可及，以其它科技方法（如UAV）代替。",
        "items": [
            ("1.材料老化程度、斷裂、腐蝕及損壞情形", "更換"),
            ("2.變形", "填補換修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("3.本體結構損壞", "整修或拆除更新，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("4.附屬結構物損壞", "換修或拆除更新"),
            ("5.基礎損壞", "查明原因，並整修或拆除重建基礎"),
            ("6.背面土石堆積", "清除堆積土石以確保其功能")
        ]
    },
    "石籠護坡": {
        "title": "表A3-3 石（箱）籠護坡設施",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "",
        "items": [
            ("1.材料老化程度、斷裂、腐蝕及損壞情形", "更換"),
            ("2.變形", "填補換修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("3.本體結構損壞", "整修或拆除更新，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("4.附屬結構物損壞", "換修或拆除更新"),
            ("5.基礎損壞", "查明原因，並整修或拆除重建基礎"),
            ("6.背面堆積土，超載", "開挖移除"),
            ("7.空洞", "填補整平，以防雨水入滲"),
            ("8.框梁鬆脫、填敷材料突出、下沉、有孔隙", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("9.擠(鼓)出、隆起、鬆動", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("10.裂縫、龜裂", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("11.接縫異樣、接縫不符合", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("12.剝落", "填補整修"),
            ("13.回填材料流失", "填補回填材料，並覆以保護材料"),
            ("14.結構之整體沉陷、移動", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，或於擋土牆背側開挖解壓，以增加其穩定性"),
            ("15.結構之整體傾倒(斜)", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並加強持續觀測，另考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，以增加其穩定性"),
            ("16.沖刷", "鋪設臨時性覆蓋物，如：帆布等"),
            ("17.排(洩)水管、坡面排水、湧水", "疏通或補設排水管；檢查湧水之水質，改善或加設截、排水設施，必要時加強水位觀測"),
            ("18.發現深層滑動現象", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並持續觀測，必要時需疏散居民，進行大規模整治")
        ]
    },
    "噴凝土護坡": {
        "title": "表A3-4 噴凝土護坡設施",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "人工可及，以人工檢測為原則；人工不可及，以其它科技方法（如UAV）代替。",
        "items": [
            ("1.材料老化程度、斷裂、腐蝕及損壞情形", "更換"),
            ("2.變形", "填補換修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("3.本體結構損壞", "整修或拆除更新，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("4.附屬結構物損壞", "換修或拆除更新"),
            ("5.空洞", "填補整平，以防雨水入滲"),
            ("6.混凝土表面剝落", "填補整修，以防雨水入滲"),
            ("7.擠(鼓)出、隆起、鬆動", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("8.裂縫、龜裂", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("9.接縫異樣、接縫不符合", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("10.剝落", "填補整修"),
            ("11.鋼筋曝露、銹蝕", "填補混凝土"),
            ("12.回填材料流失", "填補回填材料，並覆以保護材料"),
            ("13.結構之整體沉陷、移動", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，或於擋土牆背側開挖解壓，以增加其穩定性"),
            ("14.結構之整體傾倒(斜)", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並加強持續觀測，另考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，以增加其穩定性"),
            ("15.沖刷", "鋪設臨時性覆蓋物，如：帆布等"),
            ("16.排(洩)水管、坡面排水、湧水", "疏通或補設排水管；檢查湧水之水質，改善或加設截、排水設施，必要時加強水位觀測"),
            ("17.發現深層滑動現象", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並持續觀測，必要時需疏散居民，進行大規模整治")
        ]
    },
    "RC格框(格子梁)": {
        "title": "表A3-5 混凝土格框或格子梁護坡設施",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "人工可及，以人工檢測為原則；人工不可及，以其它科技方法（如UAV）代替。",
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
            ("18.沖刷", "鋪設臨時性覆蓋物，如：帆布等"),
            ("19.排(洩)水管、坡面排水、湧水", "疏通或補設排水管；檢查湧水之水質，改善或加設截、排水設施，必要時加強水位觀測"),
            ("20.發現深層滑動現象", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並持續觀測，必要時需疏散居民，進行大規模整治")
        ]
    },
    "岩(地)錨": {
        "title": "表A3-6 岩（地）錨（格梁）護坡設施",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "人工可及，以人工檢測為原則；人工不可及，以其它科技方法（如UAV）代替。",
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
    "RC擋土牆": {
        "title": "表A3-7 混凝土擋土牆",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "",
        "items": [
            ("1.材料老化程度、斷裂、腐蝕及損壞情形", "更換"),
            ("2.變形", "填補換修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("3.本體結構損壞", "整修或拆除更新，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("4.附屬結構物損壞", "換修或拆除更新"),
            ("5.基礎損壞", "查明原因，並整修或拆除重建基礎"),
            ("6.背面堆積土，超載", "開挖移除"),
            ("7.空洞", "填補整平，以防雨水入滲"),
            ("8.混凝土表面剝落", "填補整修，以防雨水入滲"),
            ("11.裂縫、龜裂", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("12.接縫異樣、接縫不符合", "填補整修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("13.剝落", "填補整修"),
            ("14.鋼筋曝露、銹蝕", "填補混凝土"),
            ("16.結構之整體沉陷、移動", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，或於擋土牆背側開挖解壓，以增加其穩定性"),
            ("17.結構之整體傾倒(斜)", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並加強持續觀測，另考量於坡趾加築擋土牆、臨時支撐，或加填土石、加強地錨預力，以增加其穩定性"),
            ("22.排(洩)水管、坡面排水、湧水", "疏通或補設排水管；檢查湧水之水質，改善或加設截、排水設施，必要時加強水位觀測"),
            ("23.發現深層滑動現象", "必要時以監測系統及地質調查，確定滑動規模及破壞機制，並持續觀測，必要時需疏散居民，進行大規模整治")
        ]
    },
    "預力地錨RC擋土牆": {
        "title": "表A3-8 預力地錨鋼筋混凝土（或排樁）擋土牆",
        "category_col_header": "設施類別",
        "category_name": "(請自填)",
        "dim_title": "設施形狀",
        "dim_h_label": "高度",
        "dim_w_label": "設施面寬",
        "remark_default": "人工可及，以人工檢測為原則；人工不可及，以其它科技方法（如UAV）代替。",
        "items": [
            ("1.材料老化程度、斷裂、腐蝕及損壞情形", "更換"),
            ("2.變形", "填補換修，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("3.本體結構損壞", "整修或拆除更新，必要時以監測系統及地質調查，確定滑動規模及破壞機制"),
            ("4.附屬結構物損壞", "換修或拆除更新"),
            ("5.基礎損壞", "查明原因，並整修或拆除重建基礎"),
            ("6.背面堆積土，超載", "開挖移除"),
            ("7.空洞", "填補整平，以防雨水入滲"),
            ("8.混凝土表面剝落", "填補整修，以防雨水入滲"),
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
    }
}

def match_template(struct_name: str) -> str:
    """精準正規化構造物名稱，支援全形、半形、括號等各種外業命名"""
    s = str(struct_name).strip()
    clean_s = re.sub(r'[\s（）\(\)\-_/]+', '', s)
    
    if any(k in clean_s for k in ["柵", "防石", "落石柵"]):
        return "防石柵"
    if any(k in clean_s for k in ["石籠", "箱籠"]):
        return "石籠護坡"
    if any(k in clean_s for k in ["噴凝土", "噴漿"]):
        return "噴凝土護坡"
    if ("錨" in clean_s or "排樁" in clean_s) and "牆" in clean_s:
        return "預力地錨RC擋土牆"
    if "錨" in clean_s or "格梁" in clean_s:
        return "岩(地)錨"
    if "格框" in clean_s or "格子梁" in clean_s:
        return "RC格框(格子梁)"
    if "擋土牆" in clean_s or "RC牆" in clean_s:
        return "RC擋土牆"
    return "自然邊坡"

def generate_doc_report(data: dict, photo_bytes_list=None) -> bytes:
    """產製與公路局官方 ODT 格式 100% 吻合、無任何欄位錯位之標準 .doc"""

    # 1. 檢測類別勾選
    t_val = str(data.get("type", "定期檢測"))
    chk_reg = "■" if "定期" in t_val else "□"
    chk_spe = "■" if "特別" in t_val else "□"

    # 2. 里程方向勾選
    d_val = str(data.get("direction", ""))
    chk_north = "■" if any(x in d_val for x in ["北", "西"]) else "□"
    chk_south = "■" if any(x in d_val for x in ["南", "東"]) else "□"

    # 3. 地質狀況勾選
    g_val = str(data.get("geo", "土層邊坡"))
    chk_soil = "■" if "土層" in g_val else "□"
    chk_rock = "■" if "岩層" in g_val else "□"
    chk_gravel = "■" if "礫石" in g_val else "□"
    chk_other_geo = "■" if "其他" in g_val else "□"

    # 4. 地下水排水湧水狀況勾選
    w_val = str(data.get("water", "乾燥"))
    chk_dry = "■" if "乾燥" in w_val else "□"
    chk_wet = "■" if "濕潤" in w_val else "□"
    chk_surf = "■" if "表面水" in w_val else "□"
    chk_spring = "■" if "湧水" in w_val else "□"

    # 5. 排(洩)水管狀況勾選
    dr_val = str(data.get("drain", "正常"))
    chk_drain_ok = "■" if "正常" in dr_val else "□"
    chk_drain_block = "■" if "阻塞" in dr_val else "□"

    # 6. 規範字典取值（具備強固預設值，絕對禁止 None 出現）
    title_text = str(data.get("title") or "表A3-1 自然邊坡")
    cat_header = str(data.get("category_col_header") or "設施類別")
    cat_name = str(data.get("category_name") or "(請自填)")
    dim_title = str(data.get("dim_title") or "設施形狀")
    dim_h_label = str(data.get("dim_h_label") or "高度")
    dim_w_label = str(data.get("dim_w_label") or "設施面寬")
    height_val = str(data.get("height") or "—")
    slope_val = str(data.get("slope") or "—")
    width_val = str(data.get("width") or "—")
    remark_val = str(data.get("remark") or "")

    # 組裝 6 欄位設施檢測項目列 (第一欄類別垂直合併，最末欄注意事項垂直合併)
    items_rows_html = ""
    check_rows = data.get("check_rows", [])
    total_items = len(check_rows)

    for idx, (iname, iact, ires, idesc) in enumerate(check_rows):
        first_row_td = ""
        last_row_td = ""

        # 首列跨列合併
        if idx == 0:
            first_row_td = f"""<td rowspan="{total_items}" style="border:1px solid #000; text-align:center; vertical-align:middle; font-weight:bold; width:9%; letter-spacing:2px;">{cat_name}</td>"""
            last_row_td = f"""<td rowspan="{total_items}" style="border:1px solid #000; vertical-align:top; font-size:11px; width:19%; line-height:1.42; padding:5px;">
一、檢查結果應記錄(正常)(○)、(異常)(×)、(無此項)(／)；發現異常情形，應於備註欄註記。<br><br>
二、設施異常時，應即設法處理，或將檢查表簽請核辦。
</td>"""

        items_rows_html += f"""
        <tr>
            {first_row_td}
            <td style="border:1px solid #000; font-size:12px; padding:4px 5px;">{iname}</td>
            <td style="border:1px solid #000; font-size:12px; padding:4px 5px;">{iact}</td>
            <td style="border:1px solid #000; text-align:center; font-size:15px; font-weight:bold; width:8%;">{ires}</td>
            <td style="border:1px solid #000; font-size:12px; padding:4px 5px; width:15%;">{idesc}</td>
            {last_row_td}
        </tr>
        """

    # 附件相片表 HTML (表 A3-10)
    photos_attachment_html = ""
    if photo_bytes_list:
        photo_tables = ""
        for p_idx, p_bytes in enumerate(photo_bytes_list, 1):
            b64_str = base64.b64encode(p_bytes).decode()
            photo_tables += f"""
            <table style="width:100%; border-collapse:collapse; margin-top:8px; page-break-inside:avoid;">
                <tr>
                    <td style="border:1px solid #000; width:10%; text-align:center; font-weight:bold;">編號</td>
                    <td style="border:1px solid #000; width:20%; font-weight:bold; text-align:center;">紀 錄 圖 片<br>(請自填)</td>
                    <td style="border:1px solid #000; text-align:center; padding:10px;">
                        <img src="data:image/jpeg;base64,{b64_str}" style="max-width:540px; max-height:400px;" />
                    </td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; text-align:center; font-weight:bold;">說 明</td>
                    <td colspan="2" style="border:1px solid #000; padding:6px;">{data.get('code')} 現地巡查記錄照片 {p_idx}</td>
                </tr>
            </table>
            """

        photos_attachment_html = f"""
        <div style="page-break-before:always; margin-top:20px;"></div>
        <div style="text-align:center; font-size:16px; font-weight:bold; margin-bottom:5px;">
            表A3-10邊坡、護坡與擋土設施（{chk_reg}定期{chk_spe}特別）檢測附件圖片說明表
        </div>
        <div style="font-size:12px; margin-bottom:4px;">
            口卡編號：{data.get('code')}；日期：{data.get('date')}；天氣狀況(晴/陰/雨)：{data.get('weather')}
        </div>
        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="border:1px solid #000; width:12%; text-align:center; font-weight:bold; background:#fafafa;">養護單位</td>
                <td style="border:1px solid #000; width:38%;">{data.get('unit', '南澳工務段')}</td>
                <td style="border:1px solid #000; width:12%; text-align:center; font-weight:bold; background:#fafafa;">檢測位置</td>
                <td style="border:1px solid #000; width:38%;">{data.get('location')}</td>
            </tr>
        </table>
        {photo_tables}
        <table style="width:100%; border-collapse:collapse; margin-top:6px;">
            <tr>
                <td style="border:1px solid #000; width:10%; font-weight:bold; text-align:center;">備 註</td>
                <td style="border:1px solid #000; font-size:11px; padding:4px 6px;">1.如有需要，可另外加頁以容納更多圖片。2.記錄照片應於上次檢查時所拍攝之同一位置拍攝。</td>
            </tr>
            <tr>
                <td colspan="2" style="border:1px solid #000; padding:6px 12px;">
                    <span style="font-weight:bold;">檢查人員：</span>{data.get('inspector')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    <span style="font-weight:bold;">單位主管：</span>{data.get('supervisor', '')}
                </td>
            </tr>
        </table>
        """

    # 完整公務 HTML 文件架構（頂部嚴格鎖定 8 欄位佈局，保證不超出頁緣邊界）
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title_text}</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 1.5cm 1.5cm 1.5cm 1.5cm;
        }}
        body {{
            font-family: "標楷體", "DFKai-SB", "PMingLiU", serif;
            color: #000;
            line-height: 1.35;
            margin: 0;
            padding: 0;
        }}
        table {{
            width: 100% !important;
            max-width: 100% !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            margin: 0;
        }}
        td, th {{
            border: 1px solid #000;
            padding: 4px 4px;
            font-size: 12px;
            word-wrap: break-word;
            overflow: hidden;
        }}
        .header-title {{
            font-size: 17.5px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 6px;
        }}
        .meta-line {{
            font-size: 12px;
            margin-bottom: 5px;
            white-space: nowrap;
        }}
    </style>
</head>
<body>

    <!-- 表頭抬頭 -->
    <div class="header-title">{title_text}（{chk_reg}定期{chk_spe}特別）檢測表</div>
    
    <!-- 口卡編號、日期、天氣 (單行緊湊排版) -->
    <div class="meta-line">
        口卡編號：{data.get('code')}；日期：{data.get('date')}；天氣狀況(晴/陰/雨)：{data.get('weather')}
    </div>

    <!-- 上半部鎖定 8 欄網格 (每列 colspan 加總皆嚴格等於 8) -->
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

        <!-- 列 1: 養護單位 (1 + 7 = 8) -->
        <tr>
            <td style="text-align:center; font-weight:bold;">養護單位</td>
            <td colspan="7">{data.get('unit', '南澳工務段')}</td>
        </tr>

        <!-- 列 2: 檢查位置與里程 (1 + 3 + 1 + 3 = 8) -->
        <tr>
            <td style="text-align:center; font-weight:bold;">檢查位置</td>
            <td colspan="3">{data.get('location')}</td>
            <td style="text-align:center; font-weight:bold;">里 程</td>
            <td colspan="3">{chk_north}北下(西向)、{chk_south}南上(東向)</td>
        </tr>

        <!-- 列 3: 地質狀況 (跨列現場狀況 1 + 1 + 6 = 8) -->
        <tr>
            <td rowspan="5" style="text-align:center; vertical-align:middle; font-weight:bold; letter-spacing:4px;">現 場<br>狀 況</td>
            <td style="font-weight:bold;">地質狀況</td>
            <td colspan="6">{chk_soil}土層邊坡 {chk_rock}岩層邊坡 {chk_gravel}礫石層邊坡 {chk_other_geo}其他地質，說明：</td>
        </tr>

        <!-- 列 4: 邊坡/設施形狀 (1 + 1 + 1 + 1 + 1 + 1 + 1 = 7，加上 rowspan 1 = 8) -->
        <tr>
            <td style="font-weight:bold;">{dim_title}</td>
            <td style="font-weight:bold; text-align:center;">{dim_h_label}</td>
            <td>{height_val} 公尺</td>
            <td style="font-weight:bold; text-align:center;">坡度(坡距比)</td>
            <td style="text-align:center;">{slope_val}</td>
            <td style="font-weight:bold; text-align:center;">{dim_w_label}</td>
            <td>{width_val} 公尺</td>
        </tr>

        <!-- 列 5: 地下水狀況第 1 列 (地下水狀況跨2列 1 + 排水湧水 1 + 湧水勾選 1 + 湧水位置 1 + 空白 1 + 湧水量 1 + 數值 1 = 7，加現場狀況 = 8) -->
        <tr>
            <td rowspan="2" style="font-weight:bold; vertical-align:middle;">地下水狀況</td>
            <td style="font-weight:bold; text-align:center;">排水湧水</td>
            <td>{chk_dry}乾燥 {chk_wet}濕潤<br>{chk_surf}表面水 {chk_spring}湧水</td>
            <td style="font-weight:bold; text-align:center;">湧水位置</td>
            <td></td>
            <td style="font-weight:bold; text-align:center;">湧水量</td>
            <td>約&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;公升/分</td>
        </tr>

        <!-- 列 6: 地下水狀況第 2 列 (湧水之地質狀況 2 + 空白 1 + 調查時間 1 + 月份 1 + 降雨日 2 = 7，加現場狀況 = 8) -->
        <tr>
            <td colspan="2" style="font-weight:bold; text-align:center;">湧水之地質狀況</td>
            <td></td>
            <td style="font-weight:bold; text-align:center;">調查時間</td>
            <td>{data.get('survey_month', '11')}月</td>
            <td colspan="2">降雨後 {data.get('rain_days', '3')} 日</td>
        </tr>

        <!-- 列 7: 排(洩)水管 (1 + 6 = 7，加現場狀況 = 8) -->
        <tr>
            <td style="font-weight:bold;">排(洩)水管</td>
            <td colspan="6">{chk_drain_ok}正常 {chk_drain_block}阻塞</td>
        </tr>

        <!-- 列 8: 監測系統 (1 + 7 = 8) -->
        <tr>
            <td style="text-align:center; font-weight:bold;">監測系統</td>
            <td colspan="7">■無 □有，項目說明：</td>
        </tr>

        <!-- 列 9: 監測情形 (1 + 3 + 1 + 3 = 8) -->
        <tr>
            <td style="text-align:center; font-weight:bold;">監測情形</td>
            <td colspan="3">□無 ■有：□自行量測 ■委外量測</td>
            <td style="text-align:center; font-weight:bold;">監測頻率</td>
            <td colspan="3">□每月 □每季 □每半年 ■每年 □其他</td>
        </tr>

        <!-- 列 10: 災害歷史 (1 + 1 + 2 + 1 + 3 = 8) -->
        <tr>
            <td style="text-align:center; font-weight:bold;">災害歷史</td>
            <td style="font-weight:bold; text-align:center;">以往災害</td>
            <td colspan="2">■無 □有</td>
            <td style="text-align:center; font-weight:bold;">鄰近災害</td>
            <td colspan="3">■無 □有，說明：</td>
        </tr>
    </table>

    <!-- 下半部 6 欄位設施檢測項目表 (緊密連接，外緣對齊) -->
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
                <td>{cat_header}</td>
                <td>檢查項目</td>
                <td>養護措施</td>
                <td>檢查結果</td>
                <td>處理情形</td>
                <td>注意事項</td>
            </tr>
        </thead>
        <tbody>
            {items_rows_html}
        </tbody>
        <tr>
            <td style="text-align:center; font-weight:bold;">備 註</td>
            <td colspan="5" style="font-size:11.5px; padding:4px 6px;">{remark_val}</td>
        </tr>
        <tr>
            <td colspan="6" style="padding:6px 10px;">
                <span style="font-weight:bold;">檢測人員：</span>{data.get('inspector')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span style="font-weight:bold;">單位主管：</span>{data.get('supervisor', '')}
            </td>
        </tr>
    </table>

    <!-- 表 A3-10 附件相片表 -->
    {photos_attachment_html}

</body>
</html>"""
    return full_html.encode("utf-8")