"""
class representing a parsed Receipt from an image Receipt
contains method for getting, setting information about the 
underlying Transaction
Handles data interface btw Tesseract Result and external API
"""

import dateutil.parser as DUP
import datetime as DT 
from re import sub

# US_DATE_FORMATS = (
#     '%b %d, %Y', 
#     '%B %d, %Y', #cvs
#     '%B %d %Y',
#     '%m/%d/%Y',
#     '%m/%d/%y',
#     '%m-%d-%y',
#     '%m-%d-%Y',
# ) 

class Receipt(object):
    def __init__(self, imageFile:str):
        self.image = imageFile
        self.date = ""
        self.location = ""
        self.payment = ""
        self.num_items_bought = 0
        self.items_set = {} #key = name, val = tesseract string

    def set_date(self,date):
        self.date = date.strip()

    def set_location(self,loc):
        self.location = loc.strip()
    
    def set_payment(self, pay):
        self.payment = pay.strip()

    def get_transactionDate(self)->str:
        '''formats date string to dd/mm/yyyy'''
        if len(self.date)==0:
            return ""
        tdate = DUP.parse(self.date)
        return DT.datetime.strftime(tdate, '%d/%m/%Y')
        
    def get_totalAmount(self)->float:
        pay = float(sub(r'[^\d.]', '', self.payment))
        return pay 

    def get_location(self)->str:
        return self.location