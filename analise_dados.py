import json
import logging

import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.linear_model import PassiveAggressiveRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import max_error
import pickle
import os
import rpa

def convert_to_int_seconds(hour_str):
    time_obj = datetime.strptime(hour_str, '%H:%M:%S')
    seconds = timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()
    return seconds

def load_and_treat_data():
    try:
        os.mkdir('base')
    except Exception as e:
        logging.exception(e)
    file = os.listdir('base')[0]
    # Open the JSON file
    with open(f'base\{file}', 'r') as f:
        # Load the contents of the file into a variable
        data = json.load(f)

    # Now you can use the data variable to access the contents of the JSON file
    print(data.keys())
    df=pd.DataFrame()
    for key in data.keys():
        type_key = type(data[key])
        if 'list' in str(type_key):
            print(key)
            print(data[key][:10])
            if len(data[key])>0:
                df[key] = data[key]
        else:
            print(key,data[key])

    df['time'] = [str(datetime.fromtimestamp(int(seconds))) for seconds in df['time']]
    df[['data', 'time']]= df['time'].str.split(' ', 1, expand=True)
    df_data = df.drop(['close','data','volume'],axis=1)#,'high','low'
    df_target = df['close']

    df_data.time = [int(convert_to_int_seconds(hour_str)) for hour_str in df_data.time.tolist()]
    return df_data, df_target

def generate_model(df_data, df_target):
    try:
        os.mkdir('models')
    except Exception as e:
        logging.exception(e)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(df_data, df_target, test_size=0.2,
                                                        random_state=42)


    # Train
    model1 = PassiveAggressiveRegressor()
    model1.fit(X_train, y_train)

    model2 = Ridge(alpha=.5, solver='auto')
    model2.fit(X_train, y_train)


    model3 = LinearRegression()
    model3.fit(X_train, y_train)

    print('PassiveAggressiveRegressor model')
    # Evaluate the model
    y_pred = model1.predict(X_test)
    print(y_test)
    print(y_pred)
    # save the trained model
    filename = 'models/PassiveAggressiveRegressor.sav'
    pickle.dump(model1, open(filename, 'wb'))

    # compute the mean squared error
    mse = mean_squared_error(y_test, y_pred)
    print("MSE: ", mse)

    # compute the mean squared error
    r2 = r2_score(y_test, y_pred)
    print("r2_score: ", r2)

    max_e = max_error(y_test, y_pred)
    print("max_error: ", max_e)

    print('#' * 20)

    print('Ridge model')
    # Evaluate the model
    y_pred = model2.predict(X_test)
    print(y_test)
    print(y_pred)
    # save the trained model
    filename = 'models/Ridge.sav'
    pickle.dump(model2, open(filename, 'wb'))

    # compute the mean squared error
    mse = mean_squared_error(y_test, y_pred)
    print("MSE: ", mse)

    # compute the mean squared error
    r2 = r2_score(y_test, y_pred)
    print("r2_score: ", r2)

    max_e = max_error(y_test, y_pred)
    print("max_error: ", max_e)

    print('#' * 20)

    print('LinearRegression model')
    # Evaluate Tree model
    y_pred = model3.predict(X_test)
    print(y_test)
    print(y_pred)
    # save the trained model
    filename = 'models/LinearRegression.sav'
    pickle.dump(model3, open(filename, 'wb'))

    # compute the mean squared error
    mse = mean_squared_error(y_test, y_pred)
    print("MSE: ", mse)

    # compute the mean squared error
    r2 = r2_score(y_test, y_pred)
    print("r2_score: ", r2)

    max_e = max_error(y_test, y_pred)
    print("max_error: ", max_e)

def load_model_and_test(model,lista):
    df_test = pd.DataFrame()
    horario = datetime.today() - timedelta(hours=1)
    print(horario)
    df_test.loc[0, 'time'] = str(horario).split()[1].split('.')[0]
    df_test.time = [int(convert_to_int_seconds(hour_str)) for hour_str in df_test.time.tolist()]
    df_test.loc[0, 'open'] = lista[0]
    df_test.loc[0, 'high'] = lista[1]
    df_test.loc[0, 'low'] = lista[2]
    open_f = lista[0]
    close = lista[3]
    print('df_test')
    print(df_test)

    # load the saved model
    with open(f'models/{model}.sav', 'rb') as file:
        # Load the contents of the file into a variable
        #file = f.read()
        loaded_model = pickle.load(file)
        result = loaded_model.predict(df_test)
        print(result)
    return result,open_f,close

def decide_order_buy_sell(predicted,open,close_now):
    if float(predicted)<float(open) and float(predicted)<float(close_now):
        sell = True
        buy = False
    elif float(predicted)>float(open) and float(predicted)>float(close_now):
        buy = True
        sell = False
    else:
        sell = False
        buy = False
    return sell, buy
if __name__ == '__main__':
    # rpa.download_historical_data('eurusd',5)
    # df_data, df_target = load_and_treat_data()
    # generate_model(df_data, df_target)
    lista = rpa.rpa_get_values_cotation(False,'EUR/USD')
    load_model_and_test('PassiveAggressiveRegressor', lista)