# -*- coding: utf-8 -*-
"""Forecasting_Passengers_SARIMA.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YrdCy52i-oc3FKg2CoMcrrtOvhZ92DVZ

## **SARIMA Model**
"""

#Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX

#Loading Dataset
df = pd.read_csv('/content/AirPassengers.csv')
df.head()

#Cleaning Of the Dataset
df.columns = ["Month","Passengers"]
df.head()

df.isna().sum()

df['Month'] = pd.to_datetime(df['Month'])
df.set_index('Month',inplace = True)
df.head()

df.describe()

#Data Visualization
df.plot()

#Stationarity Check of the dataset
def test_stationarity(dataFrame, var):
    dataFrame['Rolling mean']  = dataFrame[var].rolling(window=12).mean()
    dataFrame['Rolling std']  = dataFrame[var].rolling(window=12).std()

    adftest = adfuller(dataFrame[var],autolag='AIC')
    statistics = pd.Series(adftest[0:4],index=['Test Statistic','p-value','Number of lags used','Number of observations used'])
    print(statistics)

    for key, values in adftest[4].items():
        print('criticality',key,":",values)

    sns.lineplot(data=dataFrame,x=dataFrame.index,y=var)
    sns.lineplot(data=dataFrame,x=dataFrame.index,y='Rolling mean')
    sns.lineplot(data=dataFrame,x=dataFrame.index,y='Rolling std')

test_stationarity(df,'Passengers')

#Transformation of data using logShift
log_shift = df[['Passengers']].copy(deep=True)
log_shift['log'] = np.log(log_shift['Passengers'])
log_shift['logShift'] = log_shift['log'].shift()
log_shift['logShiftDiff'] = log_shift['log'] - log_shift['logShift']
log_shift.head()

test_stationarity(log_shift.dropna(),'logShiftDiff')

#Seasonal Differencing
df2 = df[['Passengers']].copy(deep=True)
df2['Seasonal Diff'] = df2['Passengers'].diff(12)
df2.head()

#Splitting of data into Train & Test
train = df2[:round(len(df2)*80/100)]
test = df2[round(len(df2)*80/100):]

#SARIMA model
model = SARIMAX(train['Passengers'],order=(1,1,1),seasonal_order=(1,1,1,12))
model_fit = model.fit()
Prediction = model_fit.predict(start=test.index[0],end=test.index[-1])
df2['SarimaxPred'] = Prediction
df2.plot()

#Model Evaluation
np.sqrt(mean_squared_error(test['Passengers'],Prediction))

#Forecasting data
FuturePred = pd.DataFrame(pd.date_range(start='1961-01-01', end='1965-12-01', freq='MS'), columns=['Month'])
FuturePred.set_index('Month', inplace=True)
model_fit.predict(start=FuturePred.index[0], end=FuturePred.index[-1]).plot(color='purple')