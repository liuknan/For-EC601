#!/usr/bin/env python
# encoding: utf-8
import tweepy #https://github.com/tweepy/tweepy
import re
import json
import urllib.request
import os
import io
import subprocess as sp
import google.cloud.vision
import pandas as pd
from PIL import Image,ImageDraw,ImageFont
from google.cloud import videointelligence
same=[]
img_list=[]
imgnum_list=[]
alltweets_json=[]
#Twitter API credentials

API_key = "enter your key"
API_secret_key = "enter your key"
access_token = "enter your key"
access_token_secret = "enter your key"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='enter your json file path'

def get_images(screen_name):
    ##authorization
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
        print("...%s tweets downloaded so far" % (len(alltweets)))

    # write tweet objects to JSON
    file = open('tweet.json', 'w')
    print("Writing tweet objects to JSON please wait...")
    for status in alltweets:
        # alltweets_json.append(status._json)
        # json.dump(status._json, file, sort_keys=True, indent=4)
        #json.dump(alltweets_json,file,sort_keys=True,indent=4)
        with open('tweet.json','a+') as file:
            # a = status._json
            json.dump(status._json,file)
            file.write('\r')

    # close the file
    print("Done")
    #file.close()

def read_json():
    with open('tweet.json', 'r') as f:
        result = [json.loads(line, strict=False) for line in f]
        pp = pd.DataFrame(result)
    print(result)
    cc = list(filter(lambda x: isinstance(x, list), pp.loc[:, 'entities'].apply(pd.Series)['media'].tolist()))
    a = [i[0]['media_url'] for i in cc if i[0]['type'] == 'photo']
    print('total:', len(cc))
    print('type is photo', len(a))
    if not os.path.exists('photo'):
        os.mkdir('photo')
    num = 1
    for n in a:
        nam = str(num)
        nam = nam.zfill(4)
        n = str(n)
        name = n.replace("http://", "")
        name = name.replace("/", "_")
        img_list.insert(-1, name)
        ##rename the pictures so that the ffmpeg could convert them to a video.
        urllib.request.urlretrieve(n, 'photo/img' + nam + '.jpg')
        imgnum = str(num)
        ##number the file
        imgnum_list.insert(-1, 'photo/img' + imgnum.zfill(4) + '.jpg')
        num = num + 1

def video_output():
    ##use command line to start the ffmpeg.
    ctrcmd='ffmpeg -r 1/2 -i /Users/liuknan/PycharmProjects/APIAssignment/photo/img%004d.jpg  -y newvideo.mp4'
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
        font = ImageFont.truetype('/Library/Fonts/Trattatello.ttf',32)
        x,y=(0,0)
        print('Labels:')
        for label in response.label_annotations:
            draw.text((x,y),label.description,fill='red',font=font)
            y=y+40
            im.save(imgnum_list[i])
            print(label.description)
        i=i+1

def video_detction(path): ##https://cloud.google.com/video-intelligence/docs/libraries
    """Detect labels given a file path."""
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.enums.Feature.LABEL_DETECTION]

    with io.open(path, 'rb') as movie:
        input_content = movie.read()

    operation = video_client.annotate_video(
        features=features, input_content=input_content)
    print('\nProcessing video for label annotations:')

    result = operation.result(timeout=90)
    print('\nFinished processing.')

    # Process video/segment level label annotations
    segment_labels = result.annotation_results[0].segment_label_annotations
    for i, segment_label in enumerate(segment_labels):
        print('Video label description: {}'.format(
            segment_label.entity.description))
        for category_entity in segment_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))

        for i, segment in enumerate(segment_label.segments):
            start_time = (segment.segment.start_time_offset.seconds +
                          segment.segment.start_time_offset.nanos / 1e9)
            end_time = (segment.segment.end_time_offset.seconds +
                        segment.segment.end_time_offset.nanos / 1e9)
            positions = '{}s to {}s'.format(start_time, end_time)
            confidence = segment.confidence
            print('\tSegment {}: {}'.format(i, positions))
            print('\tConfidence: {}'.format(confidence))
        print('\n')

    # Process shot level label annotations
    shot_labels = result.annotation_results[0].shot_label_annotations
    for i, shot_label in enumerate(shot_labels):
        print('Shot label description: {}'.format(
            shot_label.entity.description))
        for category_entity in shot_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))

        for i, shot in enumerate(shot_label.segments):
            start_time = (shot.segment.start_time_offset.seconds +
                          shot.segment.start_time_offset.nanos / 1e9)
            end_time = (shot.segment.end_time_offset.seconds +
                        shot.segment.end_time_offset.nanos / 1e9)
            positions = '{}s to {}s'.format(start_time, end_time)
            confidence = shot.confidence
            print('\tSegment {}: {}'.format(i, positions))
            print('\tConfidence: {}'.format(confidence))
        print('\n')

    # Process frame level label annotations
    frame_labels = result.annotation_results[0].frame_label_annotations
    for i, frame_label in enumerate(frame_labels):
        print('Frame label description: {}'.format(
            frame_label.entity.description))
        for category_entity in frame_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))

        # Each frame_label_annotation has many frames,
        # here we print information only about the first frame.
        frame = frame_label.frames[0]
        time_offset = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
        print('\tFirst frame time offset: {}s'.format(time_offset))
        print('\tFirst frame confidence: {}'.format(frame.confidence))
        print('\n')
if __name__ == '__main__':
    screen_name=str(input("please input the screen name:"))
    get_images(screen_name)
    read_json()
    image_detection()
    video_output()
    video_detction('/Users/liuknan/PycharmProjects/APIAssignment/test.mp4')



