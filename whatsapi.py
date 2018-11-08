import time
import base64
from databaseconnector import Database
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

saltWhatsAPI = 'DJjashjkdhsauUU2321JKSAo'

def sendMessage(driver):

    try:
        elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//*[@id='side']/div[1]/div/label/input"))
            )

        content = request.json
        elem.clear()
        elem.send_keys(content["contactNumber"])

        time.sleep(4)

        elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//*[@id='pane-side']/div/div/div/div[1]"))
            )

        elem.click()

        driver.implicitly_wait(8) 

        client = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME ,"_1f1zm"))
            )

        clientName = client.find_element_by_class_name("_25Ooe")

        with Database() as db:
            db.query("SELECT id FROM whatsapp_api.clients WHERE UPPER(name) = UPPER(%s)", (clientName.text.strip(), ))
            clientDB = db.fetchall()
            if not clientDB:
                db.query("INSERT INTO whatsapp_api.clients (name, active) VALUES (%s, 1)", (clientName.text.strip(), ))
                db.query("SELECT id FROM whatsapp_api.clients WHERE UPPER(name) = UPPER(%s)", (clientName.text.strip(), ))
                clientDB = db.fetchall()

        elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//*[@id='main']/footer/div[1]/div[2]/div/div[2]"))
            )

        elem.clear()
        elem.send_keys(content["message"])
        elem.send_keys(Keys.RETURN)

        current_Date = datetime.now()
        formatted_date = current_Date.strftime('%Y-%m-%d %H:%M:%S')

        hashMessage = '{}|||{}|||{}'.format(formatted_date,clientDB[0][0],saltWhatsAPI)
        hashMessage = base64.b64encode(hashMessage.encode()) 

        with Database() as db:
            db.query("INSERT INTO whatsapp_api.messagesSent (hash_message, message, id_client, date_message) VALUES (%s,%s,%s,%s)", (hashMessage, content["message"], clientDB[0][0], formatted_date))

        return jsonify({
                        "message":"Mensagem Enviada com Sucesso!",
                        "hash": hashMessage.decode("utf-8")
                        })

    except Exception as e:
        return jsonify({"message":"Falha ao enviar Mensagem!"})

