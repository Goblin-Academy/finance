import sqlite3
import base
import datetime

def OpenTable(ticker, filter_date='2015-03-01', db_name="stocks.db"):
    
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    #cursor.execute("SELECT * FROM stocks") 
    #print("fetchall:")
    #result = cursor.fetchall() 
    #for r in result:
    #    print(r)
    #print len(res)
    #res = cursor.fetchall()
    cursor.execute("SELECT * FROM stocks WHERE ticker='%s' AND date>'%s'" %(ticker,filter_date)) 
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return result

def YahooFormat(result):
    #(u'GOOGL', 964.07, 957, 964.07, 0, 0, 0, 0, 0, 0, 1305246, u'2017-05-22')
    # ticker, price, open, prev_close, high, low, moving_avg_200day, moving_avg_50day
    # price_earnings_ratio, ebitda, volume, date
    yahoo = []
    for a in range(0,len(result)):
        # reverse the order...
        r = result[len(result)-a-1]
        d = {'Symbol':r[0],
             'Close':r[3],
             'Date':r[11],
             'Open':r[2],
             'High':r[4],             
             'Low':r[5],
             'Volume':r[10],
             'Date':r[11],
                 }
        yahoo+=[d]
    return yahoo
        
if __name__ == "__main__":
        
    res = OpenTable('GOOGL')
    print YahooFormat(res)
