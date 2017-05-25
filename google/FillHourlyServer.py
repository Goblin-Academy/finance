import sqlite3
import base

import base
import datetime
from yahoo_finance import Share

#quandl.ApiConfig.api_key = 'EnUrQ_P5xgH3S9n8gyLg'

class Data():

    def __init__(self,ticker):
        self.ticker
        self.data={}

def Close(connection):
    # never forget this, if you want the changes to be saved:
    connection.commit()
    
    connection.close()
    
def GenerateTable(recreate=False, db_name="stocks_hourly.db"):

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    # delete
    #if recreate:
    #    cursor.execute("""DROP TABLE stocks_hourly;""")
    
    if recreate:
        sql_command = """
    CREATE TABLE stocks_hourly ( 
    ticker VARCHAR(8), 
    price decimal(10,3),
    date DATE);"""
    
        cursor.execute(sql_command)
    
    return connection,cursor

def AddToTable(ticker, price, date, connection,cursor):
    p = [ticker,price,date]
    
    format_str = """INSERT INTO stocks_hourly (ticker, price, date)
            VALUES ({ticker}, '{price}','{date}');"""
    
    sql_command = """INSERT INTO stocks_hourly (ticker, price, date)  
    VALUES ('%s', %s,'%s');""" %(p[0],p[1],p[2])
    #print sql_command
    cursor.execute(sql_command)
    
if __name__ == "__main__":
        
    connection,cursor=GenerateTable(base.stock_list)
    AddToTable(stock_list, connection,cursor)
    Close(connection)
