import HTML
import base
import os
#import getPriceAll as price
out_path = base.out_path
out_file_type = base.out_file_type

stock_list = [
        # Check stocks
        ['GOOGL',640.0,805.0,'NASDAQ'], # google
        ['AMZN',450.0,700.0,'NASDAQ'], # amazon
        ['AAPL',86.0,110.0,'NASDAQ'], # apple
        ]
stock_list = base.stock_list    

def genPlotPage(ticker='GOOGL', date='2016-09-14'):
    PLOTFILE = out_path+'/plot_html/'+ticker+'_'+date+'.html'
    # Check if the file exists
    if os.file.exists(PLOTFILE):
        return
    
    line='<html>\n'
    line+='   <head>\n'
    line+='       <title>Plots for Ticker: %s</title>\n' %(ticker)
    line+='   </head>\n'
    line+='   <body>\n'

    plot_data = [[out_path+'/ma/%s_%s.png' %(ticker,date)],
                 [out_path+'/ma/%s_%sbol.png' %(ticker,date)],
                 [out_path+'/macd/%s_%s.png' %(ticker,date)],
                 [out_path+'/obv/%s_%s.png' %(ticker,date)],
                 [out_path+'/obv/%s_%svolt.png' %(ticker,date)],
                 [out_path+'/obv/%s_%schaikin.png' %(ticker,date)],
                 [out_path+'/corr/%s_%s.png' %(ticker,date)],
                 [out_path+'/rsi/%s_%s.png' %(ticker,date)],
                 [out_path+'/stoch/%s_%s.png' %(ticker,date)],
                 ]
    for i in plot_data: 
        i[0]='<img src="%s" alt="N/A" width="400" />' %i[0]
        #'<span class="stock-quote" data-symbol="%s"></span>' %ticker,
    line+=HTML.table(plot_data)
    line+='   </body>\n'    
    line+='</html>'

    fticker = open(PLOTFILE, 'w')
    fticker.write(line)
    fticker.close()
    
def main(date='2016-12-29',map_for_rsi=[]):
    # open an HTML file to show output in a browser
    HTMLFILE = out_path+'/plot_html/day_%s_output.html' %date
    f = open(HTMLFILE, 'w')

    f.write('<link rel="stylesheet" type="text/css" href="/Users/schae/testarea/finances/jquery-stockquotes/bower_components/jquery-stockquotes/dist/jquery.stockquotes.css" />\n')
    f.write('<script type="text/javascript" src="/Users/schae/testarea/finances/jquery-stockquotes/bower_components/jquery-stockquotes/dist/jquery.stockquotes.js"></script>\n')
    
    #<img src="graph_legend.png" />
    table_data = [
        ['Stock','Price','MA'],
        ]
    for i in stock_list:
        genPlotPage(i[0],date)
        table_line=[i[0],5.0, '<span class="stock-quote" data-symbol="%s"></span>' %i[0],'<img src="%s/ma/%s_%s.png" alt="N/A" width="400" />' %(out_path,i[0],date)]
        table_data+=[table_line]
        
    htmlcode = HTML.table(table_data)
    #print htmlcode
    f.write(htmlcode)
    #f.write('<p>')

    #f.write('Twitter: <span class="stock-quote" data-symbol="TWTR"></span>')
    #<script type="text/javascript" src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
    #<script type="text/javascript" src="../dist/jquery.stockquotes.js"></script>
    #<script type="text/javascript">
    #  $(document).ready(function () {
    #    $('.stock-quote').stockQuote();
    #  });
    #</script>
    
    f.write("\n<script>\n$('.stock-quote').stockQuotes();\n</script>")
    #print '-'*79
    
    f.close()
    
if __name__ == "__main__":
    main()
