import TessResult as TR
import re
import calendar as cald
import TesseractHandler as TH


class TesseractOCR(object):
    '''Class to perfect a TesseractOCR operation on an image with rotation angle theta
    returns a corresponding TessResult'''

    def __init__(self, imgFile: str, theta):
        self.theta = theta
        self.image = imgFile

    def parse(self)->TR.TessResult:  
        '''called by reader to ocr convert image to text, filtering for basics info
        returns TessResult object'''

        # key = (b,p,l)  Value =(word:list, conf:list)
        bpl_dict = self.ocr()
        # capture basic info
        transaction_basics_dict = self.match_basic_data(bpl_dict)
        res= TR.TessResult(self.theta, self.image, bpl_dict, transaction_basics_dict) 
        return res

#region basics_data
    def match_basic_data(self,bpl_dict): 
        '''
        @param: bpl_dict: key = (b,p,l). Value =(word:list, conf:list)
        @return: dict: key=date/loc/amount, val=List<string>
        '''

        class date_line:
            def __init__(self, line:list, date:str):
                self.line = line
                self.pur_date = date

        class location_line: #only includes the shop name for name 
            def __init__(self, line, shop):
                self.shop = shop
                self.line = line 

        class total_pay_line: 
            def __init__(self, line, amount:str):
                self.line = line
                self.amount = amount #may contain $ or - symbol...

        date_lines = []
        location_lines = []
        total_pay_lines =[]
        for k,v in bpl_dict.items():
            line = " ".join(v[0]) #join by space even if original text no space

            d =  self._filter_date(line)
            loc = self._filter_shopLocation(line)
            payment = self._filter_price(line)

            if d:
                date_lines.append(date_line(line,d))
            if loc:
                location_lines.append(location_line(line,loc))
            if payment:
                total_pay_lines.append(total_pay_line(line,payment))


        #logic to reject false +ves in  line lists 
        dates = []
        if len(date_lines)>0:
            dates = [l.pur_date for l in date_lines if ~self._reject_line(l.line) ]

        #dict: key, val=List<string>
        basics= {
            'date': dates,
            'loc': [l.shop for l in location_lines],
            'amount':[l.amount for l in total_pay_lines]
        }
        return basics


    def _filter_date(self, line):
        '''returns the date matching string if exists in line else None'''

        # pattern="[0-9][0-9]?[\/\-][0-9]{1,2}[\/\-][0-9]{2,4} \s* ([0-9]{1,2}:[0-9]{2}(:[0-9]{2})?(\s+[AP]M)?)?", #note: 12/34/777 false +ve
        
        patterns = []
        c1 = '|'.join(cald.month_name[1:]) #set of month names 
        c2 = '|'.join(cald.month_abbr[1:])
        day_yearRegex = "[0-9]{1,2}\s?,?\s+[0-9]{4}" #23, 1997
        timeRegx="([0-9]{1,2}:[0-9]{2}(:[0-9]{2})?(\s+[AP]M)?)?"
        dateRegx = "[0-9][0-9]?[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}"
        patterns.append(f'{dateRegx}\s*{timeRegx}') #eg. 07-3-2020
        patterns.append(f'({c1})\s+{day_yearRegex}\s*{timeRegx}') #eg May 13, 2020 10:34 AM
        patterns.append(f'({c2})\s+{day_yearRegex}\s*{timeRegx}')

        line = line.strip()
        for pattern in patterns:
            res = re.search(pattern, line, flags=re.IGNORECASE)
            if res:
                return res.group(0)
        return None

    def _filter_price(self,line):
        prompts = [
            "total", "credit\s+(cards?)?", "balance", "visa", "amex"
        ]
        price_regex = "\-?\$?[0-9]{1,}\.[0-9]{2}"
        
        for prm in prompts:
            pattern = f'{prm}\s+{price_regex}' 
            res=re.search(pattern, line, re.IGNORECASE)
            if res:
                res2= re.search(price_regex, res.group(0))
                if res2:
                    return res2.group(0)
        return None 

    def _filter_shopLocation(self,line):
        #future: use location api
        shops = [
            "walgreens", "cvs",
            "safeway", "99 ranch market", "nob hill",
            "target", "walmart"
        ]
        addresess = "" #TODO
        
        for shop in shops:
            if shop.lower() in line.lower():
                return shop
        return None
    
    def _reject_line(self, line:str):
        '''True if it line contains a non-transaction date'''

        irrelevant_tags = "(expir(e|ing|es)|points?|rewards?)"
        res = re.search(f'{irrelevant_tags}', line, flags=re.IGNORECASE)
        if res:
            return True
        return False
    
#endregion basics_data


    def ocr(self):
        th = TH.TesseractHandler(self.image)
        ocr_dict = th.ocr(self.theta)
        return ocr_dict

