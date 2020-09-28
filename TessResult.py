
import numpy as np 
from enum import Enum

class Scoring(Enum):
    MSE = 0
    BINNING = 1

class TessResult(object):
    def __init__(self, \
            theta, imgFile: str,  \
            ocr_results:dict, basics_data:dict, \
            scoring_method=Scoring.MSE
        ):

        self.theta = theta
        self.image = imgFile

        self.parsed_lookup = ocr_results #key=(b,p,l), value=(words_list,conf_list)
        self.basic_data = basics_data
        self.accuracy=0.0

        self.scoring_method =scoring_method

        self.avg_line_score=-1
    
    def get_receipt_basic_data(self):
        # getter for basic_data, exposed for Reader
        return self.basic_data
    
    
    def calculate_total_accuracy(self)->float:
        if self.scoring_method is Scoring.MSE:
            return self.mean_squared_error_confidence()
        return -1
   
    def mean_squared_error_confidence(self):
        conf_list = [x[1] for x in self.parsed_lookup.values()]
        conf_vec = np.array(conf_list).reshape((-1,1))
        shape = conf_vec.shape
        #assume the ground truth is everything prob 1 
        ones = np.ones(shape) 
        #elementwise mse
        mse = np.square(ones-conf_vec).mean(axis=None) 
        return mse







