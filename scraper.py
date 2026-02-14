import requests
from bs4 import BeautifulSoup
import json
import time
import re

def extract_features(text):
    # Cerca numeri seguiti da parole chiave (mq, camere, bagni)
    mq = re.search(r'(\d+)\s*(?:mq|metri quadri)', text, re.I)
    camere = re.search(r'(\d+)\s*(?:camere|letto|locali)', text, re.I)
    bagni = re.search(r'(\d+)\s*(?:bagni|servizi)', text, re.I)
    
    return {
        "mq": int(mq.group(1)) if mq else 0,
        "camere": int(camere.group(1)) if camere else 0,
        "bagni": int(bagni.group(1)) if bagni else 0
    }

def extract_price_globally(soup):
    text = soup.get_text(separator=' ')
    patterns = [r'(?:€|EUR)\s?([\d\.]+)', r'([\d\.]+)\s?(?:€|EUR)']
    found_prices = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            clean_m = m.replace('.', '').replace(',', '')
            if clean_m.isdigit() and 10000 < int(clean_m) < 50000000:
                found_prices.append(int(clean_m))
    return min(found_prices) if found_prices else 0

def scrape_advanced():
    with open('immobili.json', 'r', encoding='utf-8') as f:
        properties = json.load(f)
    
    full_db = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

    print("--- AVVIO SCRAPING ANALITICO ---")
    for p in properties:
        try:
            res = requests.get(p['u'], headers=headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = soup.get_text()
            
            p['p_val'] = extract_price_globally(soup)
            features = extract_features(page_text)
            p.update(features) # Aggiunge mq, camere, bagni
            
            img_tag = soup.find('meta', property='og:image')
            p['img'] = img_tag['content'] if img_tag else ""
            
            full_db.append(p)
            print(f"✔ {p['t'][:30]}... | {p['p_val']}€ | {p['camere']} Camere | {p['mq']}mq")
            time.sleep(1)
        except Exception as e:
            print(f"✘ Errore: {e}")

    with open('immobili_full.json', 'w', encoding='utf-8') as f:
        json.dump(full_db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scrape_advanced()