from PIL import Image
import random
import numpy as np
from QuadTree import QuadTree

def ApplyF(pixel_values, t_r, b_r, l_c, r_c, count):
    if count == 0:
        return
    else:
        H = b_r - t_r
        W = r_c - l_c
        ApplyF(pixel_values, t_r, b_r // 2, r_c, l_c // 2, count-1)
        ApplyF(pixel_values, t_r, b_r // 2, r_c+W//2, l_c, count-1)
        ApplyF(pixel_values, t_r+H//2, b_r, r_c, l_c // 2, count-1)
        ApplyF(pixel_values, t_r+H//2, b_r // 2, r_c+W//2, l_c, count-1)
        
        pixel_values[t_r:b_r, l_c:r_c] *= random.randint(4,6)


def main():
    img = Image.open('pipes.jpg', 'r').convert('L')
    print(img.format, img.size, img.mode)
    pixel_values = np.array(img, dtype = 'uint16')
    
    r,c = pixel_values.shape
    Q = QuadTree()
    Q.BuildTree(pixel_values)

    pixel_values_temp = Q.RenderTree()
    new = Image.fromarray(pixel_values_temp)
    new.convert('L').save('temp', 'PNG')


    img = Image.open('temp', 'r').convert('L')
    pixel_values_temp = np.array(img, dtype = 'uint16')
    r,c = pixel_values_temp.shape
    Q = QuadTree()
    Q.BuildTree(pixel_values_temp)
    Q.compressTree(r,c)   
    pixel_values_output = Q.RenderTree()
    output = Image.fromarray(pixel_values_output)
    output.convert('L').save('output', 'PNG')

if __name__ == '__main__':
    main()