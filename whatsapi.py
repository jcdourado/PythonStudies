import time
import base64
from databaseconnector import Database
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from datetime import datetime
from flask import Flask, request, jsonify

saltWhatsAPI = 'DJjashjkdhsauUU2321JKSAo'

def sendMessage(driver):

    try:
        elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//*[@id='side']/div[1]/div/label/input"))
            )

        content = request.json
        elem.send_keys(content["contactNumber"])

        elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//*[@id='pane-side']/div/div/div/div[1]"))
            )

        elem.click()

        driver.implicitly_wait(8) 
        elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//*[@id='main']/footer/div[1]/div[2]/div/div[2]"))
            )

        elem.clear()
        elem.send_keys(content["message"])
        elem.send_keys(Keys.RETURN)
        return jsonify({"message":"Mensagem Enviada com Sucesso!"})

    except Exception as e:
        return jsonify({"message":"Falha ao enviar Mensagem!"})

def iteractOverMessages(driver):

    try:
        driver.implicitly_wait(2)

        while EC.presence_of_element_located((By.CLASS_NAME ,"_15G96")):
            elem = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME ,"_15G96"))
                )
            
            elemClicable = elem.find_element_by_xpath("../../..")
            elemClicable.click()

            # Tudo abaixo faz a mesma coisa
            # elem = WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located((By.XPATH,"//*[@id='side']/div[1]/div/label/input"))
            #     )
            # elem.send_keys("Amor")

            # driver.implicitly_wait(8)

            # target = driver.find_element_by_xpath('//span[@title= "{}"]'.format("Amor"))
            # target.click()

            driver.implicitly_wait(8) 

            client = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME ,"_1f1zm"))
                )

            clientName = client.find_element_by_class_name("_25Ooe")

            inputMessage = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//*[@id='main']/footer/div[1]/div[2]/div/div[2]"))
                )

            with Database() as db:
                db.query("SELECT id FROM whatsapp_api.clients WHERE UPPER(name) = UPPER(%s)", (clientName.text.strip(), ))
                clientDB = db.fetchall()
                if not clientDB:
                    db.query("INSERT INTO whatsapp_api.clients (name, active) VALUES (%s, 1)", (clientName.text.strip(), ))
                    db.query("SELECT id FROM whatsapp_api.clients WHERE UPPER(name) = UPPER(%s)", (clientName.text.strip(), ))
                    clientDB = db.fetchall()

            lastMessage = getLastMessageClient(driver,"rtl",clientDB[0][0])

            #print(lastMessage)
            messageToSend = iteractOverLastMessage(driver,lastMessage)

            inputMessage.clear()
            inputMessage.send_keys(messageToSend)
            #inputMessage.send_keys(Keys.RETURN)

            current_Date = datetime.now()
            formatted_date = current_Date.strftime('%Y-%m-%d %H:%M:%S')

            hashMessage = '{}|||{}'.format(formatted_date,saltWhatsAPI)
            hashMessage = base64.b64encode(hashMessage.encode()) 

            with Database() as db:
                db.query("INSERT INTO whatsapp_api.messagesSent (hash_message, message, id_client, date_message) VALUES (%s,%s,%s,%s)", (hashMessage, messageToSend, clientDB[0][0], formatted_date))


            try:
                elem = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME ,"_15G96"))
                    )
            except Exception as e:
                return jsonify({
                        "message":"Mensagem Enviada com Sucesso!", 
                        "hash": hashMessage.decode("utf-8") 
                        })


    except Exception as e:
        raise e

def getLastMessageClient(driver,textDirection,id_client):
    """
        Pegar a ultima mensagem do cliente
    """
    messages = None

    while(1):
        try:
            SCROLL_PAUSE_TIME = 1.1

            # Get scroll height
            last_height = driver.execute_script("return document.getElementsByClassName('_2nmDZ')[0].scrollHeight")

            while True:
                # Scroll down to bottom
                driver.execute_script("document.getElementsByClassName('_2nmDZ')[0].scrollTop = 0;")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.getElementsByClassName('_2nmDZ')[0].scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            messages = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH,"//*[contains(@class, 'message-in')]/div/div/*[contains(@class, '_3zb-j')]"))
            )

            newMessage = ""
            current_Date = datetime.now()

            for message in messages:
                with Database() as db:
                    db.query("SELECT id FROM whatsapp_api.messages WHERE UPPER(message) = UPPER(%s) and id_client = %s and opened = 0", (message.text, id_client, ))
                    messageDB = db.fetchall()

                    if not messageDB:
                        hourMessage = message.find_element_by_xpath("../../../div/*[contains(@class, '_2f-RV')]/*[contains(@class, '_1DZAH')]/*[contains(@class, '_3EFt_')]")
                        formatted_date = current_Date.strftime('%Y-%m-%d {}:{}:00'.format(hourMessage.text[:2],hourMessage.text[3:5]))
                        db.query("INSERT INTO whatsapp_api.messages (message, id_client, date_message, opened) VALUES (%s, %s, %s, 1)", (message.text, id_client, formatted_date))
                        newMessage = newMessage + " - " + message.text

            return newMessage

        except (NoSuchElementException, StaleElementReferenceException) as e:
            pass

def iteractOverLastMessage(driver,message):
    """
        Posteriormente jogar para um banco as perguntas
        E respostas
    """
    messagesHello = ["OI","OLÁ","OLA","BOM DIA", "BOA TARDE", "BOA NOITE"]

    message = message.upper()
    if any(elem in message for elem in messagesHello):
        return "Olá, boa tarde"

    return "Mensagem não encontrada"

def readAllMessages(textDirection):
    global driver    

    messages = None
    lastMessage = None

    messages = driver.find_elements_by_class_name("_3zb-j")
    lastMessage = messages[-1].text
    lastMessage = lastMessage[::-1]

    while(1):
        try:
            messages = driver.find_elements_by_class_name("_3zb-j")
            if(textDirection == "rtl"):
                for i in range(len(messages)):
                    messages[i] = messages[i][::-1]

            return messages
                    
        except (NoSuchElementException, StaleElementReferenceException) as e:
            pass