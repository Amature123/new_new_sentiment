# Sentiment Analysis Dashboard
## Project Overview
This project is a streaming pipeline that fetch data from Vietnamese network of communities, Voz. Performing sentiment analysis on each newest's message for every threads by using Scrapy for web scraping and Underthesea for advanced NLP. The result of sentiment for every messages are written to PostgresSQL. Users can view a realtime dashboard of sentiment score including percentage of sentiment on localhost buiding by Reactjs. The project was builded using docker.

# Architect
All applications are containerized into **Docker** containers.

1. **Data ingestion :** A python script called *demospider.py* is the main script to scrap all the messages from website. A little explain for the script 
