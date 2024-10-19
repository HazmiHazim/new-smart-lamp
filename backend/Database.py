import os
import urllib.parse
import pymongo
import dotenv

class Database:
    
    """
    * This Class Resposible to create collection in MongoDB Database
    * Define the collection name in this class
    """
    
    collection_names = [
        "users",
        "lamps",
        "deleted_datas"
    ]
    
    def __init__(self, logging) -> None:
        self.logging = logging
    
    def database_connection(self, collection_name):
        try:
            # Load environment variables from the .env file (if present)
            dotenv.load_dotenv()
            DB_CONNECTION = os.getenv("DB_CONNECTION")
            DB_HOST = os.getenv("DB_HOST")
            DB_PORT = os.getenv("DB_PORT")
            DB_NAME = os.getenv("DB_NAME")
            DB_USERNAME = os.getenv("DB_USERNAME")
            DB_PASSWORD = os.getenv("DB_PASSWORD")
            DB_TIMEOUT = os.getenv("DB_TIMEOUT")
            DB_AUTH_SOURCE = os.getenv("DB_AUTH_SOURCE")
            DB_APP_NAME = os.getenv("DB_APP_NAME")
            
            # Generate uri from the env file
            MONGODB_URI = f"{DB_CONNECTION}://{DB_USERNAME}:{urllib.parse.quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?directConnection=true&serverSelectionTimeoutMS={DB_TIMEOUT}&authSource={DB_AUTH_SOURCE}&appName={DB_APP_NAME}"
            connection = pymongo.MongoClient(MONGODB_URI)
            database = connection[DB_NAME]
            if collection_name not in self.collection_names:
                self.logging.log_debug(f"{collection_name} does not exists.")
                
            collection = database[collection_name]
            return collection
        
        except Exception as ex:
            self.logging.log_debug(f"Class: Database | Method: database_connection | ErorMsg: {ex}")