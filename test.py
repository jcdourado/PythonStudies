import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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
        #self.assertIn("Replikante", driver.title)
        driver.implicitly_wait(10)
        #elem = WebDriverWait(driver, 10).until(
        #		EC.presence_of_element_located((By.CLASS_NAME,"jN-F5 copyable-text selectable-text"))
        #	)
        elem = driver.find_element_by_css_selector(".jN-F5.copyable-text.selectable-text")
        elem.send_keys("Amor")
        #assert "No results found." not in driver.page_source

if __name__ == "__main__":
    unittest.main()