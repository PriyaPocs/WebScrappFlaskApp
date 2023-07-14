from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            option_selected = request.form['content']
            print('option_selected ',option_selected)
            reviews = []
            title_list = []
            views_list = []
            times_list = []
            video_urls_list = []
            thumbnail_video_url_list = []
            # initialize a web driver instance to control a Chrome window
            # in headless mode
            options = Options()
            options.add_argument('--headless=new')

            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )

            # the URL of the target page
            url = 'https://www.youtube.com/@PW-Foundation/videos'
            # visit the target page in the controlled browser
            driver.get(url)
            content = driver.page_source.encode('utf-8').strip()
            # close the browser and free up the resources
            driver.quit()
            # print(content)
            youtube_html = bs(content, "html.parser")
            thumbnails = youtube_html.findAll('a', {'id':'thumbnail'} and {'class':'yt-simple-endpoint style-scope ytd-playlist-thumbnail'})
            print(thumbnails)
            for i in range(5):
                # print('https://www.youtube.com/'+thumbnails[i]['href'])
                thumbnail_video_url_list.append('https://www.youtube.com/'+thumbnails[i]['href'])
        
            times = youtube_html.find_all('span', {'class':'inline-metadata-item style-scope ytd-video-meta-block'})
            times
            for i in range(10):
                if i%2 == 0:
                    views_list.append(times[i].text)
                    # print(times[i].text)
                else:
                    times_list.append(times[i].text)
                    # print(times[i].text)
            # youtube_html = bs(content, "html.parser")
            titles = youtube_html.find_all('a', {'id':'video-title-link'})
            titles
            # print("len(titles) = ",len(title_list))
            for i in range(5):
                # print('https://www.youtube.com/'+titles[i]['href'])
                video_urls_list.append('https://www.youtube.com/'+titles[i]['href'])
                title_list.append(titles[i]['title'])
                # print(titles[i]['title']) 
            for i in range(5):
                # print("="*100)
                # print(title_list[i]," ",video_urls_list[i]," ",views_list[i]," ",times_list[i]," ",thumbnail_video_url_list[i])
                mydict = {"title_list":title_list[i],"video_urls_list":video_urls_list[i],"views_list":views_list[i],"times_list":times_list[i],"thumbnail_video_url_list":thumbnail_video_url_list[i]}
                reviews.append(mydict)
            df = pd.DataFrame(list(zip(video_urls_list, thumbnail_video_url_list, title_list,views_list,times_list)), columns=['Video_url', 'Thumbnail_video_url', 'Title','Views','Time of upload'])
            print(df)
            df.to_csv('pwskills_web_scrape_info.csv', index=False)   
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:5],selected_option=option_selected)
        except Exception as e:
            logging.info(e)
            return 'something is wrong' 
    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0",port=5001)
