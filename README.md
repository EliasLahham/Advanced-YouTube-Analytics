# Advanced YouTube Analytics

This script will utilize YouTube's Data API v3 to gather metadata from search queries and videos from channels depending on user input. In addition to the metadata provided by the API, I've added a few more fields to fill out like checking for faces in thumbnails, title length, is the title a question, and title capital letter percentage. All metadata will be exported to a CSV file which can be easily viewable in Excel.

The goal of this mini project was to see if there are correlations between search queries and certain video metadata. 

The metadata written to CSV:

1. Channel Name
2. Video Category
3. Video URL
4. Title
5. View Count
6. Likes
7. Dislikes
8. Comment Count
9. Face in thumbnail?
10. Title Length
11. Capital Letter %
12. Question in Title
13. Tags in Video?

To run:

1. Create a new project
2. Place haarcascade_frontalface_default.xml in your project folder
3. Replace the API key placeholder with your Google API key

Need help getting a Google API key? [Click here](https://developers.google.com/youtube/v3/getting-started)

*Depending on your API privileges, you are most likely limited to 500~ videos per day

Face Detection Code by [shantnu](https://github.com/shantnu/FaceDetect), modified by Me

![Example spreadsheet](https://i.imgur.com/WDv2Ta3.png)
