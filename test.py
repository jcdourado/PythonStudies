import unittest
import whatsapi
import getpass
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Chrome

from flask import Flask, request, jsonify

app = Flask(__name__)


opts = ChromeOptions()
opts.add_argument('--disable-browser-side-navigation')
opts.add_experimental_option("detach", True)
opts.add_argument("user-data-dir=C:\\Users\\"+getpass.getuser()+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default")  # this is the directory for the cookies

#driver = WhatsAPIDriver(username="mkhase",client="Chrome")

driver = Chrome(chrome_options=opts)
driver.get("https://web.whatsapp.com/")

@app.route("/sendMessage/", methods=['GET', 'POST'])
def sendMessageRoute():
    return whatsapi.sendMessage(driver)


@app.route("/iteractOverMessages/", methods=['GET', 'POST'])
def iteractOverMessagesRoute():
    return whatsapi.iteractOverMessages(driver)

@app.route("/getStatusMessage/", methods=['GET','POST'])
def getStatusMessageRoute():
    return whatsapi.getStatusMessage(driver)

@app.route("/sendMedia/", methods=['GET','POST'])
def sendMediaRoute():
	return whatsapi.sendMedia(driver)

if __name__ == "__main__":
	app.run(debug=False)


