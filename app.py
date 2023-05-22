from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
from bs4 import BeautifulSoup
from thefuzz import fuzz
import re

#Initializing
driver = webdriver.Chrome()
actions = ActionChains(driver)
wait = WebDriverWait(driver, 10)
user_inputs_list = []
user_option = 'Y'

def authenticate_through_Duo(): #Option 1 - User authenticates through Duo Mobile push notification
    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "auth-button")))
    actions.click(login_button)
    try:
        actions.perform()
    except StaleElementReferenceException:
        print("Element changed")

def authenticate_through_passcode(passcode: str): #Option 2 - User inputs passcode as a string from Duo Mobile and authenticates directly
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

def find_max_similarity(job_titles_to_similarity): #Find the job title with maximum similarity to all the job titles entered by the user
    max_key = list(job_titles_to_similarity.keys())[0]
    for job_title in job_titles_to_similarity:
        if job_titles_to_similarity[job_title] > job_titles_to_similarity[max_key]:
            max_key = job_title
    return max_key

#Take user inputs to understand what roles the user is looking for
while user_option == 'Y':
    user_query = input("Enter a position you're looking for:\n")
    user_inputs_list.append(user_query)
    user_option = input("Continue? (Y/N)\n").upper()

#Check if user_inputs_list is empty
if user_inputs_list == []:
    print("No input from user: Terminating program")
    exit(2)

#Find number of job postings to save from user
num_to_save = int(input("How many job titles to save?"))

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

#Wait for longer as site takes a while to display TPA authorization and ask whether Duo authentication is needed
wait = WebDriverWait(driver, 15)
duo_input = input("Is Duo Authorization needed?")

#TPA authorization
if(duo_input == 'y'):
    driver.switch_to.frame(0)
    url = driver.current_url
    authenticate_through_Duo() #Currently checking through Duo push notification
    time.sleep(60) #Gives user a minute to authenticate through the Duo Mobile Application
    if(url == driver.current_url): #Checks if authentication succeeded
        print("Error with Duo Authentication")
        exit(1)

#Wait for page to load in case Duo authentcation is not needed
time.sleep(7)

#Accesses Job titles from first page
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
job_postings = soup.find_all(role="listitem") #Find every job posting on the webpage
job_titles = []
for job_posting in job_postings: #Add job titles to job_titles list
    job_title = str(list(job_posting.descendants)[9].string)
    job_titles.append(job_title)

#Sanitize job titles and add to dictionary
job_titles_to_similarity = {}
sanitized_job_titles_to_job_titles = {}
for job_title in job_titles:
    sanitized_job_title = re.sub('[^A-Za-z\s]', '', job_title) #Santizing job title using regex
    job_titles_to_similarity[sanitized_job_title] = 0
    sanitized_job_titles_to_job_titles[sanitized_job_title] = job_title

# Evaluate similarity
for user_input in user_inputs_list:
    for job_title in job_titles_to_similarity:
        job_titles_to_similarity[job_title] = job_titles_to_similarity[job_title] + fuzz.ratio(user_input, job_title)

#Save job postings on CSM
for _ in range(num_to_save):
    job_title = find_max_similarity(job_titles_to_similarity)
    save_job = driver.find_element(By.PARTIAL_LINK_TEXT, sanitized_job_titles_to_job_titles[job_title])
    print(sanitized_job_titles_to_job_titles[job_title]) #Prints saved jobs to terminal
    driver.execute_script("arguments[0].click()", save_job)
    job_titles_to_similarity[job_title] = -1 #Saved jobs should not be considered after one pass
