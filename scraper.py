'''
This is a web scraping project built via Selenium

The website used is the https://www.lambertshealthcare.co.uk/ (supplement products)

'''

# bring in the Selenium librairies
from asyncio import subprocess
from os import kill
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

# useful librairies
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

# user UI
import tkinter as tk
from tkinter import simpledialog    
ROOT = tk.Tk()
ROOT.withdraw()

# Dataframe GUI
import tabloo    

class Scraper:
    def __init__(self, url: str = "https://www.lambertshealthcare.co.uk/"):
        
        self.driver = Chrome(ChromeDriverManager().install())
        self.driver.get(url)
            
    # decorator for time waiting and clicking buttons
    def timing_button_decorator(a_function):
        def wrapper(self, msg, xpath):
            xpath = str(xpath)                    
            try:
                time.sleep(3)
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))                                                                     
                self.driver.find_element(By.XPATH, xpath).click()
            except TimeoutException:
                print(msg)
                return None                        
        return wrapper               
    
    # method to click on search bar
    def search_bar(self, msg, xpath):
            xpath = str(xpath)                    
            try:
                time.sleep(3)
                element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))                                                                     
                element.click()
                return element
            except TimeoutException:
                print(msg)
                return None                        

    # type a text on the search bar and then hit enter (after using the search_bar method)   
    def text_hit_enter(self, msg, xpath, text):
        element = self.search_bar(msg, xpath)            
        element.send_keys(text)
        element.send_keys(Keys.ENTER)
        
    # method to find multiple subcategories within the category (text)                                   
    def subcategories(self, xpath):
        return self.driver.find_element(By.XPATH, xpath)
    
    def container(self):
    # container posseses the method of all subcategories
    # just one level above of all subcategories    
        container = self.subcategories(xpath = '//div[@class="container-cols page-wrapper relative-children "]')

    # find all the children of te container (one level below)
        list_subcategories = container.find_elements(By.XPATH, './div')        
        return list_subcategories       

    def the_list_of_links(self):  # the basic method ---> it returns the elements   
        list_of_links = []    
        list_subcategories = self.container()
        for i in list_subcategories:
            list_of_links.append(i.find_element(By.TAG_NAME, 'a').get_attribute('href'))
            
        # a dictionairy with all te values of subgategories
        subcategories_dict = dict(link = [], quantity_and_price = [], usage = [])
        
        # go to each one of the above links
        # and fill in te dictionairy with the information    
        for link in list_of_links[0:3]:
            
            bot.driver.get(link)
            time.sleep(2) #delay the searching (the bot is doing the job)
            subcategories_dict['link'].append(link)
            
            try:
                quantity_and_price = bot.driver.find_element(By.XPATH, '//div[@class="nogaps pt0-25 pb0-5 bd-color4 bd-bottomonly block"]') 
                subcategories_dict['quantity_and_price'].append(quantity_and_price.text.split('£'))
            except NoSuchElementException:    
                subcategories_dict['quantity_and_price'].append('quantity or price not found')                        
            try:    
                usage = bot.driver.find_element(By.XPATH, '//div[@class="f-18 f-xspace f-color11 f-nobold"]')                                                                    
                subcategories_dict['usage'].append(usage.text)
            except NoSuchElementException:    
                subcategories_dict['usage'].append('usage not found')  
                            
        # present the info to a table format via DataFrame 
        df = pd.DataFrame(subcategories_dict)
        return tabloo.show(df)
    
    # method for searching again 
    def search_again(self):
        while True:                    
            search_me_again = input("What do you want to search for : ")
                
            if search_me_again.lower() != "y" and search_me_again.lower() != "yes":           
                exit()
            else:
                initiate()                                    
    pass            
                    
    # method to close the pop-us 
    @timing_button_decorator
    def pop_up(self, msg, xpath):
        return msg, xpath     
                           
    # method to accept the cookies of the website
    @timing_button_decorator
    def accept_cookies(self, msg, xpath):        
        return msg, xpath
    
    
# external methods to initiate scraping
bot = Scraper()                                
def initiate():
             
    # cookies call                           
    bot.accept_cookies(msg = "No cookies here!!", xpath = '//button[@id="onetrust-accept-btn-handler"]')
    
    # text_hit_enter to search bar call
    bot.text_hit_enter(msg = "No search bar found !!!"  , xpath = '//input[@id="searchINPUT"]', text = simpledialog.askstring(title="Search bar",
                                                                                                        prompt="What do you want to search for : "))
    # close possible pop-up 
    bot.pop_up(msg = 'No pop up found', xpath = '//div[@class="popup-close"]')
        
    # call the container with the list of subcategories
    bot.container()
    
    # call the list_of_links method
    bot.the_list_of_links()    
    
def search_again():
    
    # call the list_of_lists method
    bot.search_again()            
    
# run it only if it is NOT imported
if __name__ == "__main__":                
    initiate()  
    kill                                                    