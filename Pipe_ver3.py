import psycopg2
import logging
from datetime import datetime
import pytz
import torch
from transformers import RobertaForSequenceClassification, AutoTokenizer
tz = pytz.timezone('Asia/Ho_Chi_Minh')
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model_path = "./models/"
tokenizer_path = "./token/"

model = RobertaForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
def predictions(text):

    # Load model and tokenizer

    input_ids = torch.tensor([tokenizer.encode(text, max_length=256, truncation=True)])
    
    # Get prediction
    with torch.no_grad():
        out = model(input_ids)
        result = out.logits.softmax(dim=-1).tolist()[0]
        
        # Convert to -1, 0, 1 based on highest probability
        if max(result) == result[0]:
            return 'NEGATIVE'
        elif max(result) == result[1]:
            return 'POSITIVE'
        else:
            return 'NEUTRAL'
class FetchMessagePipeline:

    def analyze_sentiment(self, text):

        try:
            # Get sentiment label from underthesea
            sentiment_label = predictions(text)
            
            # Convert sentiment labels to counts
            sentiment_counts = {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            
            # Increment the appropriate counter based on sentiment
            if sentiment_label == 'POSITIVE':
                sentiment_counts['positive'] = 1
            elif sentiment_label == 'NEGATIVE':
                sentiment_counts['negative'] = 1
            else:
                sentiment_counts['neutral'] = 1
                
            return sentiment_counts
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {'positive': 0, 'negative': 0, 'neutral': 0}

    def process_item(self, item, spider):
        """Process each scraped item"""
        try:
            # Get the message content
            message_text = item['message_content']
            
            # Analyze sentiment
            sentiment_counts = self.analyze_sentiment(message_text)
            
            # Update the item with sentiment counts
            item.update({
                **sentiment_counts,
                'processed_at': datetime.now(tz).isoformat()
            })
            
            logger.info(f"Processed item {item['id']}")
            return item
            
        except Exception as e:
            logger.error(f"Error processing item: {str(e)}")
            return item

class SentimentAnalysisPipeline:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname="vozdb",
                user="postgres",
                password="postgres",
                host="db",
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            
    def process_item(self, item, spider):
        try:
            # Store in database with sentiment counts
            self.cur.execute("""
                INSERT INTO voz_messages (
                    id, thread_title, thread_date, latest_poster, 
                    latest_post_time, message_content, thread_url,
                    positive_count, negative_count, neutral_count,
                    analyzed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    positive_count = EXCLUDED.positive_count,
                    negative_count = EXCLUDED.negative_count,
                    neutral_count = EXCLUDED.neutral_count,
                    analyzed_at = EXCLUDED.analyzed_at
            """, (
                item['id'], item['thread_title'], item['thread_date'],
                item['latest_poster'], item['latest_post_time'],
                item['message_content'], item['thread_url'],
                item['positive'], item['negative'], item['neutral'],
                item['processed_at']
            ))
            
            self.conn.commit()
            logger.info(f"Successfully stored item {item['id']} in database")
            
        except Exception as e:
            logger.error(f"Error storing item {item['id']} in database: {str(e)}")
            self.conn.rollback()
            
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()