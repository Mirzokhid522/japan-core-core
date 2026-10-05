import os
import requests
import xml.etree.ElementTree as ET

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID", "YOUR_ESTAT_APP_ID")
ESTAT_URL = "https://api.e-stat.go.jp/rest/3.0/app/getStatsData"

def test_fetch_core_core(area_code, area_name):
    params = {
        "appId": ESTAT_APP_ID,
        "lang": "E",
        "statsDataId": "0004052037",
        "metaGetFlg": "N",
        "cntGetFlg": "N",
        "cdArea": area_code,
        "cdCat01": "0178",  # Code for "All items, less fresh food and energy"
        "limit": "100"
    }
    
    print(f"\nTesting Core-Core CPI fetch for {area_name} (Area: {area_code})...")
    response = requests.get(ESTAT_URL, params=params)
    
    if response.status_code != 200:
        print(f"❌ API Error: Status code {response.status_code}")
        return
    
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return
    
    count_2026 = 0
    for elem in root.iter():
        if elem.tag.endswith('VALUE') or elem.tag.endswith('value'):
            time_str = elem.attrib.get('time', '')
            if time_str.startswith('2026'):
                count_2026 += 1
                print(f"  [Found] Time: {time_str} | Tab: {elem.attrib.get('tab')} | Value: {elem.text}")
                
    print(f"Result: Successfully pulled {count_2026} records for 2026 in {area_name}.")

if __name__ == "__main__":
    test_fetch_core_core("00000", "Japan (National)")
    test_fetch_core_core("13100", "Tokyo (Ku-bu)")