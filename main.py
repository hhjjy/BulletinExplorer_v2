from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json,os
import psycopg2
import traceback
db_config = {
    'dbname': 'mydb',
    'user': 'admin',
    'password': '12345',
    'host': '127.0.0.1',
    'port': '5432'
}


NTUST_LANG_URL = "https://lc.ntust.edu.tw/p/403-1070-1053-1.php?Lang=zh-tw"
NTUST_INSIDE_URL = "https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php?Lang=zh-tw"
NTUST_OUTSIDE_URL = "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw"

class Scraper(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrape(self):
        pass
#靜態類別 輸入網址轉類別
class ScraperFactory:
    @staticmethod
    def get_scraper(url):
        # 根據不同的網址返回不同的爬蟲實例
        if "bulletin.ntust.edu.tw" in url:
            return NTUSTBulletinScraper(url)
        elif "lc.ntust.edu.tw" in url:
            return NTUSTLanguageCenterScraper(url)
        elif "www.ntust.edu.tw" in url:
            return NTUSTMajorAnnouncementScraper(url)
        else:
            raise ValueError(f"No scraper found for the given URL: {url}")


# 台科大公佈欄爬蟲
# https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php?Lang=zh-tw
# https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php?Lang=zh-tw
class NTUSTBulletinScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find("table")# 找table 標籤 
        thead = table.find("thead")# 從table 找第一個匹配的
        tbody = table.find("tbody")# 從table找第一個匹配的
        # # Process the table one row at a time
        i = 1
        
        for row in tbody.find_all("tr"):
            data_row = []       
            publisher = "台科大" + row.find("td",{"data-th":"發佈單位"}).get_text(strip=True)
            title = row.find("td",{"data-th":"標題"}).get_text(strip=True)
            a_tag = row.find("a")
            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
            content = "" # 從url去爬連結內文
            if url != None:
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.content, 'html.parser')
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    content += p.get_text(strip=True)
            yield {"publisher":publisher,"title":title,"url":url,"content":content}

# 台科大語言中心爬蟲
class NTUSTLanguageCenterScraper(Scraper):
    def scrape(self):
        print("Scraping NTUST Language Center...")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 添加針對台科大語言中心的爬蟲邏輯
        divs = soup.find_all('div', attrs={'class': 'mtitle'})
        for tag in divs:
            a_tag = tag.find('a')
            url = a_tag.get('href')
            publisher = "台科大語言中心"
            title = ""
            content = ""
            if url:
                title = a_tag.get_text(strip=True) 
                # 取得標題的內文
                webpage = requests.get(url)
                webpage_soup = BeautifulSoup(webpage.content, 'html.parser')
                div = webpage_soup.find('div',attrs={'class':'mpgdetail'})
                p_tags = div.find_all('p')
                for p in p_tags:
                    content += p.get_text(strip=True)
            yield {"publisher":publisher,"title":title,"url":url,"content":content}  

# 台科大校網公布欄爬蟲
class NTUSTMajorAnnouncementScraper(Scraper):
    def scrape(self):
        print("Scraping NTUST Major Announcements...")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = soup.find_all('div', attrs={'class': 'mtitle'})
        title = ""
        url = ""
        content = ""
        publisher = "台科大主校網"
        for t in titles:
            title = t.get_text(strip=True)
            a_tag = t.find('a')
            url = a_tag.get('href')
            yield {"publisher":"publisher","title":title,"url":url,"content":content}  


def save_bulletin_to_db(post):
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
        SELECT * FROM bulletinraw
        WHERE publisher = %s AND title = %s
        """, (post['publisher'], post['title']))
        if cursor.fetchone() is None:
            # 如果數據不存在，則插入新數據
            cursor.execute("""
                INSERT INTO bulletinraw (publisher, title, url, content)
                VALUES (%s, %s, %s, %s)
            """, (post['publisher'], post['title'], post['url'], post['content']))
            connection.commit()
            print( {"message": "Data inserted successfully"})
        else:
            print({"message": "Data already exists. No action taken."})

    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        print({"error": str(Error), "detail": error_traceback})
    finally:
        if connection:
            cursor.close()
            connection.close()

def SaveBulletin(data):
    for row in data:
        result = save_bulletin_to_db(row)
        print(result)

def scrape():
    #should add running event
    # Scrape = ScraperFactory.get_scraper(NTUST_INSIDE_URL)
    # data = Scrape.scrape()
    # SaveBulletin(data)

    Scrape = ScraperFactory.get_scraper(NTUST_LANG_URL)
    data = Scrape.scrape()
    SaveBulletin(data)

    Scrape = ScraperFactory.get_scraper(NTUST_OUTSIDE_URL)
    data = Scrape.scrape()
    SaveBulletin(data)

def print_bulletin_data():
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bulletinraw")
        rows = cursor.fetchall()
        
        # 打印每行數據
        for row in rows:
            print(row)
    
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        # error_traceback = traceback.format_exc()
    # finally:
    #     if connection:
    #         cursor.close()
    #         connection.close()

# 測試函數


if __name__ == '__main__':
    # print("hello")
    Scrape = ScraperFactory.get_scraper(NTUST_LANG_URL)
    data = Scrape.scrape()
    for announcement in data:
        print(announcement)
        SaveBulletin(announcement)

    # print_bulletin_data()

