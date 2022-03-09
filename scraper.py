'''
This is a web scraping project built via Selenium
The website used is the https://www.lambertshealthcare.co.uk/ (supplement products)
'''

# essential librairies
import os
import uuid
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
from tqdm import tqdm

# library that allows us to work with aws from our script
import boto3
from boto.s3.connection import S3Connection
from boto.s3.key import Key

# bring in the Selenium librairies
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
    
    '''
    This class is used to represent a SCRAPER.

    Attributes:
        to be finalized....
    '''
        
    # sample url = "https://www.lambertshealthcare.co.uk/"
    def __init__(self, url = simpledialog.askstring(title="URL input",
                 prompt="Please enter your url : ")):
        
        """
        Get the HTML of a URL
        
        Parameters
        ----------
        url : str
            The URL to get the HTML of        
        """                        
        url = str(url)
        self.driver = Chrome(ChromeDriverManager().install())       
        
        
        self.driver.get(url)
        self.driver.maximize_window()
            
    # decorator for time waiting and clicking buttons
    def timing_button_decorator(a_function):
        def wrapper(self, msg, xpath):
            """
            wrapper:
            Get any function that handles the messages and xpaths of elements such as cookies and pop ups 
            
            Parameters
            ----------
            msg : str
            xpath : XML path used for navigation through the HTML structure of the page                
            
            Returns
            -------
            clicks the window of rather cookies (accept cookies) or pop-ups (x button to close them)
                
            """                    
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
    
    def search_bar(self, msg, xpath):
            """
            Get the function that handles the search bar of website 
            
            Parameters
            ----------
            msg : str
            xpath : XML path used for navigation through the HTML structure of the page                
            
            Returns
            -------
            a.clicks on the search bar 
            b.if no search bar found --> None
                
            """                            
            xpath = str(xpath)                    
            try:
                time.sleep(3)
                element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))                                                                     
                element.click()
                return element
            except TimeoutException:
                print(msg)
                return None                                
       
    def text_hit_enter(self, msg, xpath, text):        
            """
            text and then hit enter method 
            
            Parameters
            ----------
            msg : str
            xpath : XML path used for navigation through the HTML structure of the page                
            text : input user string
            """
            element = self.search_bar(msg, xpath)            
            element.send_keys(text)
            element.send_keys(Keys.ENTER)
        
    # method to find multiple subcategories within the category (text)                                   
    def subcategories(self, xpath):        
        return self.driver.find_element(By.XPATH, xpath)
    
    def container(self, xpath):
        # contains the parent of all product subcategories
        # just one level above of all subcategories            
        # for example vitamin c is the parent 
        self.xpath = str(xpath)
        container = self.subcategories(self.xpath)

        # find all the children of the container (one level below)
        list_subcategories = container.find_elements(By.XPATH, './div')                
        return list_subcategories       

    def the_list_of_links(self, qnt_price_xpath, usage_xpath, name_of_product_xpath, complete_label_xpath):             
        """
        the basic method ---> it returns the elements of products
        
        Parameters
        ----------
        qnt_price_xpath : product's quantity and price xpath
        usage_xpath :  product's usage xpath
        name_of_product_xpath : product's name xpath
        complete_label_xpath : product's label with xpath
                                       
        Returns
        -------
        dictionairy of product subcategories (all turmeric range products e.g)
        in DataFrame format.
             
        """        
        self.label = complete_label_xpath        
        self.list_of_links = []        
        list_subcategories = self.container(self.xpath)
        for i in list_subcategories:
            self.list_of_links.append(i.find_element(By.TAG_NAME, 'a').get_attribute('href'))
            
        # a dictionairy with all the values of subcategories
        subcategories_dict = dict(uuid1 = [], uuid4 = [], link = [], quantity_and_price = [], usage = [], name_of_product = [])
        
        # go to each one of the above links
        # and fill in the dictionairy with the information          
        for link in self.list_of_links:                        
            
            # chrome will get step by step the links of the products
            self.driver.get(link)
            
            time.sleep(1) # delay the searching (the bot is doing the job)  
            
            # refresh the name of product with iteration
            self.name_of_product = name_of_product_xpath          
            
            # it will append the elements to the subcategories dictionairy
            subcategories_dict['link'].append(link)            
            
            # it will append the unique id to the subcategories dictionairy
            uuid1 = str(uuid.uuid1())
            self.uuid1 = uuid1                    
            subcategories_dict['uuid1'].append(uuid1)
            
            
            uuid4 = str(uuid.uuid4())
            self.uuid4 = uuid4
            subcategories_dict['uuid4'].append(uuid4)
            
            try:
                quantity_and_price = self.driver.find_element(By.XPATH, qnt_price_xpath) 
                subcategories_dict['quantity_and_price'].append(quantity_and_price.text.split('£'))
            except NoSuchElementException:    
                subcategories_dict['quantity_and_price'].append('quantity or price not found')                        
            try:    
                usage = self.driver.find_element(By.XPATH, usage_xpath)                                                                    
                subcategories_dict['usage'].append(usage.text)
            except NoSuchElementException:    
                subcategories_dict['usage'].append('usage not found')
            try:    
                name_of_product = self.driver.find_element(By.XPATH, name_of_product_xpath)                                                                    
                subcategories_dict['name_of_product'].append(name_of_product.text)
            except NoSuchElementException:    
                subcategories_dict['name_of_product'].append('no name of product found')
            
            # call the image methods inside the iteration              
            time.sleep(1)                
            self.image_source()
            time.sleep(1)
            self.images_label_download()
                                  
        # reuse the dictionairy                    
        self.subcategories_dict = subcategories_dict                            
        # present the info to a table format via DataFrame 
        self.df = pd.DataFrame(subcategories_dict)
        return self.df                 
    
    # images links
    def image_source(self) :                                                                                
        self.src_label = self.driver.find_element_by_xpath(self.label).get_attribute('src')                                 
    
    # create new folder 
    def create_store(self, path, label_folder):        
        self.label_folder = label_folder # reusable 
        self.path = path # reusable
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)               

    # dump the data into the folder 
    def data_dump(self):
        time.sleep(1)                                     
        with open(f"{self.path}/{self.label_folder}/link_and_product_data.json", "w") as f:            
            json.dump(self.subcategories_dict, f)                                                          
                                        
    # download images & labels of products
    def images_label_download(self) -> None:        
        # iterate and bring all the images
        urllib.request.urlretrieve(self.src_label, f"{self.path}/{self.label_folder}/{self.uuid1}_{self.uuid4}_{self.driver.find_element_by_xpath(self.name_of_product).text}.jpg")                
        
    # a beautiful demonstration via pivot table js for further analysis
    def my_gui(self) :                        
        return pivot_ui(self.df)                 
                
    def bucket_interraction(self) -> None:        
        conn = S3Connection()
                        
        bucket = conn.get_bucket('scraper-aicore')

        # upload the folder created to the bucket
        for root, dirs, files in os.walk(f"{self.label_folder}"):
            for name in files:
                path = root.split(os.path.sep)[1:]
                path.append(name)
                key_id = os.path.join(*path)
                k = Key(bucket)
                k.key = key_id
                k.set_contents_from_filename(os.path.join(root, name))
                
    def tabular_data(self, database_type, dbapi, endpoint, user, password, port, database) -> None:        
        # upload the dictionary with product to amazon RDS
        engine = create_engine(f"{database_type}+{dbapi}://{user}:{password}@{endpoint}:{port}/{database}")
        self.df.to_sql(f'{self.label_folder}', engine, if_exists='replace')        
        
        # access the sql table
        df = pd.read_sql_table(f'{self.label_folder}', engine)
        print(df.head())
                                                                                                                                                                                                 
    # method to close the pop-us 
    @timing_button_decorator
    def pop_up(self, msg, xpath) :
        return msg, xpath
                           
    # method to accept the cookies of the website
    @timing_button_decorator
    def accept_cookies(self, msg, xpath) :        
        return msg, xpath        

