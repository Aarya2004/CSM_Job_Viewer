from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time

#Initializing
driver = webdriver.Chrome()
actions = ActionChains(driver)
wait = WebDriverWait(driver, 10)

def authenticate_through_Duo():
    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "auth-button")))
    actions.click(login_button)
    try:
        actions.perform()
    except StaleElementReferenceException:
        print("Element changed")

def authenticate_through_passcode(passcode: str):
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "passcode")))
    actions.click(login_button)
    try:
        actions.perform()
    except StaleElementReferenceException:
        print("Element changed")

    passcode_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'passcode-input')))
    actions.send_keys_to_element(passcode_input, passcode)
    actions.click(login_button)
    try:
        actions.perform()
    except StaleElementReferenceException:
        print("Element changed")

#Get CSM website with all jobs
driver.get("https://utsc-utoronto-csm.symplicity.com/students/app/jobs/search?perPage=20&page=1&sort=!postdate&currentJobId=54c3717762ffa70a96fe4183794d5748")

#CSM login
login_button = driver.find_element(By.CLASS_NAME, 'input-button')
actions.click(login_button)
actions.perform()

#UTor ID login
login_button = wait.until(EC.element_to_be_clickable((By.NAME, '_eventId_proceed')))
login_button = driver.find_element(By.NAME, '_eventId_proceed')
username_input = driver.find_element(By.ID, 'username')
actions.send_keys_to_element(username_input, '___________') #Enter your UTORid
password_input =  driver.find_element(By.ID, 'password')
actions.send_keys_to_element(password_input, '___________') #Enter your password
actions.click(login_button)
actions.perform()

#Wait for longer as site takes a while to display TPA authorization
wait = WebDriverWait(driver, 15)

#TPA authorization
driver.switch_to.frame(0)
url = driver.current_url
authenticate_through_Duo() #Currently checking through Duo push notification
time.sleep(60) #Gives user a minute to authenticate through the Duo Mobile Application
if(url == driver.current_url): #Checks if authentication succeeded
    print("Error with Duo Authentication")
    exit(1)