from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

#Initializing
driver = webdriver.Chrome()
actions = ActionChains(driver)
wait = WebDriverWait(driver, 10)

#Get CSM website
driver.get("https://utsc-utoronto-csm.symplicity.com/students/?uri=%2Fstudents%2Fapp%2Fjobs%2Fsearch&signin_tab=0")

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