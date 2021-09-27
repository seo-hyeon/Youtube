import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import datetime
import time

url = "mongodb+srv://User:User@cluster0.b762i.mongodb.net/test"
connection = MongoClient(url)
db = connection.nuance
col = db.get_collection("newsdata")


def scraper(oid, last):
    # date = "20210924"
    # raw = requests.get("https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=119&date=", headers={'User-Agent':'Mozilla/5.0'})
    raw = requests.get("https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid="+oid+"&date=", headers={'User-Agent':'Mozilla/5.0'})
    html = BeautifulSoup(raw.text, "html.parser")

    articles = []
    articles.append(html.select_one(".type06_headline").select("li"))
    articles.append(html.select_one(".type06").select("li"))

    news = []
    i = 0

    for article in articles:
        for art in article:
            try:
                r = requests.get(art.select("a")[0]['href'], headers={'User-Agent':'Mozilla/5.0'})
                h = BeautifulSoup(r.text, "html.parser")

                if (h.select_one('#articleBodyContents') != None):
                    h.select_one('#articleBodyContents').script.decompose()
                    contents = h.select_one('#articleBodyContents').text.strip()
                elif (h.select_one('#articeBody') != None):
                    contents = h.select_one('#articeBody').text.strip()
                elif (h.select_one('#newsEndContents') != None):
                    contents = str(h.select_one('#newsEndContents'))[str(h.select_one('#newsEndContents')).find("</em></img></span>") + 18: str(h.select_one('#newsEndContents')).find("<p class=")]
                # print(contents)

                contents = contents.replace("<br/>", " ")

                if (contents in last):
                    if len(news) > 0:
                        col.insert_many(news)
                    return -1
                
                data = {}
                data['channel'] = "news"
                data['data'] = contents
                data['createdAt'] = datetime.datetime.utcnow()
                data['updatedAt'] = datetime.datetime.utcnow()
                data['url'] = art.select("a")[0]['href']
                news.append(data)

                if i < 5:
                    if len(last) < 5:
                        last.append(contents)
                    else:
                        last.pop()
                        last.insert(0, contents)
                    i += 1
            except Exception as e:
                print(e)

    col.insert_many(news)
    return 0

if __name__ == "__main__":
    last1 = []
    last2 = []
    last3 = []
    last4 = []
    last5 = []

    while(True):
        scraper("629", last1)
        scraper("119", last2)
        scraper("006", last3)
        scraper("031", last4)
        scraper("047", last5)

        
        time.sleep(30)