from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import json, os, re, requests, psycopg2, traceback, time, telegram, copy, pprint, asyncio, functools, sys
from ProxyManager import *

# format :{site}/p/{bulletin_page_number}-{catogriy}-{CertainID}-1.php?Lang=zh-tw
url_main_method = {
    # main 
    "台科大教務處": "https://www.academic.ntust.edu.tw/p/403-1048-1405-1.php?Lang=zh-tw",
    "台科大主計室": "https://www.accounting.ntust.edu.tw/p/403-1067-1-1.php?Lang=zh-tw",
    "台科大電子計算中心": "https://www.cc.ntust.edu.tw/p/403-1050-1426-1.php?Lang=zh-tw",
    "台科大教學發展中心": "https://ctld.ntust.edu.tw/p/403-1051-1430-1.php?Lang=zh-tw",
    "台科大總務處": "https://www.general.ntust.edu.tw/p/403-1054-5-1.php?Lang=zh-tw",
    "台科大產學營運處": "https://iac.ntust.edu.tw/p/403-1061-1147-1.php?Lang=zh-tw",
    "台科大語言中心": "https://lc.ntust.edu.tw/p/403-1070-1053-1.php?Lang=zh-tw",
    "台科大圖書館": "https://library.ntust.edu.tw/p/403-1049-1-1.php?Lang=zh-tw",
    "台科大主校網": "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw",
    "台科大國際事務處": "https://www.oia.ntust.edu.tw/p/403-1060-1-1.php?Lang=zh-tw",
    "台科大人事室": "https://www.personnel.ntust.edu.tw/p/403-1066-1-1.php?Lang=zh-tw",
    "台科大永續發展與校務研究中心": "https://po.ntust.edu.tw/p/403-1059-763-1.php?Lang=zh-tw",
    "台科大研發處": "https://www.rd.ntust.edu.tw/p/403-1055-19-1.php?Lang=zh-tw",
    "台科大秘書室": "https://www.secretariat.ntust.edu.tw/p/403-1063-2-1.php?Lang=zh-tw",
    "台科大環安室": "https://she.ntust.edu.tw/p/403-1068-1497-1.php?Lang=zh-tw",
    "台科大體育室": "https://www.sport.ntust.edu.tw/p/403-1069-1475-1.php?Lang=zh-tw",
    "台科大學務處": "https://student.ntust.edu.tw/p/403-1053-1435-1.php?Lang=zh-tw",
    "台科大臺巴計畫辦公室": "https://uptp-office.ntust.edu.tw/p/403-1116-2155-1.php?Lang=zh-tw",
    # teach 
    "台科大電資學院":   "https://www.ceecs.ntust.edu.tw/p/403-1001-1-1.php?Lang=zh-tw",
    "台科大工程學院":   "https://www.ce.ntust.edu.tw/p/403-1024-1037-1.php?Lang=zh-tw",
    "台科大管理學院":   "https://www.management.ntust.edu.tw/p/403-1031-7-1.php?Lang=zh-tw",
    "台科大設計學院":   "https://dcollege.ntust.edu.tw/p/403-1028-491-1.php?Lang=zh-tw",
    "台科大人文社會學院":"https://web.lass.ntust.edu.tw/p/403-1029-475-1.php?Lang=zh-tw",
    "台科大應用科技學院":"https://honor.ntust.edu.tw/p/403-1030-2-1.php?Lang=zh-tw",
    "台科大通識教育中心":"https://cla.ntust.edu.tw/p/403-1076-1476-1.php?Lang=zh-tw",
    "台科大產學創新學院":"https://innc.ntust.edu.tw/p/403-1111-2122-1.php?Lang=zh-tw",
}

url_other_method ={
    "台科大雙語辦公室": "https://ntust-obi-backend-srv-bfb5f44ce574.herokuapp.com/api/articles",
}

# 定義正則表達式模式
pattern = re.compile(r"^(?P<site>.+?)/p/(?P<bulletin_page_number>\d+)-(?P<catogriy>[^-]+)-(?P<CertainID>[^-]+)-1\.php\?Lang=zh-tw$")

# 定義處理函數
def extract_info(url):
    match = pattern.match(url)
    if match:
        site = match.group('site')
        bulletin_page_number = match.group('bulletin_page_number')
        category = match.group('catogriy')
        certain_id = match.group('CertainID')
        return {
            "site": site,
            "bulletin_page_number": bulletin_page_number,
            "category": category,
            "specific_id": certain_id
        }
    else:
        print("No match found for URL:", url)  # 输出没有匹配到的URL，方便调试
        return None

# 定義請求函數
def fetch_page_content(publisher, url, page):
    # 提取信息
    info = extract_info(url)
    # print(info)
    if not info:
        print(f"No match found for URL: {url}")
        return []

    apiurl = f"{info.get('site', None)}/app/index.php?Action=mobilercglist"
    # print(f"Dealing with url: {apiurl} ", end=" ")
    specific_id = info['specific_id']
    proxy_manager = ProxyManager()
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-TW,zh;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    data = {
        'Rcg': specific_id,
        'Op': 'getpartlist',
        'Page': str(page)
    }

    response = requests.post(apiurl, headers=headers, data=data)
    
    results = []
    if response.status_code == 200:
        try:
            # 嘗試解析 JSON
            content = response.json().get('content', None)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                rows = soup.find_all('tr')
                # print(f"\nPage {page} Results:")
                for row in rows[1:]:  # 跳過表頭行
                    date = row.find('td', {'data-th': '日期'}).text.strip()
                    title = row.find('td', {'data-th': '標題'}).text.strip()
                    link = row.find('a')['href']
                    results.append({
                        'title': title,
                        'content': date,
                        'link': link,
                        'publisher': publisher
                    })
                if not results:  # 如果結果為空，保存content
                    save_html_to_file(content, publisher, page)
                    print(f"{publisher} page {page} 沒有結果，保存成 no_results/{publisher}_page_{page}.html")
            else:
                print("No content found in the JSON response")
        except Exception as e:
            error_html = response.text
            save_html_to_file(error_html, publisher, page)
            print(f"{publisher} page {page} 解析失敗，保存成 no_results/{publisher}_page_{page}.html")

    else:
        print(f"请求失败，状态码: {response.status_code}，页数: {page}")

    return results

# 定義保存HTML到文件的函數
def save_html_to_file(html_content, publisher, page):
    directory = "no_results"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f"{publisher}_page_{page}.html")
    
    # 使用BeautifulSoup美化HTML內容
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html_content = soup.prettify()
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(pretty_html_content)

# 測試函數
def test_fetch_page_content():
    test_urls = url_main_method

    for publisher, url in test_urls.items():
        print(f"Testing {publisher}...")
        results = fetch_page_content(publisher, url, 1)
        if results:
            print(f"{publisher} 解析成功，共 {len(results)} 條結果")
        else:
            print(f"{publisher} 沒有結果")

# 運行測試函數
test_fetch_page_content()
