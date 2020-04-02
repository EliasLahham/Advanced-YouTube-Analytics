import cv2
import csv
import os
from sys import path
from youtube_api import YouTubeDataAPI

# Imports for URL to image
from urllib.request import urlopen
import numpy as np

key = [YOUR KEY]
yt = YouTubeDataAPI(key)


def main():
    global path
    path = str(path[-4])
    userInput = int(input("Type 0 for comparing channels\n"
                      "Type 1 for a YouTube search query\n"
                      "Type anything else to exit\n"
                      "> "))

    if userInput != 0 and userInput != 1:
        print(f'Input received -> "{userInput}" --- Exitting program...')
        exit()

    # Ask user for number of videos to analyze and file name
    videosToAnalyze = int(input("How many videos do you want to analyze: "))
    nameOfCSV = input("Name of CSV file: ")

    if not nameOfCSV.endswith('.csv'):
        nameOfCSV = nameOfCSV + ".csv"

    path = path + "/" + nameOfCSV
    createCSV(path)

    # Comparing channels
    if userInput == 0:
        # Holds channel ids
        channelList = []
        while 1:
            channelName = input("Type a channel's id [Type DONE when finished]: ")
            if channelName.lower() == "done":
                break
            channelList.append(channelName)
        channelAnalyzer(channelList, videosToAnalyze)
    elif userInput == 1:
        # YouTube search query
        searchQuery = input("Enter a YouTube Search Query: ")
        searchQueryAnalyzer(searchQuery, videosToAnalyze)


def channelAnalyzer(channels, numberOfVideos):
    count = 0
    for id in channels:
        # Queries a YouTube search based on channel id
        channelSearch = yt.search(channel_id=id, max_results=numberOfVideos, order_by="date")
        # Stores metadata for each video in a list and beings analyzing
        for video in channelSearch:
            videoMetadata = yt.get_video_metadata(video_id=channelSearch[count]["video_id"])
            metadataAnalyzer(videoMetadata)
            count += 1
            print(f"{count}/{numberOfVideos * len(channels)} video(s) analyzed")


def searchQueryAnalyzer(query, numberOfVideos):
    count = 0
    # Queries a YouTube search based on a user's query
    searchQuery = yt.search(q=query, max_results=numberOfVideos, order_by="relevance")
    # Stores metadata for each video in a list and calls CSV writer
    for video in searchQuery:
        videoMetadata = yt.get_video_metadata(video_id=searchQuery[count]["video_id"])
        metadataAnalyzer(videoMetadata)
        count += 1
        print(f"{count}/{numberOfVideos} video(s) analyzed")


def metadataAnalyzer(metadata):
    videoLink = f'https://www.youtube.com/watch?v={metadata["video_id"]}'
    channelName = metadata["channel_title"]
    thumbnail = metadata["video_thumbnail"]
    isFaceInThumbnail = faceRecogonitionInThumbnail(thumbnail)
    title = metadata["video_title"]
    titleLength, capitalLetterPercentageInTitle, isQuestionMarkInTitle = getMetadataFromTitle(title)
    category = youtubeCategoryConverter(str(metadata["video_category"]))
    views = metadata["video_view_count"]
    likes = metadata["video_like_count"]
    dislikes = metadata["video_dislike_count"]
    comments = metadata["video_comment_count"]
    if not metadata["video_tags"]:
        doTagsExists = str(False)
    else:
        doTagsExists = str(True)
    metadataList = [channelName, category, videoLink, title, views, likes, dislikes, comments, isFaceInThumbnail, titleLength, capitalLetterPercentageInTitle, isQuestionMarkInTitle, doTagsExists]
    csvWriter(metadataList)


def faceRecogonitionInThumbnail(thumbnailUrl):
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
        return str(True)
    else:
        return str(False)


def url_to_image(url):
    resp = urlopen(url)
    imageArray = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(imageArray, cv2.IMREAD_COLOR)
    return image


def getMetadataFromTitle(videoTitle):
    capitalLetterCount = 0
    spaceCharCount = 0

    videoTitleLength = len(videoTitle.split())

    if "?" in videoTitle:
        isQuestionMarkInTitle = str(True)
    else:
        isQuestionMarkInTitle = str(False)

    for char in videoTitle:
        if char.isupper():
            capitalLetterCount += 1
        elif char == " ":
            spaceCharCount += 1

    capitalLetterPercentage = str(round((capitalLetterCount / (len(videoTitle) - spaceCharCount)) * 100, 2)) + "%"
    return videoTitleLength, capitalLetterPercentage, isQuestionMarkInTitle


def youtubeCategoryConverter(videoCategory):
    # Predetermined values for video categories
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
    print("Blank CSV file with headers created...")


# Writes metadata to CSV
def csvWriter(videoMetadata):
        with open(path, 'a', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, lineterminator='\n')
            try:
                filewriter.writerow(videoMetadata)
            except UnicodeEncodeError:
                # Occurs when various Emojis are in title
                videoMetadata[3] = "Invalid Title"
                filewriter.writerow(videoMetadata)


main()
while 1:
    userDecision = input("Analysis Complete\n"
                         "Type open to open project folder\n"
                         "Type yes to run again\n"
                         "Type no to exit program\n"
                         "> ")
    if userDecision.lower() == "yes":
        main()
    elif userDecision.lower() == "open":
        os.startfile(path)
        exit()
    else:
        exit()
