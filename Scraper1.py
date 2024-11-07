import requests
from bs4 import BeautifulSoup
import json

url = "https://lc.ntust.edu.tw/app/index.php?Action=mobilercglist"

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PageLang=zh-tw; _counter=1711599",
    "DNT": "1",
    "Origin": "https://lc.ntust.edu.tw",
    "Referer": "https://lc.ntust.edu.tw/p/403-1070-1053-1.php?Lang=zh-tw",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not?A_Brand";v="99", "Chromium";v="130"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"'
}

data = {
    "Rcg": "1053",
    "Op": "loadpage",
    "Page": "3"
}

response = requests.post(url, headers=headers, data=data)
content = response.text
soup = BeautifulSoup(content, 'html.parser')
items = soup.find_all('div', class_='mtitle')
result = []

for item in items:
    title_tag = item.find('a')
    if title_tag:
        title = title_tag.get_text(strip=True)
        url = title_tag['href']
        data_dict = {
            'publisher': '略過',
            'title': title,
            'url': url,
            'content': '略過'
        }
        result.append(data_dict)

print(json.dumps(result, ensure_ascii=False, indent=4))