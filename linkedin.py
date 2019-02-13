from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from flask import jsonify
import shutil
import random
import time
import json
import urllib.parse

contador=0

def start(user,password,keyword,limit=100):
    #print(time.ctime())
    openBrowser()  
    login(user,password)
    pesquisar(keyword,limite=limit)

def openBrowser():
    global randomPath
    chrome_Options =  Options()
    #chrome_Options.add_argument("--user-data-dir=C:\\Users\\Administrator\\Desktop\\RPA\\hydra-rpa\\caj\\")
    chrome_Options.add_argument("--disable-dev-shm-usage")
    chrome_Options.add_argument("--log-level=3")
    chrome_Options.add_argument("--disable-infobars")
    chrome_Options.add_argument("--disable-extensions")
    chrome_Options.add_argument("--disable-gpu")
    chrome_Options.add_argument("--no-sandbox")
    # chrome_Options.add_argument('--headless')
    global driver
    driver = webdriver.Chrome(options=chrome_Options)
    driver.set_page_load_timeout(60)
    driver.get("https://www.linkedin.com/mynetwork/")
    
def login(userID,userPass):
    global idUser
    global senhaUser
    idUser = userID
    senhaUser = userPass
    time.sleep(2)
    driver.switch_to.frame(driver.find_element_by_xpath("//*[@id='ember5']/div[5]/iframe"))
    driver.find_element_by_xpath('//*[@id="uno-reg-join"]/div/div/div/div[2]/div[1]/div[1]/div[2]/p/a').click()
    # driver.switch_to.frame("conteudo")
    # driver.switch_to.frame("acesso")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'session_key')))
    driver.execute_script("document.getElementsByName('session_key')[0].value='"+idUser+"'")
    driver.execute_script("document.getElementsByName('session_password')[0].value='"+senhaUser+"'")
    driver.execute_script('document.forms[0].submit()')
    # #assert "LOGIN INVÁLIDO!" not in driver.page_source
    
def pesquisar(termos,page=1,limite=100):

    if page < limite:
        global contador
        #driver.get("https://www.linkedin.com/search/results/all/?keywords=" + urllib.parse.quote_plus(termos) + "&origin=GLOBAL_SEARCH_HEADER&page=" + str(page))
        driver.get("https://www.linkedin.com/search/results/people/?keywords=" + urllib.parse.quote_plus(termos) + "&origin=CLUSTER_EXPANSION&page=" + str(page))
        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ember77"]/div/div/a'))).click()
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        #buttonsConectar = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME , '.search-result__actions--primary.button-secondary-medium.m5')))
        #driver.find_element_by_xpath("//*[@id='ember583']/div/ul/li/div/div/div[3]/div/button")
        buttonsConectar = driver.find_elements_by_xpath('//*[contains(@aria-label, "Conecte-se")]')
        
        try:
            for a in buttonsConectar:
                #buttonConectar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH , '//button[contains(@aria-label, "Conecte-se")]')))
                #buttonConectar = driver.find_element_by_tag_name("button")
                try:
                    a.click()
                except:
                    continue
                time.sleep(1)
                driver.find_element_by_xpath('//*[contains(@class, "button-primary-large")]').click()
                time.sleep(1)
            raise Exception
        except Exception as e:
            print(e)
            buttonsConectar = driver.find_elements_by_xpath('//*[contains(@aria-label, "Conecte-se")]')
            if len(buttonsConectar) > 0 and contador < 3:
                contador = contador + 1
                pesquisar(termos,page)
            else:
                contador = 0
                pesquisar(termos,page+1)
            return
        
        pesquisar(termos,page+1)
    return
