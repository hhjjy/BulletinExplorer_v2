from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import aiohttp
import json, os, requests, psycopg2, traceback, time, telegram, copy, pprint, asyncio, functools,sys

# #NTUST_LANG1 = "https://lc.ntust.edu.tw/p/403-1070-1053-1.php?Lang=zh-tw"
# NTUST_INSIDE = "https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php?Lang=zh-tw"
# NTUST_OUTSIDE = "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw"
# NTUST_LANG = "https://lc.ntust.edu.tw/app/index.php?Action=mobilercglist"#
# NTUST_IAC = "https://iac.ntust.edu.tw/p/403-1061-1147-1.php?Lang=zh-tw"
# NTUST_OAA = "https://www.academic.ntust.edu.tw/p/403-1048-1405-1.php?Lang=zh-tw"
    # "台科大教學發展中心": "https://ctld.ntust.edu.tw/p/403-1051-1430-1.php?Lang=zh-tw",
    # "@@台科大總務處": "https://www.general.ntust.edu.tw/p/403-1054-5-1.php?Lang=zh-tw",
    # "@@台科大圖書館": "https://library.ntust.edu.tw/p/403-1049-1-1.php?Lang=zh-tw",
    # "@@台科大人事室": "https://www.personnel.ntust.edu.tw/p/403-1066-1-1.php?Lang=zh-tw",
    # "@@台科大體育室": "https://www.sport.ntust.edu.tw/p/403-1069-1475-1.php?Lang=zh-tw",
    # teach 
    # "台科大電資學院":   "https://www.ceecs.ntust.edu.tw/p/403-1001-1-1.php?Lang=zh-tw",
    # "台科大工程學院":   "https://www.ce.ntust.edu.tw/p/403-1024-1037-1.php?Lang=zh-tw",
    # "台科大管理學院":   "https://www.management.ntust.edu.tw/p/403-1031-7-1.php?Lang=zh-tw",
    # "台科大設計學院":   "https://dcollege.ntust.edu.tw/p/403-1028-491-1.php?Lang=zh-tw",
    # "台科大人文社會學院":"https://web.lass.ntust.edu.tw/p/403-1029-475-1.php?Lang=zh-tw",
    # "台科大應用科技學院":"https://honor.ntust.edu.tw/p/403-1030-2-1.php?Lang=zh-tw",
    # "台科大通識教育中心":"https://cla.ntust.edu.tw/p/403-1076-1476-1.php?Lang=zh-tw",
    # "台科大產學創新學院":"https://innc.ntust.edu.tw/p/403-1111-2122-1.php?Lang=zh-tw",

    # "台科大永續發展與校務研究中心": "https://po.ntust.edu.tw/p/403-1059-763-1.php?Lang=zh-tw",




   
main_method = {
    # main 
    "台科大語言中心": "https://lc.ntust.edu.tw/app/index.php?Action=mobilercglist",
    "台科大教務處": "https://www.academic.ntust.edu.tw/p/403-1048-1405-1.php?Lang=zh-tw",
    "台科大主計室": "https://www.accounting.ntust.edu.tw/p/403-1067-1-1.php?Lang=zh-tw",
    "台科大電子計算中心": "https://www.cc.ntust.edu.tw/p/403-1050-1426-1.php?Lang=zh-tw",
    "台科大產學營運處": "https://iac.ntust.edu.tw/p/403-1061-1147-1.php?Lang=zh-tw",
    "台科大主校網": "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw",
    "台科大國際事務處": "https://www.oia.ntust.edu.tw/p/403-1060-1-1.php?Lang=zh-tw",
    "台科大研發處": "https://www.rd.ntust.edu.tw/p/403-1055-19-1.php?Lang=zh-tw",
    "台科大秘書室": "https://www.secretariat.ntust.edu.tw/p/403-1063-2-1.php?Lang=zh-tw",
    "台科大環安室": "https://she.ntust.edu.tw/p/403-1068-1497-1.php?Lang=zh-tw",
    "台科大學務處": "https://student.ntust.edu.tw/p/403-1053-1435-1.php?Lang=zh-tw",
    "台科大臺巴計畫辦公室": "https://uptp-office.ntust.edu.tw/p/403-1116-2155-1.php?Lang=zh-tw",}

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


class Scraper(ABC):
    def __init__(self, url, data):
        self.url = url
        self.data = data

    @abstractmethod
    def scrape(self):
        pass

class ScraperFactory:
    @staticmethod
    def get_scraper(key):
        url = main_method.get(key)
        if not url:
            raise ValueError(f"No URL found for the key: {key}")
        
        if key == "台科大語言中心":
            data = {
                "Rcg": "1053",
                "Op": "loadpage",
                "Page": "1"
            }
            return NTUSTLanguageCenterScraper(url, data)
        else:
            data = {}
            return NTUSTScraper(url, data)
        

