import TessResult as TR
import difflib

class ErrorAnalysis(object):

    def plot_scoring_freeRotate(self, tessResult, theta, scoring_strategy=0):
        #to evaluate if my scoring function is a unimodal function, cts
        
        if scoring_strategy == 0:
            score_dict = lambda x: tessResult.binning_scoring_method(x)
            return score_dict
        else:
            #use mse TODO
            return 0

    def count_hitRate(self, ocr_text, groundTruthFile)->float:
        '''word to word count of hit rate compared to ground truth text'''

        #split lines to obtain word count of dfiferences
        #since split respects line ordering + word ordering
        with open(groundTruthFile, "r") as f:
            truth = f.readlines()
        with open(ocr_text, "r") as f:
            ocr = f.readlines()       
        wordsT =[ t.split() for t in truth]
        wordsC = [ t.split() for t in ocr]
        all_words_count = len(wordsT)

        d = difflib.Differ(charjunk=lambda x: x == " ") #TODO vs charjunk
        comparision = list(d.compare(groundTruthFile,ocr_text))

        hit=0
        for i in range(len(comparision)):
            if comparision[i][0] == "  ":
                hit+=1
        
        return hit/all_words_count



