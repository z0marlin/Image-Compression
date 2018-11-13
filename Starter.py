from PIL import Image
from QuadTree import QuadTree
import random
import numpy as np
import sys
import time
import datetime

def main():
    for image in sys.argv[1:]:
        print("********************************************")
        print("Image : " + image)
        img = Image.open(image, 'r').convert('L')
        img.convert('L').save(image + 'Temp', 'PNG')
        img = Image.open(image + 'Temp', 'r').convert('L')
        pixel_values = np.array(img, dtype = 'uint16')
        Q = QuadTree()
        Q.deviation_threshold = float(input("Enter threshold : "))
        start = time.time()
        print("Started processing",image,'at',datetime.datetime.now())
        Q.BuildTree(pixel_values)
        Q.compressTree()   
        pixel_values_output = Q.RenderTree()
        output = Image.fromarray(pixel_values_output)
        output.convert('L').save(image + 'Output', 'PNG')
        end = time.time()
        print('Finished processing',image,'at',datetime.datetime.now())
        print('Time difference',end-start)
        print('Output image : ',image + 'Output')

if __name__ == '__main__':
    main()