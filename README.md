# Sentiment Analysis Dashboard
## Project Overview
This project is a streaming pipeline that fetch data from Vietnamese network of communities, Voz. Performing sentiment analysis on each newest's message for every threads by using Scrapy for web scraping and Underthesea for advanced NLP. The result of sentiment for every messages are written to PostgresSQL. Users can view a realtime dashboard of sentiment score including percentage of sentiment on localhost buiding by Reactjs. The project was builded using docker.

## Architect
All applications are containerized into **Docker** containers.

1. **Data ingestion :** A python script called *demospider.py* is the main script to scrap all the messages from website. Every message it scrap will head to the pipeline called *pipeline.py*. The pipeline start analysing each sentence using Underthesea and return sentiment label.
2. **Database procession :** A simple PostgreSQL file called *init* to generate a table, each results of messages that has been analysed will be load into the database one by one
3. **Backend API :** A containerized Python application called *main.py* sets up **FastAPI** endpoints for the frontend to obtain sentiment and emotion data for comments.
   Two endpoints are provided:
    - A **WebSocket** on 1 second intervals, it calculates the sum of all sentiments and counts of all comments written to the PostgreSQL table continuously. It returns this data in JSON form.
    - A HTTP GET endpoint that takes a variety of fields in the url. The endpoint function returns a list of dictionaries containing all comments filtered by those fields. This is converted into JSON by FastAPI.
4. **Data Visualization :** A **React** frontend provides a variety of components for visualizing real-time sentiment voz comments. Mui is used to render several different times of charts, including line chart, bar chart, and pie chart. Data normalization has to be performed for the area chart to provide a % breakdown of each emotion. Every data were taken from backend API, you can also check it using `localhost:8080`.

## Installation and Setup
### System Requirements
- [Docker Engine](https://www.docker.com/)
### How to use 
- Simply navigate to the folder and go to the terminal, run `docker-compose build`, wait for like 15 minutes (Sorry for our choosen model kinda heavy load), and then `docker compose up`, go to  `localhost:5173` and see the dashboard

## Current Limitations
1. **Lack of Testing**
   - The project currently lacks a comprehensive testing strategy
   - No unit tests or integration tests have been implemented
   - Recommendation: Develop a robust testing framework to ensure reliability and catch potential bugs early in the development process

## Proposed Enhancements
1. **Kafka Integration**
   - Implement Apache Kafka as a message queue and streaming platform
   - Benefits:
     - Improved data streaming capabilities
     - Better scalability for handling large volumes of comments
     - Enhanced real-time data processing
     - Decoupling of data ingestion and processing components

2. **Spark for Advanced Data Processing**
   - Integrate Apache Spark for more sophisticated data analysis
   - Potential improvements:
     - Distributed computing for sentiment analysis
     - Advanced machine learning models for sentiment classification
     - Ability to process larger datasets more efficiently
     - More complex data transformations and aggregations
## Potential Future Expansions
- Machine learning model improvements
- More advanced visualization techniques
- Multi-language sentiment analysis support
## Library
1. [nama1arpit Reddit Streaming Data Pipeline Project](https://github.com/nama1arpit/reddit-streaming-pipeline)
2. [jalvin99 Reddit Sentiment Analyzer](https://github.com/jalvin99/RedditSentimentAnalyzer)
3. [Underthesea - Vietnamese NLP Toolkit](https://github.com/undertheseanlp/underthesea)
