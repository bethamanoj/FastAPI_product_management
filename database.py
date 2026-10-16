import mysql.connector as connector 
from config import db_config
def get_connection():
    return connector.connect(**db_config)