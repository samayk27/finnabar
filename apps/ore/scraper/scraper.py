from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import requests
import json
import re

RELEVANT_KEYWORDS = [
    "annual", "report", "quarterly", "results", "investor",
    "presentation", "financial", "statement", "earnings",
    "fy", "q1", "q2", "q3", "q4", "half", "yearly"
]

IRRELEVANT_KEYWORDS = [
    "brochure", "product", "catalog", "catalogue", "manual",
    "policy", "certificate", "form", "application",
    "environmental", "clearance", "fly-ash", "fly_ash",
    "sustainability", "esop", "agm-notice", "agm_notice",
    "postal-ballot", "voting", "court-convened",
    "monitoring-report", "csr"
]

def is_relevant_pdf(url):
    filename = urlparse(url).path.lower()
    
    has_relevant = any(kw in filename for kw in RELEVANT_KEYWORDS)
    has_irrelevant = any(kw in filename for kw in IRRELEVANT_KEYWORDS)
    
    return has_relevant and not has_irrelevant

def scrape_ore_json(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    pdf_links = set()
    
    def extract_links(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.lower().endswith('.pdf'):
                    absolute_url = urljoin(url, value)
                    if is_relevant_pdf(absolute_url):
                        pdf_links.add(absolute_url)
                else:
                    extract_links(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_links(item)

    extract_links(data)
    return list(pdf_links)


def scrape_ore_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(url, href)
        
        path = urlparse(absolute_url).path.lower()
        if not path.endswith('.pdf'):
            continue
        if not is_relevant_pdf(absolute_url):
            continue
            
        pdf_links.add(absolute_url)
    
    return list(pdf_links)

def main():
    with open('../links.json', 'r') as f:
        links = json.load(f)
    all_data = []
    for company, items in links.items():
        urls = [item for item in items if isinstance(item, str)]
        type_dict = next((item for item in items if isinstance(item, dict)), {})
        scrape_type = type_dict.get("type", "html")
        
        company_links = []
        for url in urls:
            if scrape_type == "json":
                company_links.extend(scrape_ore_json(url))
            else:
                company_links.extend(scrape_ore_html(url))
        
        all_data.append({company: company_links})


    with open('ore_data.json', 'w') as f:
        json.dump(all_data, f, indent=4)
        
if __name__ == "__main__":    
    main()