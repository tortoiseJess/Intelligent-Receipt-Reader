import TessResult as TR
import TesseractOCR as TOCR
import re
import Receipt as R
from collections import Counter

class IntelligentReader(object):
    '''parsing for receipts, designed for immediate human verification interface'''

    def __init__(self, imageFile):
        self.img = imageFile
        self.date_strings = Counter() #verified dates with certain format from regex 
        self.location_strings = Counter()
        self.payment_strings = Counter()
        self.item_text = ""
        self.confidence = -1
        self.tessResult = None 

    def read(self, rotate_resolution=0):
        """main"""
        self.ternary_search_rotation(
                    start=-abs(rotate_resolution),\
                    end = abs(rotate_resolution))
        receipt = self.produce_receipt() #TODO2
        report = self.analyze_errors() #TODO2
        return receipt, report

    def ternary_search_rotation(self,start=-5, end=5, eps=1):

        tessRes_sofar, score_sofar = self._trio_search(start, end)

        #if results missed a basic data or low confidence, conduct ternary search
        l = None
        t1 = None
        s1 = -1
        if (
            len(self.date_strings)==0 or\
            len(self.payment_strings)==0 or\
            len(self.location_strings)==0 \
            #or score_sofar <=0.5
        ):
            l = start
            r = end
            while(abs(r-l)>eps):
                m1 = l+(r-l)/3
                m2 = r-(r-l)/3
                t1 =TOCR.TesseractOCR(self.img, theta=0+m1).parse() #TOTest
                t2= TOCR.TesseractOCR(self.img, theta=0+m2).parse()
                self.collect_basic_data(t1)
                self.collect_basic_data(t2)
                s1 = t1.calculate_total_accuracy()
                s2 = t2.calculate_total_accuracy() 
                if s2>s1:
                    l = m1
                else:
                    r=m2

        #compare the final value of l with original start , ends 
        if s1>score_sofar:
            self.tessResult= t1
            self.confidence = s1
        else:
            self.confidence = score_sofar
            self.tessResult = tessRes_sofar

    def _trio_search(self,start=-2, end=2):

        #compare the final value of l with original start , ends 
        candidates = set([start, end, 0])
        best_tessRessult = None
        best_score = -1
        for incr in candidates:
            t= TOCR.TesseractOCR(self.img, theta=0+incr).parse() 
            self.collect_basic_data(t)
            t.calculate_total_accuracy()

            if t.accuracy > best_score:
                best_score = t.accuracy
                best_tessRessult = t

        return best_tessRessult, best_score

############### Receipt: TessResults aggregater ############################################

    def produce_receipt(self):
        date = self._evaluate_dates()
        payment = self._evaluate_payments()
        loc = self._evaluate_locs()
        print("date {}, pay {}, loc {}".format(date,payment,loc))

        #todo3: self.item_text parsing from the self.tessResult
        receipt = R.Receipt(self.img) 
        receipt.set_date(date)
        receipt.set_location(loc)
        receipt.set_payment(payment)
        return receipt
    
    def collect_basic_data(self, tessResult):
        '''aggregate all the basic data parsed in different rotations'''
        bd = tessResult.get_receipt_basic_data()
        self.date_strings.update(bd['date'])
        self.location_strings.update(bd['loc'])
        self.payment_strings.update(bd['amount'])

    def _evaluate_dates(self):
        """determine which date string most accurate"""
        if len(self.date_strings)==0: 
            return ""

        # high confidence: filter for date with a time attached, expected only 1 unique time
        high_confidence = self._extract_high_conf_dates(set(self.date_strings))
        if high_confidence: 
            return high_confidence

        #else pick majority vote using absolute
        majority_vote = self.date_strings.most_common(1)[0][0]
        return majority_vote

    def _evaluate_locs(self):
        if len(self.location_strings)==0: 
            return ""

        majority_vote = self.location_strings.most_common(1)[0][0]
        return majority_vote

    def _evaluate_payments(self):
        if len(self.payment_strings)==0: 
            return ""    

        majority_vote = self.payment_strings.most_common(1)[0][0]
        return majority_vote

    def _extract_high_conf_dates(self, dates:set):
        '''extracts the date which contains time, should be unique within a receipt'''
        #eg use case {'7/2/2000 ', '7/2/2020 7:35:42 PM'}, the 2020 higher conf

        # heuristic 1: with time
        tpat="[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?(\s+[AP]M)?"
        date_withTime = filter((lambda x: re.search(tpat, x) is not None), dates) #iterator
        return next(date_withTime, None)


    def analyze_errors(self):
        #return error reports, plots
        return None