import os
import requests
import xml.etree.ElementTree as ET

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID", "YOUR_ESTAT_APP_ID")
ESTAT_URL = "https://api.e-stat.go.jp/rest/3.0/app/getStatsData"

def test_api():
    params = {
        "appId": ESTAT_APP_ID,
        "lang": "E",
        "statsDataId": "0004052037",
        "metaGetFlg": "N",
        "cntGetFlg": "N",
        "cdArea": "00000",
        "limit": "100"
    }
    
    print(f"Sending request to e-Stat API for area 00000...")
    response = requests.get(ESTAT_URL, params=params)
    print(f"HTTP Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print("API connection failed.")
        return

    root = ET.fromstring(response.content)
    
    # Check total values found
    values = root.findall(".//{*}VALUE")
    if not values:
        values = root.findall(".//{*}value")
    
    print(f"Total <VALUE> elements found in response: {len(values)}")
    
    # Print sample attributes and text for the first 5 records
    print("\n--- First 5 Records Sample ---")
    for elem in values[:5]:
        print(f"Attribs: {elem.attrib} | Text: {elem.text}")

    # Check for any 2026 data
    count_2026 = 0
    for elem in values:
        time_val = elem.attrib.get('time', '')
        if '2026' in time_val:
            count_2026 += 1
            if count_2026 <= 5:
                print(f"Found 2026 Record -> Time: {time_val}, Cat01: {elem.attrib.get('cat01')}, Tab: {elem.attrib.get('tab')}, Value: {elem.text}")
                
    print(f"\nTotal records matching '2026' in this batch: {count_2026}")

if __name__ == "__main__":
    if ESTAT_APP_ID == "YOUR_ESTAT_APP_ID":
        print("⚠️ Please set your ESTAT_APP_ID environment variable first!")
    else:
        test_api()