import glob, os, csv, json, time
from pymongo import MongoClient
from urllib.parse import urljoin  # for Python2: from urlparse import urljoin
from urllib.request import urlretrieve
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

url = "https://covid.saude.gov.br/"

fileName = datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")[:-3]+".csv"

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : "C:\\Users\\User\\jobs\\pandemia\\csv\\"}
chromeOptions.add_experimental_option("prefs",prefs)
chromedriver = "C:\\chromedriver_win32\\chromedriver.exe"
browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

# browser = webdriver.Chrome(chromedriver) #browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)
browser.get(url)

# wait for page to load
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ok')))
print("Page loaded")
button = browser.find_element_by_xpath('//div[@role="button"]')
browser.implicitly_wait(10)
ActionChains(browser).move_to_element(button).click(button).perform()

#PERMANENCIA MONGODB
client = MongoClient("mongodb://localhost:27017")
db = client['covid19']
dados = db['dados']

data = {}

while (True):    
    try:
        for fname in glob.glob("C:\\Users\\User\\jobs\\pandemia\\csv\\*.csv"):
            with open(fname, encoding="iso-8859-1") as csvfile:
                dados.drop()
                csvreader = csv.DictReader(csvfile, delimiter=';')
                for row in csvreader:
                    UF = row['sigla']
                    dados.find_and_modify(query={'UF':UF}, update={"$push": {'date':row['date'],'casosNovos':row['casosNovos'],'obitosNovos':row['obitosNovos']}}, upsert=True, full_response= True)
            os.remove(fname)
        break
    except IOError:
        time.sleep(10)

browser.close()