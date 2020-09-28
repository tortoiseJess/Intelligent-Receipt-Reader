import cv2
import numpy as np
from PIL import Image
import pytesseract as tess
import collections
import re

tess.pytesseract.tesseract_cmd = r'D:\\ProgramFiles\\Tesseract-OCR\\tesseract-ocr_v5\\tesseract.exe'
DEBUG = False

class TesseractHandler:
    def __init__(self, image):
        self.image = image

    def ocr(self, theta=0):
        '''Return:  dict , key = (b,p,l)  Value =(word:list, conf:list)'''
        rot_img = self.rotate_image(self.image, theta)

        d = tess.image_to_data(rot_img,output_type=tess.Output.DICT)
        lines_dict = collections.defaultdict(list) #key = (b,p,l). value = (word list, conf list<int>)
        n_boxes = len(d['left'])
        for i in range(1, n_boxes):
            #ignore -1 prob indicating the prob of a line, only capture word prob
            if int(d['conf'][i])>0: 
                lines_dict[(d['block_num'][i], d['par_num'][i], d['line_num'][i])]\
                    .append((d['text'][i], int(d['conf'][i]))) 

            if DEBUG:
                conf = int(d['conf'][i])
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                ## if indicates a word, color it red 
                if conf==-1:
                    cv2.rectangle(rot_img, (x, y), (x + w, y + h), (0, 0,255), 1)
                # else color in green
                elif conf>=10:
                    cv2.rectangle(rot_img, (x, y), (x + w, y + h), (0, 255,0), 1)
                    nameReceipt = re.split('\\\|\.',rot_img)[-2] #todo use python's sys/os lib to split, create dir
                cv2.imwrite("{}_tess_blocks_theta-{}.jpg".format(nameReceipt ,theta), rot_img)
        
        for k in list(lines_dict.keys()):
            line = [x[0] for x in lines_dict[k]]
            conf = [x[1] for x in lines_dict[k]]
            lines_dict[k] = (line, conf)

        if DEBUG:
            #print line by line to text
            result_file = "{}_tess_results_theta-{}.txt".format( nameReceipt,theta)
            with open(result_file, "w") as f:
                for k in list(lines_dict.keys()):
                    f.write("\n")
                    f.write("block {}, para {}, line_num {}: \n".format(*k))
                    f.write(" ".join(x[0] ))
                    f.write("\n")
                    f.write(", ".join([str(x) for x in lines_dict[k][1]]))
                    f.write("\n")

        return lines_dict
        
    def rotate_image(self, imFile, angle):
        image = cv2.imread(imFile)
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], \
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return result