
import os
import getpass
import requests
import numpy as np
import pandas as pd
from datetime import datetime as dt
from bokeh.layouts import column
from bokeh.plotting import figure, show, output_file

os.chdir('C:/Users/' + str(getpass.getuser()) +'/Desktop/Data')

# Download Data
Ticker = 'GOOG'
Url  = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+str(Ticker)+ '&apikey={}'
Api  = open('API.txt','r').read()
Json = requests.get(Url.format(Api))
Json = Json.json()['Time Series (Daily)']

Data = pd.DataFrame(columns=['Date','Open','High','Low','Close','Volume'])
for d,p in Json.items():
    date = dt.strptime(d, '%Y-%m-%d').date()
    data_row=[date,float(p['1. open']),float(p['2. high']),float(p['3. low']),float(p['4. close']),int(p['6. volume'])]
    Data.loc[-1,:]=data_row
    Data.index=Data.index+1
Data=Data.sort_values('Date')
Data.set_index('Date', inplace=True)
del (Json,  Url, Api, d, data_row, date, p)

# Plot Graph
Candle = figure(background_fill_color = 'black',
                width=1350,height=530,
                sizing_mode='scale_width',
                toolbar_location='right',
                toolbar_sticky=False,
                tools = 'pan,wheel_zoom,box_zoom,reset')

Candle.segment(Data.index, Data.High, Data.index, Data.Low, color='White')

def inc_dec (c, o):
    if c > o:
        value = 'Increase'
    elif c < o:
        value = 'Decrease'
    else:
        value = 'Equal'
    return value

Data['Status'] = [inc_dec(c, o) for c, o in zip(Data.Close, Data.Open)]
Data['Middle'] = (Data.Open + Data.Close) / 2
Width = 12 * 60 * 60 * 1000 * 1.5
Data['Height'] = abs(Data.Close - Data.Open)

Candle.rect(Data.index[Data.Status=='Increase'],
            Data.Middle[Data.Status=='Increase'],
            Width,
            Data.Height[Data.Status=='Increase'],
            fill_color = '#007FFF',
            line_color = 'black')

Candle.rect(Data.index[Data.Status=='Decrease'],
            Data.Middle[Data.Status=='Decrease'],
            Width,
            Data.Height[Data.Status=='Decrease'],
            fill_color = '#ff4500',
            line_color = 'black')

Candle.xaxis.visible = False
Candle.title.text = Ticker + ' Daily OHLC- Crossover'
Candle.title_location = 'above'
Candle.title.text_color = 'Blue'
Candle.title.text_font = 'times'
Candle.title.text_font_size = '15pt'
Candle.grid.grid_line_alpha = 0.2

# Add Moving Average
Data['SMA'] = Data['Close'].rolling(window=10).mean()
Data['LMA'] = Data['Close'].rolling(window=30).mean()
Candle.line(Data.index, Data.SMA, line_width=2, line_color='white', legend="SMA: 10")
Candle.line(Data.index, Data.LMA, line_width=2, line_color='orange',legend="LMA: 30")
Candle.legend.location = (10,370)
Candle.legend.background_fill_color = 'black'
Candle.legend.label_text_color = 'white'
Candle.legend.label_text_font = 'times'

# Add signals
Data['SMA1'] = Data['Close'].rolling(window=10).mean().shift(1)
Data['LMA1'] = Data['Close'].rolling(window=30).mean().shift(1)
Data['Buy']  = Data.apply(lambda x : x['SMA']-(.03*x['SMA']) if x['SMA'] > x['LMA'] and 
                                     x['SMA1'] < x['LMA1'] else np.NaN, axis=1)
Data['Sell'] = Data.apply(lambda x : x['LMA']+(.03*x['LMA']) if x['SMA'] < x['LMA'] and 
                                     x['SMA1'] > x['LMA1'] else np.NaN, axis=1)

Candle.circle(Data.index, Data.Buy,size=25, fill_color="black", line_color="#00FF00",line_width=2)
Candle.circle(Data.index, Data.Sell,size=25, fill_color="black", line_color="red",line_width=2)
Candle.triangle(Data.index, Data.Buy, size=15, color="#00FF00", legend='Buy')
Candle.inverted_triangle(Data.index, Data.Sell, size=15, color="red", legend='Sell')

# Add Volume
Volume = figure(x_axis_type='datetime',
                background_fill_color = '#E0E0E0',
                width=1350,height=160,
                sizing_mode='scale_width',
                toolbar_location=None)
Volume.vbar(Data.index, Width, (Data.Volume/10000))
Volume.grid.grid_line_alpha = 1
Volume.left[0].formatter.use_scientific = False
Volume.title.text = '  Volume  (x10000)'
Volume.title_location = 'right'
Volume.title.text_font = 'times'
Volume.title.text_font_size = '11pt'

output_file('Output.html')
show(column(Candle,Volume))