from PIL import Image
import random
import numpy as np
from QuadTree import QuadTree

# def ApplyF(pixel_values, t_r, b_r, l_c, r_c, count):
#     if count == 0:
#         return
#     else:
#         W = r_c - l_c
#         H = b_r - t_r
#         ApplyF(pixel_values, t_r, b_r // 2, r_c, l_c // 2, count-1)
#         ApplyF(pixel_values, t_r, b_r // 2, r_c+W//2, l_c, count-1)
#         ApplyF(pixel_values, t_r+H//2, b_r, r_c, l_c // 2, count-1)
#         ApplyF(pixel_values, t_r+H//2, b_r // 2, r_c+W//2, l_c, count-1)
        
#         pixel_values[t_r:b_r, l_c:r_c] *= random.randint(4,6)


def main():
    img = Image.open('temp/scene.jpg', 'r').convert('L')
    img.convert('L').save('temp/.temp', 'PNG')
    img = Image.open('temp/.temp', 'r').convert('L')
    pixel_values = np.array(img, dtype = 'uint16')

    Q = QuadTree()
    Q.BuildTree(pixel_values)
    # Q.printTree()
    Q.compressTree()   
    pixel_values_output = Q.RenderTree()
    # Q.printTree()
    output = Image.fromarray(pixel_values_output)
    output.convert('L').save('temp/output', 'PNG')

if __name__ == '__main__':
    main()