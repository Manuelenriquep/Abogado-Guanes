import requests
from bs4 import BeautifulSoup

url = "https://www.floridablanca.gov.co/Transparencia/Normatividad"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

try:
    res = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {res.status_code}")
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.find_all("a")
    print(f"Total links found: {len(links)}")
    for link in links[:20]:
        print(f"Link: {link.get_text().strip()} | Href: {link.get('href')}")
except Exception as e:
    print(f"Error: {e}")
