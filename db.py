import pyodbc
import os
from dotenv import load_dotenv
from info import SERVER, DATABASE, USER, PASSWORD

load_dotenv()

# SERVER = os.getenv('SERVER')
# DATABASE = os.getenv('DATABASE')
# USERNAME = os.getenv('USER')
# PASSWORD = os.getenv('PASSWORD')

connectionString = f"""
    DRIVER={{ODBC Driver 18 for SQL Server}};
    SERVER={f'{SERVER},1433'};
    DATABASE={DATABASE};
    UID={USER};
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
        return {"status": None, "error": e}