class NTUSTScraper(Scraper):
    def __init__(self, url, data):
        self.url = url
        self.data = data

    async def scrape(self):
        print("Scraping NTUST" + self.url + "...")
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, data=self.data) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find("table")
                    tbody = table.find("tbody")
                    try:
                        for row in tbody.find_all("tr"):
                            publisher = "N/A"
                            title = row.find("td", {"data-th": "標題"}).get_text(strip=True)
                            a_tag = row.find("a")
                            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
                            content = ""
                            if url is not None:
                                async with session.get(url) as webpage:
                                    if webpage.status == 200:
                                        page_html = await webpage.text()
                                        page_soup = BeautifulSoup(page_html, 'html.parser')
                                        paragraphs = page_soup.find_all("p")
                                        for p in paragraphs:
                                            content += p.get_text(strip=True)
                            yield {"publisher": publisher, "title": title, "url": url, "content": content}
                    except Exception as e:
                        print("ERROR:", e)
                else:
                    print(f"Failed: {response.status}")



        # soup = BeautifulSoup(response.content, 'html.parser')
        # table = soup.find("table")# 找table 標籤 
        # thead = table.find("thead")# 從table 找第一個匹配的
        # tbody = table.find("tbody")# 從table找第一個匹配的
        # # # Process the table one row at a time
        
        # for row in tbody.find_all("tr"):
        #     data_row = []       
        #     publisher = "None"#台科大" + row.find("td",{"data-th":"發佈單位"}).get_text(strip=True)
        #     title = row.find("td",{"data-th":"標題"}).get_text(strip=True)
        #     a_tag = row.find("a")
        #     url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
        #     content = "" # 從url去爬連結內文
        #     if url != None:
        #         webpage = requests.get(url)
        #         soup = BeautifulSoup(webpage.content, 'html.parser')
        #         paragraphs = soup.find_all("p")
        #         for p in paragraphs:
        #             content += p.get_text(strip=True)
        #     yield {"publisher":publisher,"title":title,"url":url,"content":content}


# 台科大語言中心爬蟲
class NTUSTLanguageCenterScraper(Scraper):
    def __init__(self, url, data):
        self.url = url
        self.data = data

    
    async def scrape(self):
        print("Scraping NTUST Language Center...")
        response = requests.post(self.url, headers=headers, data=self.data)
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        items = soup.find_all('div', class_='mtitle')
        result = []
        for item in items:
            title_tag = item.find('a')
            title = ""
            if title_tag:
                title = title_tag.get_text(strip=True)
                url = title_tag['href']
                publisher = "台科大語言中心"
                content = ""
                if url:
                    title = title_tag.get_text(strip=True) 
                    # 取得標題的內文
                    webpage = requests.get(url)
                    webpage_soup = BeautifulSoup(webpage.content, 'html.parser')
                    div = webpage_soup.find('div',attrs={'class':'mpgdetail'})
                    p_tags = div.find_all('p')
                    for p in p_tags:
                        content += p.get_text(strip=True)
                yield {"publisher":publisher,"title":title,"url":url,"content":content}  








# url_main_method = {
#     # main 
#     "台科大教務處": "https://www.academic.ntust.edu.tw/p/403-1048-1405-1.php?Lang=zh-tw",
#     "台科大主計室": "https://www.accounting.ntust.edu.tw/p/403-1067-1-1.php?Lang=zh-tw",
#     "台科大電子計算中心": "https://www.cc.ntust.edu.tw/p/403-1050-1426-1.php?Lang=zh-tw",
#     "台科大教學發展中心": "https://ctld.ntust.edu.tw/p/403-1051-1430-1.php?Lang=zh-tw",
#     "台科大總務處": "https://www.general.ntust.edu.tw/p/403-1054-5-1.php?Lang=zh-tw",
#     "台科大產學營運處": "https://iac.ntust.edu.tw/p/403-1061-1147-1.php?Lang=zh-tw",
#     "台科大語言中心": "https://lc.ntust.edu.tw/p/403-1070-1053-1.php?Lang=zh-tw",
#     "台科大圖書館": "https://library.ntust.edu.tw/p/403-1049-1-1.php?Lang=zh-tw",
#     "台科大主校網": "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw",
#     "台科大國際事務處": "https://www.oia.ntust.edu.tw/p/403-1060-1-1.php?Lang=zh-tw",
#     "台科大人事室": "https://www.personnel.ntust.edu.tw/p/403-1066-1-1.php?Lang=zh-tw",
#     "台科大永續發展與校務研究中心": "https://po.ntust.edu.tw/p/403-1059-763-1.php?Lang=zh-tw",
#     "台科大研發處": "https://www.rd.ntust.edu.tw/p/403-1055-19-1.php?Lang=zh-tw",
#     "台科大秘書室": "https://www.secretariat.ntust.edu.tw/p/403-1063-2-1.php?Lang=zh-tw",
#     "台科大環安室": "https://she.ntust.edu.tw/p/403-1068-1497-1.php?Lang=zh-tw",
#     "台科大體育室": "https://www.sport.ntust.edu.tw/p/403-1069-1475-1.php?Lang=zh-tw",
#     "台科大學務處": "https://student.ntust.edu.tw/p/403-1053-1435-1.php?Lang=zh-tw",
#     "台科大臺巴計畫辦公室": "https://uptp-office.ntust.edu.tw/p/403-1116-2155-1.php?Lang=zh-tw",
#     # teach 
#     "台科大電資學院":   "https://www.ceecs.ntust.edu.tw/p/403-1001-1-1.php?Lang=zh-tw",
#     "台科大工程學院":   "https://www.ce.ntust.edu.tw/p/403-1024-1037-1.php?Lang=zh-tw",
#     "台科大管理學院":   "https://www.management.ntust.edu.tw/p/403-1031-7-1.php?Lang=zh-tw",
#     "台科大設計學院":   "https://dcollege.ntust.edu.tw/p/403-1028-491-1.php?Lang=zh-tw",
#     "台科大人文社會學院":"https://web.lass.ntust.edu.tw/p/403-1029-475-1.php?Lang=zh-tw",
#     "台科大應用科技學院":"https://honor.ntust.edu.tw/p/403-1030-2-1.php?Lang=zh-tw",
#     "台科大通識教育中心":"https://cla.ntust.edu.tw/p/403-1076-1476-1.php?Lang=zh-tw",
#     "台科大產學創新學院":"https://innc.ntust.edu.tw/p/403-1111-2122-1.php?Lang=zh-tw",
# }

# url_other_method ={
#     "台科大雙語辦公室": "https://ntust-obi-backend-srv-bfb5f44ce574.herokuapp.com/api/articles",
# }