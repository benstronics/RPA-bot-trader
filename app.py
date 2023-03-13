import logging
from referencias import Referencias
from interface import Interface
import rpa
import analise_dados as anl
import threading as td
from functools import partial
import time

gui = Interface()
ref = Referencias(gui=gui)

# Define the current simbol to predict
simbol='EUR/USD'

# Interval of historical data to generate model
# the value represent the position of this element on the table website
# exemple 5 correspont to the position of 1hour interval in that table
interval_historic = 5
interval_now = 5

df_data = None
df_target = None
lista = None
model = 'PassiveAggressiveRegressor'
loop=False
buy = False
sell =False

def download_historical(*args):
    global simbol
    rpa.download_historical_data(simbol.replace('/',''),interval_historic,ref)

def treat_data(*args):
    global df_data, df_target
    df_data, df_target = anl.load_and_treat_data()

def generate_models(*args):
    if df_data is not None and df_target is not None:
        anl.generate_model(df_data, df_target)
    else:
        gui.warning('Data not defined load and treat first!')

def get_forex_now(*args):
    global lista,simbol,interval_now
    lista = rpa.rpa_get_values_cotation(False,simbol,interval_now,ref)

def load_and_predict(*args):
    global lista, model,buy,sell
    result,open_f,close_f = anl.load_model_and_test(model,lista)
    print(result[0],open_f,close_f)
    buy,sell = anl.decide_order_buy_sell(result[0],open_f,close_f)

def define_simbol(*args):
    global simbol
    while True:
        resp = gui.ask_user('Write the forex simbol')
        if len(resp)>0:
            simbol = resp
            with open('simbol.txt','w') as f:
                f.write(simbol)
            break
def define_model(*args):
    global model
    while True:
        resp = gui.ask_user('Write name model')
        if len(resp)>0:
            model = resp
            with open('model.txt','w') as f:
                f.write(model)
            break
def define_interval_historic(*args):
    global interval_historic
    while True:
        resp = gui.ask_user('Write interval historic')
        if len(resp)>0:
            interval_historic = resp.strip()
            with open('interval_historic.txt','w') as f:
                f.write(interval_historic)
            break
def define_interval_now(*args):
    global interval_now
    while True:
        resp = gui.ask_user('Write interval now')
        if len(resp)>0:
            interval_now = resp.strip()
            with open('interval_now.txt','w') as f:
                f.write(interval_now)
            break

def define_loop(*args):
    global loop
    while True:
        resp = gui.ask_user('Write "yes"-> to loop / "no" -> to not loop').lower().strip()
        if 'yes' == resp or 'no' == resp:
            with open('loop.txt','w') as f:
                f.write(resp)
            loop = True if 'yes' == resp else False
            break

def load_variables(*args):
    try:
        with open('simbol.txt', 'r') as f:
            global simbol
            # Load the contents of the file into a variable
            data = f.read()
            print(data)
            simbol=data
        print(simbol)
    except Exception as e:
        logging.exception(e)
        with open('simbol.txt', 'w') as f:
            f.write(simbol)
    try:
        with open('model.txt', 'r') as f:
            global model
            # Load the contents of the file into a variable
            data = f.read()
            print(data)
            model=data
        print(model)
    except Exception as e:
        logging.exception(e)
        with open('model.txt', 'w') as f:
            f.write(model)
    try:
        with open('interval_historic.txt', 'r') as f:
            global interval_historic
            # Load the contents of the file into a variable
            data = f.read()
            print(data)
            interval_historic=int(str(data).strip())
        print(interval_historic)
    except Exception as e:
        logging.exception(e)
        with open('interval_historic.txt', 'w') as f:
            f.write(str(interval_historic))
    try:
        with open('interval_now.txt', 'r') as f:
            global interval_now
            # Load the contents of the file into a variable
            data = f.read()
            print(data)
            interval_now=int(str(data).strip())
        print(interval_now)
    except Exception as e:
        logging.exception(e)
        with open('interval_now.txt', 'w') as f:
            f.write(str(interval_now))
    try:
        with open('loop.txt', 'r') as f:
            global loop
            # Load the contents of the file into a variable
            data = f.read()
            print(data)
            loop= True if 'yes' == str(data).strip().lower() else False
        print(loop)
    except Exception as e:
        logging.exception(e)
        with open('loop.txt', 'w') as f:
            f.write('no')

def complete_process(*args):
    global df_data,df_target,simbol,interval_historic,interval_now,loop,buy,sell
    td.Thread(target=partial(rpa.trade, 0, ref)).start()
    rpa.download_historical_data(simbol.replace('/',''),interval_historic,ref)
    df_data, df_target = anl.load_and_treat_data()
    anl.generate_model(df_data, df_target)
    while True:
        lista = rpa.rpa_get_values_cotation(False, simbol,interval_now,ref)
        result, open_f, close_f = anl.load_model_and_test(model, lista)
        print(result[0], open_f, close_f)
        buy,sell = anl.decide_order_buy_sell(result[0], open_f, close_f)
        print('Buy',buy)
        print('Sell',sell)
        time.sleep(300)
        if not loop:
            #input()
            break

def send_order_buy():
    global buy
    buy=True

def send_order_sell():
    global sell
    sell = True

def trade_forex():
    global buy,sell
    rpa.trade(5,ref)

def thread1():
    td.Thread(target=download_historical).start()
def thread2():
    td.Thread(target=treat_data).start()
def thread3():
    td.Thread(target=generate_models).start()
def thread4():
    td.Thread(target=get_forex_now).start()
def thread5():
    td.Thread(target=load_and_predict).start()
def thread6():
    td.Thread(target=complete_process).start()
def thread7():
    td.Thread(target=trade_forex).start()
def thread8():
    td.Thread(target=send_order_buy).start()
def thread9():
    td.Thread(target=send_order_sell).start()


def app(title):
    while True:
        load_variables()
        gui.titulo = title
        list_options = [define_simbol,define_model,define_interval_historic,define_interval_now,define_loop]
        list_buttons=['Download Historical data','Treat data','Generate Models','Get forex values now','Load model and predict','Complete process','Trade','Buy','Sell']
        list_functions = [thread1, thread2, thread3, thread4, thread5, thread6, thread7, thread8, thread9]
        gui.select_options(['Define simbol','Define model','Define interval historic','Define interval now','Define loop'],list_optional_function=list_options)
        gui.create_menu_buttons(9,list_buttons,list_functions)
        gui.loop()