from yahoo_finance import Share
#yahoo = Share('YHOO')
#yahoo = Share('SPXC')
yahoo = Share('^SPX')
#yahoo = Share('INDU')
#INDEXSP
#yahoo = Share('NDX')
print yahoo
print yahoo.get_open()
#'36.60'
print yahoo.get_price()
print yahoo.get_price_earnings_ratio()
print 'get_dividend_share: ',yahoo.get_dividend_share()
print 'get_dividend_yield: ',yahoo.get_dividend_yield()
print 'get_earnings_share: ',yahoo.get_earnings_share()
print 'get_price_earnings_ratio: ',yahoo.get_price_earnings_ratio()
print 'get_price_earnings_growth_ratio: ',yahoo.get_price_earnings_growth_ratio()
print 'get_year_high: ',yahoo.get_year_high()
print 'get_year_low: ',yahoo.get_year_low()
print 'get_days_high: ',yahoo.get_days_high()
print 'get_days_low: ',yahoo.get_days_low()
print 'get_ebitda: ',yahoo.get_ebitda()
print 'get_book_value: ',yahoo.get_book_value()
#'36.84'
#print yahoo.get_trade_datetime()
#'2014-02-05 20:50:00 UTC+0000'
#get_avg_daily_volume()
