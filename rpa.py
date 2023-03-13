import logging
import os
import time
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from referencias import Referencias
from selenium.webdriver.common.keys import Keys
#from interface import Interface
import undetected_chromedriver as uc
import pyperclip



def get_src(elements):
    try:
        srcs =[element.get_attribute('src') for element in elements if 'http' in element.get_attribute('src')]
        return srcs
    except Exception as e:
        logging.exception(e)

def rpa_get_values_cotation(loop:bool=True,simbol:str='BTC/USD',interval:int=5,ref:object=None):
    link='https://tvc-invdn-com.investing.com/web/1.12.34/index60-prod.html?carrier=3e7e782c94cb1da90cd0ea195b2cd764&time=1678560759&domain_ID=1&lang_ID=1&timezone_ID=8&version=1.12.34&locale=en&timezone=America/New_York&pair_ID=945629&interval=5&session=24x7&prefix=www&suffix=&client=1&user=247776956&family_prefix=tvc6&init_page=instrument&sock_srv=https://streaming.forexpros.com&m_pids=&watchlist=&geoc=BR&site=https://www.investing.com'
    lista=[]

    # configurando argumentos para inicialização do chrome
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
        # Disable Chrome's PDF Viewer
        "download.extensions_to_open": "applications/pdf",
        'plugins.always_open_pdf_externally': True
    })
    headless = str(ref.criar_filtros([0], ['headless'], 'filtro_chromedriver_headless')['headless'][0]).strip()
    if int(headless)==1:
        options.add_argument('headless')
    chrome_service = Service(ChromeDriverManager(path=os.getcwd()).install())
    chrome_service.creationflags = CREATE_NO_WINDOW
    driver = webdriver.Chrome(service=chrome_service, options=options)
    while True:
        try:
            driver.get(link)

            # create an ActionChains object
            actions = ActionChains(driver)

            # Encontrando 1° iframe
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.TAG_NAME, 'iframe')))
            iframe = driver.find_element(By.TAG_NAME, 'iframe')
            print(iframe)
            driver.switch_to.frame(iframe)


            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pane-legend-item-value-wrap')))

            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'symbol-edit')))
            actions.double_click(elemento).perform()
            actions.send_keys(Keys.DELETE).perform()
            elemento.send_keys(simbol,Keys.ENTER)
            script="""
            document.getElementsByClassName('submenu apply-common-tooltip')[0].click();
            """
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[3]/div/span')))
            driver.execute_script(script)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'/html/body/div[13]/span[{interval}]'))).click()
            while True:
                script="""
                var text = document.getElementsByClassName('symbol-edit')[0].value;
                return text
                """
                text = driver.execute_script(script)
                print(text)
                if simbol.upper() in str(text).upper().strip():
                    time.sleep(3)
                    break

        except Exception as e:
            logging.exception(e)
            continue

        status=False
        while not status:
            try:
                script="""
                document.addEventListener("DOMContentLoaded", function() {
                  console.log("HTML content has loaded!");
                });
            
                var elementos = document.getElementsByClassName('pane-legend-item-value-wrap');
                var lista = []
                for (let i = 0; i < elementos.length; i++) {
                  lista.push(elementos[i].innerText);
                }
                console.log(lista)
                return lista
                """
                lista = driver.execute_script(script)
                print(lista)
                tamanho_valores = [len(valor) for valor in lista]
                if not 4 in tamanho_valores:
                    lista = [valor[1:] for valor in lista]
                    print(lista)
                    status = True
            except Exception as e:
                logging.exception(e)
        if not loop:
            break
    #input('digite')
    return lista

def download_historical_data(simbol,row:int=2,ref:object=None):
    try:
        os.mkdir('base')
    except Exception as e:
        logging.exception(e)

    link = 'https://forexsb.com/historical-forex-data'
    lista = []
    caminho = os.path.abspath(os.getcwd() + '/base')
    ref.delete_Files_Folder('base')
    # configurando argumentos para inicialização do chrome
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": caminho,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
        # Disable Chrome's PDF Viewer
        "download.extensions_to_open": "applications/pdf",
        'plugins.always_open_pdf_externally': True
    })
    headless = str(ref.criar_filtros([0], ['headless'], 'filtro_chromedriver_headless')['headless'][0]).strip()
    if int(headless) == 1:
        options.add_argument('headless')
    chrome_service = Service(ChromeDriverManager(path=os.getcwd()).install())
    chrome_service.creationflags = CREATE_NO_WINDOW
    driver = webdriver.Chrome(service=chrome_service, options=options)
    while True:
        try:
            driver.get(link)

            # create an ActionChains object
            actions = ActionChains(driver)

            # Encontrando 1° iframe
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.TAG_NAME, 'iframe')))
            iframe = driver.find_element(By.TAG_NAME, 'iframe')
            print(iframe)
            driver.switch_to.frame(iframe)

            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'select-symbol')))
            actions.double_click(elemento).perform()
            actions.send_keys(Keys.DELETE).perform()
            elemento.send_keys(simbol, Keys.ENTER)

            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'select-format')))
            elemento.click()

            options = elemento.find_elements(By.TAG_NAME,'option')
            for option in options:
                att = str(option.text).lower()
                if 'json' in att:
                    option.click()


            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'btn-load-data')))
            elemento.click()

            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="table-acquisition"]/tr[{row}]/td[6]/a')))
            elemento.click()
            time.sleep(5)
            ref.esperar_downloads(caminho)
            driver.quit()
            break
        except Exception as e:
            logging.exception(e)
            #input()

