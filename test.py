import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from flask import Flask, request, jsonify

app = Flask(__name__)


opts = ChromeOptions()
opts.add_experimental_option("detach", True)

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = Chrome(chrome_options=opts)

    def tearDown(self):
        #self.driver.close()
        pass

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("https://web.whatsapp.com/")
        elem = WebDriverWait(driver, 10).until(
        		EC.presence_of_element_located((By.XPATH,"//*[@id='side']/div[1]/div/label/input"))
        	)

        content = request.json
        elem.send_keys(content["Numero"])

        try:
        	elem = WebDriverWait(driver, 10).until(
	        		EC.presence_of_element_located((By.XPATH,"//*[@id='pane-side']/div/div/div/div[1]"))
	        	)

	        elem.click()

	        driver.implicitly_wait(2) 
	        elem = WebDriverWait(driver, 10).until(
	        		EC.presence_of_element_located((By.XPATH,"//*[@id='main']/footer/div[1]/div[2]/div/div[2]"))
	        	)

	        elem.clear()
	        elem.send_keys(content["Mensagem"])
	        elem.send_keys(Keys.RETURN)

        except Exception as e:
        	raise e


@app.route("/", methods=['GET', 'POST'])
def receive_params():
    unittest.main()
    #content = request.json
    #print(content)
    return jsonify({"message":"Mensagem Enviada com Sucesso!"})

if __name__ == "__main__":
	app.run(debug=True)
