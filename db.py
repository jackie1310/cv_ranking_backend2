import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# SERVER = os.getenv('SERVER')
SERVER = '103.97.125.205'
# DATABASE = os.getenv('DATABASE')
DATABASE = 'db_cv'
# USERNAME = os.getenv('USER')
USERNAME = 'intern'
# PASSWORD = os.getenv('PASSWORD')
PASSWORD = 'interncybersoft'

connectionString = f"""
    DRIVER={{ODBC Driver 18 for SQL Server}};
    SERVER={f'{SERVER},1433'};
    DATABASE={DATABASE};
    UID={USERNAME};
    PWD={PASSWORD};
    Encrypt=yes;
    TrustServerCertificate=yes;
"""

def connectToDB():
    try:
        connection = pyodbc.connect(connectionString)
        print("Connection established")
        cursor = connection.cursor()
        return cursor
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        return None