def trade(frame_hour:int=2,ref:object=None):
    global buy, sell
    try:
        os.mkdir('base')

    except Exception as e:
        logging.exception(e)

    credentials = ref.criar_credenciais('tickmill',['login','password'])

    link = 'https://www.tickmill.com/trade'
    link = 'https://trade.mql5.com/trade?version=4&trade_server=Tickmill-Live10&servers=Tickmill-Live,Tickmill-Live02,Tickmill-Live04,Tickmill-Live05,Tickmill-Live08,Tickmill-Live09,Tickmill-Live10,TickmillAsia-Live06,TickmillAsia-Live,Tickmill-Demo,Tickmill-DemoUK,TickmillAsia-Demo&lang=en&color_scheme=black_on_white&utm_source=https://www.tickmill.com/trade'
    lista = []

    caminho = os.path.abspath(os.getcwd() + '/base')
    ref.delete_Files_Folder('base')
    # configurando argumentos para inicialização do chrome
    # options = Options()
    # options.add_experimental_option("prefs", {
    #     "download.default_directory": caminho,
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True,
    #     "safebrowsing.enabled": True,
    #     "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    #     # Disable Chrome's PDF Viewer
    #     "download.extensions_to_open": "applications/pdf",
    #     'plugins.always_open_pdf_externally': True
    # })
    # headless = str(ref.criar_filtros([0], ['headless'], 'filtro_chromedriver_headless')['headless'][0]).strip()
    # if int(headless) == 1:
    #     options.add_argument('headless')
    # chrome_service = Service(ChromeDriverManager(path=os.getcwd()).install())
    # chrome_service.creationflags = CREATE_NO_WINDOW
    # driver = webdriver.Chrome(service=chrome_service, options=options)

    options2 = uc.ChromeOptions()
    options2.add_argument("--ignore-certificate-error")
    options2.add_argument("--ignore-ssl-errors")
    options2.add_experimental_option("prefs", {
        "download.default_directory": caminho,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
        # Disable Chrome's PDF Viewer
        "download.extensions_to_open": "applications/pdf",
        'plugins.always_open_pdf_externally': True
    })
    #ChromeDriverManager(path=os.getcwd()).install()

    # if headless == 1:
    #     pass
    # if headless == 2:
    #     options2.headless = True
    # if len(profile_path) > 0:
    #     options2.add_argument(f"--user-data-dir={profile_path}")
    driver = uc.Chrome(options=options2)
    while True:
        try:
            driver.get(link)

            # create an ActionChains object
            actions = ActionChains(driver)

            # Encontrando 1° iframe
            # time.sleep(5)
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            #     (By.TAG_NAME, 'iframe')))
            # iframe = driver.find_element(By.TAG_NAME, 'iframe')
            # source = str(iframe.get_attribute('src'))
            # print(source)
            # with open('source.txt','w') as f:
            #     f.write(source)
            # print(iframe)
            # #driver.switch_to.frame(iframe)
            # driver.get(source)
            time.sleep(5)

            script="""
            var elemento = document.getElementsByTagName('input')[6];
            return elemento
            """
            elemento = driver.execute_script(script)
            elemento.send_keys(ref.descriptografar_dados(credentials['LOGIN']).strip())

            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.ID, 'password')))
            password = ref.descriptografar_dados(credentials['PASSWORD'])#.strip()

            pyperclip.copy(password)
            elemento.click()
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()


            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.TAG_NAME, 'select')))
            elemento.click()
            time.sleep(5)
            options = elemento.find_elements(By.TAG_NAME,'option')
            for option in options:
                att = str(option.get_attribute('value')).strip()
                if 'Tickmill-DemoUK' in att:
                    option.click()
                    break
            elemento.click()
            elemento = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[14]/div/div[3]/button[2]')))
            elemento.click()
            time.sleep(10)
            while True:
                try:
                    print('Tentando clickar...')
                    script=f"""
                    document.getElementsByClassName('page-bar-button iconed')[{frame_hour+17}].click();
                    """
                    driver.execute_script(script)
                    print('clickou')
                    break
                except Exception as e:
                    logging.exception(e)
            while True:
                import app
                try:
                    script="""
                    var buttons = document.getElementsByClassName('but');
                    return buttons
                    """
                    buttons = driver.execute_script(script)
                    if app.buy:
                        print('Comprando')
                        buttons[1].click()
                        time.sleep(3)
                        try:
                            acpt="""
                            document.getElementById('one-click-accept').click();
                            document.getElementsByClassName('input-button')[23].click();
                            """
                            driver.execute_script(acpt)
                            buttons[1].click()
                        except Exception as e:
                            logging.exception(e)
                        print('Clickou')
                        app.buy = False
                    if app.sell:
                        print('Vendendo')
                        buttons[0].click()
                        time.sleep(3)
                        try:
                            acpt = """
                            document.getElementById('one-click-accept').click();
                            document.getElementsByClassName('input-button')[23].click();
                            """
                            driver.execute_script(acpt)
                            buttons[0].click()
                        except Exception as e:
                            logging.exception(e)
                        print('Clickou')
                        app.sell = False
                except Exception as e:
                    logging.exception(e)


            input()
        except Exception as e:
            logging.exception(e)
            input()


if __name__ == '__main__':
    global buy,sell
    buy = False
    sell = True
    trade()