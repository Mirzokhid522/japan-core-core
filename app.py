import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify

app = Flask(__name__)

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID", "YOUR_ESTAT_APP_ID")
ESTAT_URL = "https://api.e-stat.go.jp/rest/3.0/app/getStatsData"

def fetch_yoy_and_index(area_code):
    params = {
        "appId": ESTAT_APP_ID,
        "lang": "E",
        "statsDataId": "0004052037",
        "metaGetFlg": "N",
        "cntGetFlg": "N",
        "cdArea": area_code,
        "cdCat01": "0178",  # Core-Core CPI
        "limit": "100000"   # Increased limit to capture recent 2025/2026 records
    }
    
    response = requests.get(ESTAT_URL, params=params)
    if response.status_code != 200:
        print(f"API Error for area {area_code}: Status code {response.status_code}")
        return []
    
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return []
    
    index_2025 = {}
    index_2026 = {}
    
    for elem in root.iter():
        if elem.tag.endswith('VALUE') or elem.tag.endswith('value'):
            time_str = elem.attrib.get('time', '')
            tab = elem.attrib.get('tab', '')
            if tab == '1' and elem.text:
                try:
                    val = float(elem.text)
                    if time_str.startswith('2025'):
                        month = time_str[6:8]
                        index_2025[month] = val
                    elif time_str.startswith('2026'):
                        month = time_str[6:8]
                        index_2026[month] = val
                except ValueError:
                    continue
                    
    data = []
    month_names = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", 
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", 
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    
    for m in sorted(index_2026.keys()):
        val_26 = index_2026[m]
        val_25 = index_2025.get(m)
        yoy_change = None
        if val_25 and val_25 > 0:
            yoy_change = round(((val_26 - val_25) / val_25) * 100, 2)
            
        data.append({
            "month": m,
            "label": f"{month_names.get(m, m)} 2026",
            "index": val_26,
            "yoy": yoy_change
        })
        
    print(f"Successfully processed {len(data)} records for 2026 (area {area_code})")
    return data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/cpi")
def get_cpi_api():
    return jsonify({
        "japan": fetch_yoy_and_index("00000"),
        "tokyo": fetch_yoy_and_index("13100")
    })

if __name__ == "__main__":
    app.run(debug=True, port=2025)