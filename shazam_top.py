import csv
from datetime import datetime
import io
import os

import boto3
from botocore.config import Config
from bs4 import BeautifulSoup
from firecrawl import Firecrawl


firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
r = firecrawl.scrape('https://www.shazam.com/charts/top-50/india/bengaluru', formats=['rawHtml'])


soup = BeautifulSoup(r.raw_html, features='html.parser')
results = []


for div in list(soup.select("div[data-test-id=songItem]")):
    print(len(results)+1)
    title_a = div.select_one('a[data-test-id=charts_userevent_list_songTitle]')
    artist_a = div.select_one('a[data-test-id=charts_userevent_list_artistName]')
    am_a = div.select_one('a[data-test-id=charts_userevent_appleMusicLink]')
    if len(results)==0 and not artist_a:
        artist_a = soup.select_one('#S\\:5 a[data-test-id=charts_userevent_list_artistName]')
    if len(results)==0 and not am_a:
        am_a = soup.select_one('#S\\:6 a[data-test-id=charts_userevent_appleMusicLink]')
    
    results.append(dict(
        position = len(results) + 1,
        title = title_a.get("aria-label"),
        link = 'https://shazam.com' + title_a.get('href'),
        artist = artist_a.get("aria-label"),
        artist_link = 'https://shazam.com' + artist_a.get('href'),
        apple_music_link = am_a.get('href').split("?")[0],
    ))
    print(results[-1])
    print()

csv_buffer = io.StringIO()
w = csv.DictWriter(csv_buffer, fieldnames=results[0].keys())
w.writeheader()
w.writerows(results)

s3_client = boto3.client(
    "s3",
    endpoint_url = os.getenv("S3_ENDPOINT"),
    aws_access_key_id = os.getenv("S3_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("S3_SECRET_KEY"),
    config = Config(
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    )
)

filename = "shazam-top/" + datetime.now().strftime("%Y-%m-%d") + ".csv"
s3_client.put_object(
    Bucket = os.getenv("S3_BUCKET"),
    Key = filename,
    Body = csv_buffer.getvalue(),
)
