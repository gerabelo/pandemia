'''
    geraldo@selvadebits.com.br
    14/04/2020 mudanças anteriores se vizeram necessárias em razão da ausência de um padrão na nomenclatura adotada pelo ministérios. hj a UF mudou 'sigla' para 'estado'

    v2: 15/04/2020
        Gov mudou a plataforma para Ionic

'''
import glob, os, csv, json, time #, pdfkit
import util
from pymongo import MongoClient
from urllib.parse import urljoin  # for Python2: from urlparse import urljoin
from urllib.request import urlretrieve
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from io import BytesIO
from PIL import Image

url = "https://covid.saude.gov.br/"

# fileName = datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")[:-3]+".csv"

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : "C:\\Users\\User\\jobs\\pandemia\\csv\\"}
chromeOptions.add_experimental_option("prefs",prefs)
chromedriver = "C:\\chromedriver_win32\\chromedriver.exe"
browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

# browser = webdriver.Chrome(chromedriver) #browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)
browser.get(url)

# wait for page to load
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'button-solid')))
print(url, " loaded")
button = browser.find_element_by_xpath('//ion-icon[@role="img"]')
browser.implicitly_wait(10)
ActionChains(browser).move_to_element(button).click(button).perform()
time.sleep(10)
#PERMANENCIA MONGODB
client = MongoClient("mongodb://localhost:27017")
db = client['covid19']
dados = db['dados']

# data = {}

bkp = datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")[:8]

while (True):    
    try:
        for fname in glob.glob("C:\\Users\\User\\jobs\\pandemia\\csv\\*.csv"):
            with open(fname, encoding="iso-8859-1") as csvfile:
                try:
                    dados.rename(bkp)
                except:
                    try:
                        dados.drop()
                    except:
                        pass

                csvreader = csv.DictReader(csvfile, delimiter=';')
                for row in csvreader:
                    try:
                        UF = row['sigla']
                    except:
                        UF = row['estado']
                    try:
                        #recuperados = int(row['casosAcumulados']) - int(row['obitosNovos']) - int(row['casosNovos'])
                        dados.find_and_modify(query={'UF':UF}, update={"$push": {'data':row['data'],'casosNovos':row['casosNovos'],'obitosNovos':row['obitosNovos'],'casosAcumulados':row['casosAcumulados'],'obitosAcumulados':row['obitosAcumulados']}}, upsert=True, full_response= True)
                    except:
                        #recuperados = int(row['cases']) - int(row['deaths_inc']) - int(row['cases_inc'])
                        dados.find_and_modify(query={'UF':UF}, update={"$push": {'data':row['date'],'casosNovos':row['cases_inc'],'obitosNovos':row['deaths_inc'],'casosAcumulados':row['cases'],'obitosAcumulados':row['deaths']}}, upsert=True, full_response= True)                                                
            os.remove(fname)
        break
    except IOError:
        time.sleep(10)
util.fullpage_screenshot(browser, "C:\\Users\\User\\jobs\\pandemia\\pdf\\"+bkp+"_br.png")
browser.close()

# url = "http://www.saude.am.gov.br/painel/corona/"
url = "http://public.tableau.com/views/PainelCOVID-19Resumo/PainelCovid-19Resumo?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Fpublic.tableau.com%2F&:embed_code_version=3&:tabs=no&:toolbar=yes&:animate_transition=yes&:display_static_image=no&:display_spinner=no&:display_overlay=yes&:display_count=yes&:loadOrderID=0"
# url = "https://public.tableau.com/profile/astec.sass#!/vizhome/PainelCOVID-19Resumo/PainelCovid-19Resumo"

chrome_options = webdriver.ChromeOptions()
settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')
CHROMEDRIVER_PATH = "C:\\chromedriver_win32\\chromedriver.exe"
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=CHROMEDRIVER_PATH)
driver.get(url)
time.sleep(300)
# driver.execute_script('window.print();')

# i = 3
# while i > 0:
#     driver.find_element_by_tag_name("html").send_keys(Keys.CONTROL,Keys.SUBTRACT)
#     i -= 1
driver.execute_script("document.body.style.zoom='100%'")

# driver.set_window_size(1024*3,927*3)
# img = Image.open(BytesIO(driver.find_element_by_tag_name('body').screenshot_as_png))

util.fullpage_screenshot(driver, "C:\\Users\\User\\jobs\\pandemia\\pdf\\"+bkp+"_am.png")
# if img.mode == 'RGBA':
#     img = img.convert('RGB')

# rgb = Image.new('RGB', img.size, (255, 255, 255))  # white background
# rgb.paste(img, mask=img.split()[3])
# rgb.save("C:\\Users\\User\\jobs\\pandemia\\pdf\\"+bkp+".pdf", "PDF", resolution=300, quality=100)
driver.quit()