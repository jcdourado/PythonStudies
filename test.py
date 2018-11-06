import unittest
import whatsapi
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Chrome

from flask import Flask, request, jsonify

app = Flask(__name__)


opts = ChromeOptions()
opts.add_argument('--disable-browser-side-navigation')
opts.add_experimental_option("detach", True)

#driver = WhatsAPIDriver(username="mkhase",client="Chrome")

driver = Chrome(chrome_options=opts)
driver.get("https://web.whatsapp.com/")

@app.route("/sendMessage/", methods=['GET', 'POST'])
def sendMessageRoute():
    return whatsapi.sendMessage(driver)


@app.route("/iteractOverMessages/", methods=['GET', 'POST'])
def iteractOverMessagesRoute():
    return whatsapi.iteractOverMessages(driver)

if __name__ == "__main__":
	app.run(debug=True)


