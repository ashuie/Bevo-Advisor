import time
import pandas as pd
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


home_url = "https://utdirect.utexas.edu/apps/registrar/course_schedule/20252/"

driver = webdriver.Chrome()
actions = ActionChains(driver)

def split_course_header(course_text):
    match = re.search(r'\d', course_text)
    if match:
        index = match.start() 
        course_number = course_text[:index].strip() 
        course_name = course_text[index:].strip()  
        return course_number, course_name
    else:
        return "", course_text.strip()
    
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight") 
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break 
        last_height = new_height

def parse_categories(driver):
    global df
    dropdown = Select(driver.find_element(By.XPATH, "//*[@id=\"fos_fl\"]"))
    options = dropdown.options
    for index, option in enumerate(options):
        for i in range(2):   
            time.sleep(2)
            dropdown = Select(driver.find_element(By.XPATH, "//*[@id=\"fos_fl\"]"))
            dropdown.select_by_index(index)

            if (i == 0):
                div_type = "Lower"
            else:    
                div_type = "Upper"
                division_select = driver.find_element(By.XPATH, "//*[@id=\"level.upper\"]")
                division_select.click()

            search_button = driver.find_element(By.XPATH, "//*[@id=\"search_area\"]/div[2]/div[2]/form/div[3]/div[2]/input")
            search_button.click()
            time.sleep(3)
            scroll_to_bottom(driver)
            
            all_tr_tags = driver.find_elements(By.XPATH, "//*[@id=\"inner_body\"]/table/tbody/tr")
            curr_class_name = ""
            curr_class_num = ""
            for tr in all_tr_tags:
                if tr.find_element(By.XPATH, "./td[1]").get_attribute("class") == "course_header":
                    curr_class_num, curr_class_name = split_course_header(tr.find_element(By.XPATH, "./td[1]").text) 
                else:
                    try: 
                        unique = tr.find_element(By.XPATH, "./td[@data-th='Unique']//a").text
                    except:
                        unique = ""
                    try:    
                        days = tr.find_element(By.XPATH, "./td[@data-th='Days']//span").text
                    except: 
                        days = ""
                    try:        
                        hours = tr.find_element(By.XPATH, "./td[@data-th='Hour']//span").text
                    except:
                        hours = ""
                    try:        
                        location = tr.find_element(By.XPATH, "./td[@data-th='Room']//span").text
                    except: 
                        location = ""
                    try:        
                        instructor = tr.find_element(By.XPATH, "./td[@data-th='Instructor']//span").text
                    except: 
                        instructor = ""
                    try:        
                        flags = " ".join([li.text for li in tr.find_elements(By.XPATH, "./td[@data-th='Flags']//div/ul/li")])
                    except:
                        flags =""
                    try:    
                        core = " ".join([li.text for li in tr.find_elements(By.XPATH, "./td[@data-th='Core']//div/ul/li")])
                    except:
                        core =""    
                    new = [curr_class_num, curr_class_name, unique, div_type, days, hours, location, instructor, flags, core, ""]
                    new = pd.DataFrame(columns=df.columns, data=[new])
                    df = pd.concat([df, new], axis = 0)
                    print(df)
            time.sleep(2)
            driver.get(home_url)



df = pd.DataFrame(columns=['Class Number', 'Class Name', 'Unique Number', 'Division', 'Days', 'Time', 'Location', 'Instructor', 'Flags', 'Core', 'Description'])

driver.get(home_url)
driver.maximize_window()
time.sleep(1)
print("Log in manually with username and password, then press enter.")
input()
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "searchOptions"))
)

parse_categories(driver)
time.sleep(3)

df.to_csv("./data/courses.csv", encoding = "utf-8-sig", index = False)
driver.quit()