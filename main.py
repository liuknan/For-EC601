#!/usr/bin/env python
# encoding: utf-8
import tweepy #https://github.com/tweepy/tweepy
import re
import json
import urllib.request
import os
import subprocess as sp
##import random
same=[]
img_list=[]
#Twitter API credentials
API_key = ""
API_secret_key = ""
access_token = ""
access_token_secret = ""


def get_images(screen_name):
    auth = tweepy.OAuthHandler(API_key, API_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api=tweepy.API(auth)
    alltweets=[]
    new_tweets = api.user_timeline(screen_name=screen_name, count=10)
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    while len(new_tweets) > 0:

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=10, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        if (len(alltweets) > 15):
            break
        print
        "...%s tweets downloaded so far" % (len(alltweets))

    # write tweet objects to JSON
    file = open('tweet.json', 'w')
    print
    "Writing tweet objects to JSON please wait..."
    for status in alltweets:
        json.dump(status._json, file, sort_keys=True, indent=4)

    # close the file
    print
    "Done"
    file.close()

def get_image_url(file):
        text=open(file,'r')
        for line in text.readlines():
            urltext = re.compile(r'media_url": "(.*)",')
            url=urltext.findall(line)
            if len(url):
                if url[0] in same:
                    continue
                else:
                    same.insert(-1,url[0])

            else:
                continue
            ##line = line.replace("'", "")
            ##images = json.loads(line)
            ##for m in images['entities'] ['media'].values():
                ##print("%s" % (m['display_url']))
def download_images(list):
    file = open('url.txt','w')
    num = 0
    for n in list:
        num = num + 1
        nam = str(num)
        file.write(n+'\n')
        n=str(n)
        ##name='./'+str(random.randrange(0,1000))+'.jpg'
        name=n.replace("http://","")
        name=name.replace("/","_")
        img_list.insert(-1,name)
        dir=os.path.abspath('.')+'/images'
        if not os.path.exists(dir):
            os.mkdir(dir)
        else:

       ## file_path=os.path.join(dir,n)
            urllib.request.urlretrieve(n,nam+'.jpg')
    file.close()

def video_output():
    # input_file = 'video.mp4'
    # out_file = 'video_out.mp4'
    # img_data= list
    # video.ins_img(input_file, img_data,out_file)
    ctrcmd='ffmpeg -f image2 -loop 1 -y -i %d.jpg -vcodec libx264 -r 10 test.mp4'
    sp.call(ctrcmd,shell=True)
if __name__ == '__main__':
    get_images('@FoAMortgage')
    get_image_url('tweet.json')
    download_images(same)
    video_output()
    print(img_list)
##for status in tweepy.Cursor(api.home_timeline).items(2):
##    print (status.txt)

##alltweets = []

