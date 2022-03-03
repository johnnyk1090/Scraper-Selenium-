'''
This is a web scraping project built via Selenium
The website used is the https://www.lambertshealthcare.co.uk/ (supplement products)
'''

from ast import Continue
from lib2to3.pgen2 import driver
import os

# bring in the Selenium librairies
from fileinput import filename
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

# useful librairies
import time
import pandas as pd

# user interface
import tkinter as tk
from tkinter import simpledialog    
ROOT = tk.Tk()
ROOT.withdraw()

# GUI
from pivottablejs import pivot_ui 

# format json
import json

# import url library
import urllib.request

class Scraper:
    # sample url = "https://www.lambertshealthcare.co.uk/"
    def __init__(self, url = simpledialog.askstring(title="URL input",
                                                    prompt="Please enter your url : ")):
        url = str(url) 
        self.driver = Chrome(ChromeDriverManager().install())       
        self.driver.get(url)
            
    # decorator for time waiting and clicking buttons
    def timing_button_decorator(a_function):
        def wrapper(self, msg, xpath):
            xpath = str(xpath)                    
            try:
                time.sleep(3)
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))                                                                     
                clicked = self.driver.find_element(By.XPATH, xpath).click()                
                return clicked
            except :
                print(TimeoutError, msg)                
                pass # in case there are not cookies or pop ups                        
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
    
    def container(self, xpath):
        # container posseses the method of all subcategories
        # just one level above of all subcategories            
        self.xpath = str(xpath)
        container = self.subcategories(self.xpath)

        # find all the children of te container (one level below)
        list_subcategories = container.find_elements(By.XPATH, './div')        
        return list_subcategories       

    def the_list_of_links(self, qnt_price_xpath, usage_xpath, name_of_product_xpath, complete_label_xpath):  # the basic method ---> it returns the elements           
        self.label = complete_label_xpath        
        self.list_of_links = []        
        list_subcategories = self.container(self.xpath)
        for i in list_subcategories:
            self.list_of_links.append(i.find_element(By.TAG_NAME, 'a').get_attribute('href'))
            
        # a dictionairy with all the values of subcategories
        subcategories_dict = dict(link = [], quantity_and_price = [], usage = [], name_of_product = [])
        
        # go to each one of the above links
        # and fill in the dictionairy with the information   
        for link in self.list_of_links[:2]:            
            
            # chrome will get step by step the links of the products
            bot.driver.get(link)
            
            time.sleep(2) # delay the searching (the bot is doing the job)  
            
            # refresh the name of product with iteration
            self.name_of_product = name_of_product_xpath          
            
            # it will append the elements to the subcategories dictionairy
            subcategories_dict['link'].append(link)            
            
            try:
                quantity_and_price = bot.driver.find_element(By.XPATH, qnt_price_xpath) 
                subcategories_dict['quantity_and_price'].append(quantity_and_price.text.split('£'))
            except NoSuchElementException:    
                subcategories_dict['quantity_and_price'].append('quantity or price not found')                        
            try:    
                usage = bot.driver.find_element(By.XPATH, usage_xpath)                                                                    
                subcategories_dict['usage'].append(usage.text)
            except NoSuchElementException:    
                subcategories_dict['usage'].append('usage not found')
            try:    
                name_of_product = bot.driver.find_element(By.XPATH, name_of_product_xpath)                                                                    
                subcategories_dict['name_of_product'].append(name_of_product.text)
            except NoSuchElementException:    
                subcategories_dict['name_of_product'].append('no name of product found')
                                  
        # reuse the dictionairy                    
        self.subcategories_dict = subcategories_dict                            
        # present the info to a table format via DataFrame 
        self.df = pd.DataFrame(subcategories_dict)
                 
        return self.df.to_json # in case you need it to json format
    
    # images links
    def image_source(self) :        
        time.sleep(2)                                
        for link in self.list_of_links[:2]:            
            
            # chrome will get step by step the links of the products
            self.driver.get(link)        
        
            self.src_label = self.driver.find_element_by_xpath(self.label).get_attribute('src') 
            self.data_dump()
            
            self.source = self.src_label        
            self.images_label_download()        
    
    # create new folder 
    def create_store(self, path, label_folder):        
        self.label_folder = label_folder # reusable 
        self.path = path # reusable
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)               

    # dump the data into the folder 
    def data_dump(self):                                     
        with open(f"{self.path}/{self.label_folder}/link_and_product_data.json", "w") as f:            
            json.dump(self.subcategories_dict, f)                                              
                                        
    # download images & labels of products
    def images_label_download(self):
        # iterate and bring all the images
        urllib.request.urlretrieve(self.source, f"{self.path}/{self.label_folder}/{self.driver.find_element_by_xpath(self.name_of_product).text}.jpg")
        
    # a beautiful demonstration via pivot table js for further analysis
    def my_gui(self):
        file = pivot_ui(self.df)                    
        os.path.join(f"{self.label_folder}, {file}.html")
                                                                                                                                                                                             
    # method to close the pop-us 
    @timing_button_decorator
    def pop_up(self, msg, xpath) :
        return msg, xpath
                           
    # method to accept the cookies of the website
    @timing_button_decorator
    def accept_cookies(self, msg, xpath) :        
        return msg, xpath    
    
# bot = class Scraper
# driver is Chrome
bot = Scraper()                                 

# CONTROL PANEL --- > DO ANY SCRAPPING YOU WANT FROM ANY SUPPLEMENT SITE
def initiate():
             
    # cookies accept                           
    bot.accept_cookies(msg = "No cookies here!!", xpath = '//button[@id="onetrust-accept-btn-handler"]')    
    
    # text then hit_enter to search bar 
    bot.text_hit_enter(msg = "No search bar found !!!"  , xpath = '//input[@id="searchINPUT"]', 
                       text = simpledialog.askstring(title="Search bar",
                       prompt="What do you want to search for : "))        
    
    # close possible pop-up 
    bot.pop_up(msg = 'No pop up found', xpath = '//div[@class="popup-close"]')            
                    
    # call the container with the list of subcategories
    bot.container(xpath = '//div[@class="container-cols page-wrapper relative-children "]')
    
    # call the elements (quantity and price, usage, name, label)
    bot.the_list_of_links(qnt_price_xpath = '//div[@class="nogaps pt0-25 pb0-5 bd-color4 bd-bottomonly block"]', 
                          usage_xpath = '//div[@class="f-18 f-xspace f-color11 f-nobold"]',                           
                          name_of_product_xpath = '//h1[@class="mt0-5 mb0 f-30 f-color6 f-bold"]',
                          complete_label_xpath = '//img[@id="mainImage"]')
        
    # call the function to create folder for the images
    # enter the path you want this to be sent 
    bot.create_store(path = simpledialog.askstring(title="Path",
                    prompt="Type the path you want to create the folder : "),
                    label_folder = simpledialog.askstring(title="Folder Name",
                    prompt="Name the folder of your scrapping : "))                    
    
    # get the link of images 
    bot.image_source()
    
    bot.my_gui()
                
# run it only if it is NOT imported
if __name__ == "__main__":                
    initiate()
    Chrome(ChromeDriverManager().install()).back()
