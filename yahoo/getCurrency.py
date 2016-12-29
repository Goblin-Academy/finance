from yahoo_finance import Currency
import send_sms

def Run():

    currencies = [['EURCHF',1.05,1.20],
                ['EURUSD',1.05,1.25],
                ['CHFUSD',0.98,1.08],
                ]

    for curr in currencies:
        print curr
        eur_pln = Currency(curr[0])
        #print eur_pln.get_bid()
        #print eur_pln.get_ask()
        conv_rate = float(eur_pln.get_rate())
        print conv_rate
        line =''
        if conv_rate<curr[1]:
            line ='Should consider switching currency: %0.2f for %s' %(conv_rate,curr[0])
        if conv_rate>curr[2]:
            line ='Should consider switching currency: %0.2f for %s' %(conv_rate,curr[0])
        #if len(line)>0:
        #    send_sms.sendMessage(line)
        
        #print eur_pln.get_trade_datetime()
        #'2014-03-05 11:23:00 UTC+0000'
        #eur_pln.refresh()
        #print eur_pln.get_rate()
        #print eur_pln.get_trade_datetime()
        #'2014-03-05 11:27:00 UTC+0000'


if __name__ == "__main__":
    Run()    
