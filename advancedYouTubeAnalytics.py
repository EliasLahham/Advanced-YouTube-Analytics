import cv2
import csv
import os
from sys import path
from youtube_api import YouTubeDataAPI

# Imports for URL to image
from urllib.request import urlopen
import numpy as np

key = <YOUR API KEY>
yt = YouTubeDataAPI(key)
filename = ''


def progStart():
    fileName = str(path[-4])
    userInput = int(input("Type 0 for comparing channels\n"
                      "Type 1 for a YouTube search query\n"
                      "Type anything else to exit\n"
                      "> "))

    # Ask user for number of videos to analyze and file name
    videosToAnalyze = int(input("How many videos do you want to analyze: "))
    fileNameAddOn = input("Name of CSV file: ")

    # Handles user input with or without .csv attached
    if not fileNameAddOn.endswith('.csv'):
        fileNameAddOn = fileNameAddOn + ".csv"

    fileName = fileName + "/" + fileNameAddOn
    filename = fileName
    createCSV(fileName)

    # Comparing channels
    if userInput == 0:
        # Holds channel ids
        channelList = []
        while 1:
            channelName = input("Type a channel's id [Type DONE when finished]: ")
            if channelName.lower() == "done":
                break
            channelList.append(channelName)
        createCSV(fileName)
        channelAnalyzer(channelList, videosToAnalyze, fileName)
    elif userInput == 1:
        # YouTube search query
        searchQuery = input("Enter a YouTube Search Query: ")
        searchQueryAnalyzer(searchQuery, videosToAnalyze, fileName)
    else:
        print(f'Input received -> "{userInput}" --- Exitting program...')
        exit()


def channelAnalyzer(channels, numOfVideos, filename):
    analyzerCounter = 0
    for id in channels:
        count = 0
        # Queries a YouTube search based on channel id
        channelSearch = yt.search(channel_id=id, max_results=numOfVideos, order_by="date")
        # Stores metadata for each video in a list and calls CSV writer
        for video in channelSearch:
            videoMetadata = yt.get_video_metadata(video_id=channelSearch[count]["video_id"])
            metadataAnalyzer(videoMetadata, filename)
            analyzerCounter += 1
            count += 1
            print(f"{analyzerCounter}/{numOfVideos * len(channels)} video(s) analyzed")


def searchQueryAnalyzer(query, numOfVideos, filename):
    count = 0
    # Queries a YouTube search based on a user's query
    searchQuery = yt.search(q=query, max_results=numOfVideos, order_by="relevance")
    # Stores metadata for each video in a list and calls CSV writer
    for video in searchQuery:
        videoMetadata = yt.get_video_metadata(video_id=searchQuery[count]["video_id"])
        metadataAnalyzer(videoMetadata, filename)
        count += 1
        print(f"{count}/{numOfVideos} video(s) analyzed")


def metadataAnalyzer(metadata, filename):
    videoLink = f"https://www.youtube.com/watch?v={metadata['video_id']}"
    channelName = metadata["channel_title"]
    thumbnail = metadata["video_thumbnail"]
    face = faceRecog(thumbnail)
    title = metadata["video_title"]
    titleLength, percentCap, questionCheck = titleChecker(title)
    category = categoryConverter(str(metadata["video_category"]))
    views = metadata["video_view_count"]
    likes = metadata["video_like_count"]
    dislikes = metadata["video_dislike_count"]
    comments = metadata["video_comment_count"]
    if not metadata["video_tags"]:
        tags = "False"
    else:
        tags = "True"
    metadataList = [channelName, category, videoLink, title, views, likes, dislikes, comments, face, titleLength, percentCap, questionCheck, tags]
    csvWriter(metadataList, filename)


def faceRecog(thumbnailUrl):
    # Face Detection Code by shantnu, modified by Me
    # https://github.com/shantnu/FaceDetect

    # Converts url to image
    img = url_to_image(thumbnailUrl)

    # Get user supplied values
    cascPath = "haarcascade_frontalface_default.xml"

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    # Read the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) > 0:
        return "True"
    else:
        return "False"


# Converts a URL hosted image to a usable image in Python via a numpy array
def url_to_image(url):
    resp = urlopen(url)
    imageArray = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(imageArray, cv2.IMREAD_COLOR)
    return image


# Gathers various data on the video's title
def titleChecker(videoTitle):
    capitalCount = 0
    spaceCount = 0
    percentCapital = ''

    # Length of title
    videoTitleLength = len(videoTitle.split())

    # Checks if the title is a question or not
    if "?" in videoTitle:
        questionMark = "True"
    else:
        questionMark = "False"

    # Calculates the percentage of capital letters in the title
    for char in videoTitle:
        if char.isupper():
            capitalCount += 1
        elif char == " ":
            spaceCount += 1
    percent = (capitalCount / (len(videoTitle) - spaceCount)) * 100
    percentCapital = str(round(percent, 2)) + "%"
    return str(videoTitleLength), percentCapital, questionMark


def categoryConverter(videoCategory):
    # Predetermined values via YouTube
    videoCategories = {
        "1": "Film & Animation",
        "2": "Auto & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "18": "Short Movies",
        "19": "Travel & Events",
        "20": "Gaming",
        "21": "Videoblogging",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "Howto & Style",
        "27": "Education",
        "28": "Science & Technology",
        "29": "Nonprofits & Activism",
        "30": "Movies",
        "31": "Anime/Animation",
        "32": "Action/Adventure",
        "33": "Classics",
        "34": "Comedy",
        "35": "Documentary",
        "36": "Drama",
        "37": "Family",
        "38": "Foreign",
        "39": "Horror",
        "40": "Sci-Fi/Fantasy",
        "41": "Thriller",
        "42": "Shorts",
        "43": "Shows",
        "44": "Trailers"
    }
    if videoCategory in videoCategories.keys():
        return videoCategories.get(videoCategory)
    else:
        return "No Category"


# Creates/Overwrites CSV file with predetermined headers
def createCSV(file):
    with open(file, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow(["Channel Name", "Category", "Video Link", "Title", "View Count", "Likes", "Dislikes", "Comments", "Face?", "Title Length", "Title Capital Percentage", "Title Question", "Tags?"])


# Writes metadata to CSV via given list
def csvWriter(list, file):
        with open(file, 'a', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, lineterminator='\n')
            try:
                filewriter.writerow(list)
            except UnicodeEncodeError:
                list[3] = "Invalid Title"
                filewriter.writerow(list)


progStart()
while 1:
    userDecision = input("Analysis Complete\n"
                         "Type yes to run again\n"
                         "Type open to open project folder\n"
                         "Type no to exit program\n"
                         "> ")
    if userDecision.lower() == "yes":
        progStart()
    elif userDecision.lower() == "open":
        os.startfile(filename)
        exit()
    else:
        exit()
