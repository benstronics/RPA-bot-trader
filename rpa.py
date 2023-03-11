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

ref = Referencias()

def get_src(elements):
    try:
        srcs =[element.get_attribute('src') for element in elements if 'http' in element.get_attribute('src')]
        return srcs
    except Exception as e:
        logging.exception(e)

def rpa_get_values_cotation(loop:bool=True,simbol:str='BTC/USD'):
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

if __name__ == '__main__':
    lista = rpa_get_values_cotation(False)
    print(lista)