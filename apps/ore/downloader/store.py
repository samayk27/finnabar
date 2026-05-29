from urllib.parse import urlparse

import requests
import os

def download(data):
    for company_data in data:
        for company, links in company_data.items():
            company_dir = os.path.join('downloads', company)
            os.makedirs(company_dir, exist_ok=True)
            
            for link in links:
                filename = os.path.basename(urlparse(link).path)
                file_path = os.path.join(company_dir, filename)
                if os.path.exists(file_path):
                    print(f"File already exists: {file_path}")
                    continue
                try:
                    response = requests.get(link, stream=True)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Downloaded: {file_path}")
                except Exception as e:
                    print(f"Failed to download {link}: {e}")