def iteractOverMessages(driver):

    try:
        driver.implicitly_wait(2)

        hashes = []

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

            time.sleep(4)

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

            hashMessage = '{}|||{}|||{}'.format(formatted_date,clientDB[0][0],saltWhatsAPI)
            hashMessage = base64.b64encode(hashMessage.encode()) 

            with Database() as db:
                db.query("INSERT INTO whatsapp_api.messagesSent (hash_message, message, id_client, date_message) VALUES (%s,%s,%s,%s)", (hashMessage, messageToSend, clientDB[0][0], formatted_date))
                hashToJSON = {"name":clientName.text.strip(), "hash": hashMessage.decode("utf-8")}
                hashes.append(hashToJSON)

            try:
                elem = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME ,"_15G96"))
                    )

            except Exception as e:
                elem = driver.find_element_by_xpath("//*[@id='pane-side']/div/div/div/div/div/div[not(contains(@class, 'CxUIE'))]")
                elem.click()
                return jsonify({
                        "message":"Mensagem Enviada com Sucesso!", 
                        "hashes": hashes 
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

            weekday_name = ["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO", "DOMINGO"]

            for message in messages:
                with Database() as db:
                    messageDate = message.find_elements_by_xpath("../../../../preceding-sibling::div[contains(@class, '_3rjxZ')]")
                    hourMessage = message.find_element_by_xpath("../../../div/*[contains(@class, '_2f-RV')]/*[contains(@class, '_1DZAH')]/*[contains(@class, '_3EFt_')]")

                    if len(messageDate) == 2:
                        messageDate = messageDate[len(messageDate) - 2]
                    else:
                        messageDate = messageDate[len(messageDate) - 1]
                        
                    if messageDate.text == "HOJE":
                        messageDate = datetime.now()
                    elif messageDate.text == "ONTEM":
                        messageDate = datetime.now() - timedelta(days=1)
                    elif messageDate.text in weekday_name:
                        contDay = 2
                        auxMessageDate = datetime.now().date() - timedelta(days=contDay)
                        
                        while True:
                            if auxMessageDate.weekday() == weekday_name.index(messageDate.text):
                                messageDate = auxMessageDate
                                break
                            contDay = contDay + 1
                            auxMessageDate = datetime.now().date() - timedelta(days=contDay)

                    else:
                        auxMessageDate = messageDate.text.split("/")
                        messageDate = datetime(auxMessageDate[2],auxMessageDate[1].zfill(2),auxMessageDate[0].zfill(2))

                    formatted_date = messageDate.strftime('%Y-%m-%d {}:{}:00'.format(hourMessage.text[:2],hourMessage.text[3:5]))
                    
                    db.query("SELECT id FROM whatsapp_api.messages WHERE UPPER(message) = UPPER(%s) and id_client = %s and date_message = %s", (message.text, id_client, formatted_date))
                    messageDB = db.fetchall()

                    if not messageDB:
                        db.query("INSERT INTO whatsapp_api.messages (message, id_client, date_message) VALUES (%s, %s, %s)", (message.text, id_client, formatted_date))
                        newMessage = newMessage + " - " + message.text

            return newMessage

        except (NoSuchElementException, StaleElementReferenceException) as e:
            pass

def getStatusMessage(driver):
    """
        Pegar o Status da Mensagem de acordo com o Hash
    """
    content = request.json

    try:
        hashReceived = content["hash"]

        if hashReceived:
            with Database() as db:
                query = "SELECT cli.name, ms.message, STR_TO_DATE(ms.date_message, '%Y-%m-%d %H:%i:%S') date_message"
                query = query + " FROM whatsapp_api.messagesSent ms"
                query = query + " LEFT JOIN whatsapp_api.clients cli"
                query = query + " ON cli.id = ms.id_client "
                query = query + " WHERE"
                query = query + " hash_message = %s"
                db.query(query, (hashReceived, ))
                messageDB = db.fetchall()

                if messageDB:
                    elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,"//*[@id='side']/div[1]/div/label/input"))
                    )

                    elem.clear()
                    elem.send_keys(messageDB[0][0])

                    time.sleep(4)

                    elem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,"//*[@id='pane-side']/div/div/div/div[1]"))
                        )

                    elem.click()

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
                        EC.presence_of_all_elements_located((By.XPATH,"//*[contains(@class, 'message-out')]/div/div/*[contains(@class, '_3zb-j')]"))
                    )

                    messagesFind = []

                    statusTxt = "Não enviada"
                    for message in messages:
                        if (message.text == messageDB[0][1]):
                            weekday_name = ["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO", "DOMINGO"]

                            if (messageDB[0][2].date() == datetime.now().date()):
                                textDate = "HOJE"
                            elif (messageDB[0][2].date() == (datetime.now() - timedelta(days=1)).date()):
                                textDate = "ONTEM"
                            elif ((messageDB[0][2].date() == (datetime.now() - timedelta(days=2)).date()) or (messageDB[0][2].date() == (datetime.now() - timedelta(days=3)).date()) or (messageDB[0][2].date() == (datetime.now() - timedelta(days=4)).date()) or (messageDB[0][2].date() == (datetime.now() - timedelta(days=5)).date())):
                                textDate = weekday_name[messageDB[0][2].date().weekday()]
                            else:
                                textDate = messageDB[0][2].strftime('%-d/%-m/%Y')

                            blocoData = message.find_element_by_xpath("../../../../../*[contains(@class, '_3rjxZ')]/div/span[text()='{}']".format(textDate))

                            contDivMessages = 1
                            statusTxt = "Não enviada"

                            while contDivMessages <= len(blocoData.find_elements_by_xpath("../../following-sibling::div")):
                                try:
                                    blocoMessage = blocoData.find_element_by_xpath("../../following-sibling::div[position() = {}]/div[contains(@class, 'message-out')]/div/div/*[contains(@class, '_3zb-j')]/span[text()='{}']".format(contDivMessages,message.text))

                                    blocoHour = blocoMessage.find_element_by_xpath("../../../*[contains(@class, '_2f-RV')]/*[contains(@class, '_1DZAH')]/*[contains(@class, '_3EFt_')]")

                                    if blocoHour.text == messageDB[0][2].strftime('%H:%M'):
                                        
                                        try:
                                            statusTxt = "Visualizada"
                                            blocoStatus = blocoMessage.find_element_by_xpath("../../../*[contains(@class, '_2f-RV')]/*[contains(@class, '_1DZAH')]/*[contains(@class, '_32uRw')]/span[contains(@data-icon,'msg-dblcheck-ack')]")
                                        except Exception as a:
                                            try:
                                                statusTxt = "Enviada"
                                                blocoStatus = blocoMessage.find_element_by_xpath("../../../*[contains(@class, '_2f-RV')]/*[contains(@class, '_1DZAH')]/*[contains(@class, '_32uRw')]/span[contains(@data-icon,'msg-dblcheck')]")
                                            except Exception as a:
                                                try:
                                                    statusTxt = "Não recebida"
                                                    blocoStatus = blocoMessage.find_element_by_xpath("../../../*[contains(@class, '_2f-RV')]/*[contains(@class, '_1DZAH')]/*[contains(@class, '_32uRw')]/span[contains(@data-icon,'msg-check')]")
                                                except Exception as a:
                                                    statusTxt = "Não enviada"

                                        break
                                        
                                    contDivMessages = contDivMessages + 1

                                except Exception as e:
                                    #print (e)
                                    contDivMessages = contDivMessages + 1

                            break

                    formatted_date = messageDB[0][2].strftime('%Y-%m-%d %H:%M:%S')
                    return jsonify({"name_client": messageDB[0][0], "message": messageDB[0][1],"date_message": formatted_date, "status": statusTxt})

    except Exception as e:
        raise e

    return jsonify({"message":"Parâmetros incorretos"})

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

def sendMedia(driver):
    content = request.json

    try:
        if content:

    except Exception as e:
        print(e)

    return jsonify({"message": "Parâmetros incorretos"})

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