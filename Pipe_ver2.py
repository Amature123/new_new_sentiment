import psycopg2
import logging
from datetime import datetime
import pytz
from tensorflow.keras.models import load_model
import pickle
import tensorflow as tf
from pyvi import ViTokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import model_from_json
tz = pytz.timezone('Asia/Ho_Chi_Minh')
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_raw_input(raw_input, tokenizer):
    input_text_pre = list(tf.keras.preprocessing.text.text_to_word_sequence(raw_input))
    input_text_pre = " ".join(input_text_pre)
    input_text_pre_accent = ViTokenizer.tokenize(input_text_pre)
    tokenized_data_text = tokenizer.texts_to_sequences([input_text_pre_accent])
    vec_data = pad_sequences(tokenized_data_text, padding='post', maxlen=335)
    return vec_data

def inference_model(input_feature, model):
    output = model(input_feature).numpy()[0]
    result = output.argmax()
    label_dict = {'tiêu cực': 0, 'trung lập': 1, 'tích cực': 2}
    label = list(label_dict.keys())
    return label[int(result)]

def prediction(raw_input, tokenizer, model):
    input_model = preprocess_raw_input(raw_input, tokenizer)
    result= inference_model(input_model, model)
    return result
model_path = "./models/model.pkl"
tokenizer_data_path = "./models/tokenizer_data.pkl"
with open(model_path, "rb") as model_file:
    my_model = pickle.load(model_file)
model_structure, model_weights = my_model 
model = model_from_json(model_structure)
model.set_weights(model_weights)  

with open(tokenizer_data_path, "rb") as tokenizer_file:
    my_tokenizer = pickle.load(tokenizer_file)

class FetchMessagePipeline:

    def analyze_sentiment(self, text):
        """Analyze sentiment using underthesea"""
        try:
            # Get sentiment label from underthesea
            sentiment_label = prediction(text,my_tokenizer,model)
            
            # Convert sentiment labels to counts
            sentiment_counts = {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            
            # Increment the appropriate counter based on sentiment
            if sentiment_label == 'tích cực':
                sentiment_counts['positive'] = 1
            elif sentiment_label == 'tiêu cực':
                sentiment_counts['negative'] = 1
            else:
                sentiment_counts['trung lập'] = 1
                
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