# CONTROL PANEL --- > DO ANY SCRAPING YOU WANT FROM ANY SUPPLEMENT SITE
def initiate():
    
    # bot = class Scraper
    # driver is Chrome
    bot = Scraper()                                 
             
    # cookies accept  (it can be used for pop-ups too)                         
    bot.accept_cookies(msg = "No cookies here!!", xpath = '//button[@id="onetrust-accept-btn-handler"]')    
    
    # text then hit_enter to search bar 
    bot.text_hit_enter(msg = "No search bar found !!!"  , xpath = '//input[@id="searchINPUT"]', 
                       text = simpledialog.askstring(title="Search bar",
                       prompt="What do you want to search for : "))        
    
    # close possible pop-up 
    bot.pop_up(msg = 'No pop up found', xpath = '//div[@class="popup-close"]')            
                    
    # call the container with the list of subcategories
    bot.container(xpath = '//div[@class="container-cols page-wrapper relative-children "]')
    
    # call the function to create folder for the images
    # enter the path you want this to be sent 
    bot.create_store(path = simpledialog.askstring(title="Path",
                    prompt="Type the path you want to create the folder : "),
                    label_folder = simpledialog.askstring(title="Folder Name",
                    prompt="Name the folder of your scraping : "))                        
    
    # call the elements (quantity and price, usage, name, label)
    bot.the_list_of_links(qnt_price_xpath = '//div[@class="nogaps pt0-25 pb0-5 bd-color4 bd-bottomonly block"]', 
                          usage_xpath = '//div[@class="f-18 f-xspace f-color11 f-nobold"]',                           
                          name_of_product_xpath = '//h1[@class="mt0-5 mb0 f-30 f-color6 f-bold"]',
                          complete_label_xpath = '//img[@id="mainImage"]')        
    
    # dump the data in json format in the folder 
    bot.data_dump()
    
    # call the pivot table js method
    bot.my_gui()    
    
    # start interracting with bucket 
    # upload the whole folder 
    bot.bucket_interraction()
    
    # RDS TIME!
    bot.tabular_data(database_type = 'postgresql',
                     dbapi = 'psycopg2',
                     endpoint = 'aicoredb.ctuapz5fv9z4.eu-central-1.rds.amazonaws.com', 
                     user = 'postgres',
                     password = 'Twinperama10',
                     port = 5432,
                     database = 'postgres')
    
def keep_playing():    
    for i in tqdm(range(50)):
        initiate()
                
# run it only if it is NOT imported
if __name__ == "__main__":                    
    initiate()
    keep_playing()
