from googleapiclient.discovery import build
from pymongo import MongoClient
import sys
import datetime
import re
import config

url = config.MONGO_URL
connection = MongoClient(url)
db = connection.nuance
col = db.get_collection("snsdata")

def main(videoId):
    comments = []
    youtube = build('youtube','v3',developerKey=config.YOUTUBE_API_KEY)
    results = youtube.commentThreads().list(
        part="id, snippet, replies",
        videoId = videoId,
        maxResults=100,
        pageToken='',
    ).execute()
    
    while(1):
        for item in results['items']:
            com = item['snippet']['topLevelComment']['snippet']['textOriginal'].replace("\n", " ")
            com = com.replace("\r", " ")
            com = com.replace("\t", " ")
            com = re.sub(' +', ' ', com)
            data = {}
            data['channel'] = "youtube"
            data['data'] = com
            data['createdAt'] = datetime.datetime.utcnow()
            data['updatedAt'] = datetime.datetime.utcnow()
            data['url'] = "https://www.youtube.com/watch?v=" + item['snippet']['videoId']
            comments.append(data)
        nt = results['nextPageToken']

        results = youtube.commentThreads().list(
            part="id, snippet, replies",
            videoId = videoId,
            maxResults=50,
            pageToken=nt,
        ).execute()

        if 'nextPageToken' not in results:
            break;

    for item in results['items']:
        com = item['snippet']['topLevelComment']['snippet']['textOriginal'].replace("\n", " ")
        com = com.replace("\r", " ")
        com = com.replace("\t", " ")
        com = re.sub(' +', ' ', com)
        data = {}
        data['channel'] = "youtube"
        data['data'] = com
        data['createdAt'] = datetime.datetime.utcnow()
        data['updatedAt'] = datetime.datetime.utcnow()
        data['url'] = "https://www.youtube.com/watch?v=" + item['snippet']['videoId']
        comments.append(data)

    col.insert_many(comments)
    
    return {"success": True}

if __name__ == "__main__":
    main(sys.argv[1])