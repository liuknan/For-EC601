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
    new_tweets = api.user_timeline(screen_name=screen_name, count=30)
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    while len(new_tweets) > 0:

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=30, max_id=oldest,tweet_mode='extended')

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        if (len(alltweets) > 30):
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
    num = 1
    for n in list:
        nam = str(num)
        nam=nam.zfill(4)
        file.write(n+'\n')
        n=str(n)
        ##name='./'+str(random.randrange(0,1000))+'.jpg'
        name=n.replace("http://","")
        name=name.replace("/","_")
        img_list.insert(-1,name)
        ##dir=os.path.abspath('.')+'/images'
        ##if not os.path.exists(dir):
            ##os.mkdir(dir)
        ##else:

       ## file_path=os.path.join(dir,n)
        urllib.request.urlretrieve(n,'img'+nam+'.jpg')
        imgnum=str(num)
        imgnum_list.insert(-1,'img'+imgnum.zfill(4)+'.jpg')
        num = num + 1
    file.close()

def video_output():
    # input_file = 'video.mp4'
    # out_file = 'video_out.mp4'
    # img_data= list
    # video.ins_img(input_file, img_data,out_file)
    ctrcmd='ffmpeg -i img%004d.jpg -pix_fmt yuv420p -r 25 -y test.mp4'
    sp.call(ctrcmd,shell=True)

def image_detection():
    # Create a Vision client.
    vision_client = google.cloud.vision.ImageAnnotatorClient()

    # TODO (Developer): Replace this with the name of the local image
    # file to analyze.
    i=0
    for name in imgnum_list:

        image_file_name = imgnum_list[i]
        with io.open(image_file_name, 'rb') as image_file:
            content = image_file.read()

    # Use Vision to label the image based on content.
        image = google.cloud.vision.types.Image(content=content)
        response = vision_client.label_detection(image=image)
        im = Image.open(name)
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype('/Users/liuknan/Downloads/Interface/AddOns/Skada/media/fonts/ABF.ttf',32)
        x,y=(0,0)
        print('Labels:')
        for label in response.label_annotations:
            draw.text((x,y),label.description,fill='red',font=font)
            y=y+40
            im.save(imgnum_list[i])
            print(label.description)
        i=i+1


if __name__ == '__main__':
    get_images('@FoAMortgage')
    get_image_url('tweet.json')
    download_images(same)
    video_output()
    image_detection()
##for status in tweepy.Cursor(api.home_timeline).items(2):
##    print (status.txt)

##alltweets = []

