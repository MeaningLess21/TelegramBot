import config
from pymongo import MongoClient
# Подключение к базе данных MongoDB
try:
    mongo_client = MongoClient(config.db_connect)
    db = mongo_client['task_manager']
    tasks_collection = db['tasks']
    performers_collection = db['performers']
except:
    print("Не удалось подключиться к БД ")