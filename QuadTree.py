import numpy as np

class bounds :
    def __init__(self,b):
        self._b=b

    @property
    def left(self):
        return self._b[0]
    
    @property
    def right(self):
        return self._b[1]
    
    @property
    def top(self):
        return self._b[2]
    
    @property
    def bottom(self):
        return self._b[3]

    def __str__(self):
        return str(self._b)
        

VARIANCE_THRESHOLD = 4000
class QuadTree:

    def __init__(self):
        self._list=[]
        self._image_size=(0,0)
    
    def _BuildTreeUtil(self, pixel_matrix, index, b):
        # print(b,index)
        if b.left > b.right or b.top > b.bottom :
            return 0
        if (b.left == b.right and b.top == b.bottom) :
            self._list[index]=pixel_matrix[b.left,b.top]
            return self._list[index]

        mid_v=(b.right+b.left)//2
        mid_h=(b.bottom+b.top)//2
        self._list[index] = (
        self._BuildTreeUtil(pixel_matrix, 4*index+1, bounds((b.left,mid_v,b.top,mid_h)))+
        self._BuildTreeUtil(pixel_matrix, 4*index+2, bounds((mid_v+1, b.right, b.top, mid_h)))+
        self._BuildTreeUtil(pixel_matrix, 4*index+3, bounds((b.left, mid_v, mid_h+1, b.bottom)))+
        self._BuildTreeUtil(pixel_matrix, 4*index+4, bounds((mid_v+1, b.right, mid_h+1, b.bottom))))
        self._list[index]//=4
        return self._list[index]

    def _RenderTreeUtil(self, pixel_matrix, index, b) :
        if b.left > b.right or b.top > b.bottom :
            return
        if b.left==b.right and b.top==b.bottom :
            pixel_matrix[b.left, b.top] = self._list[index]
            return
        vertical_middle = (b.right + b.left)//2
        horizontal_middle = (b.top + b.bottom)//2
        quad_top_left = bounds((b.left, vertical_middle, b.top, horizontal_middle))
        quad_top_right = bounds((vertical_middle+1, b.right, b.top, horizontal_middle))
        quad_bottom_left = bounds((b.left, vertical_middle, horizontal_middle+1, b.bottom))
        quad_bottom_right = bounds((vertical_middle+1, b.right, horizontal_middle+1, b.bottom))
        self._RenderTreeUtil(pixel_matrix, 4*index+1, quad_top_left)
        self._RenderTreeUtil(pixel_matrix, 4*index+2, quad_top_right)
        self._RenderTreeUtil(pixel_matrix, 4*index+3, quad_bottom_left)
        self._RenderTreeUtil(pixel_matrix, 4*index+4, quad_bottom_right)
        

    def BuildTree(self, pixel_matrix) :
        c,r = self._image_size = pixel_matrix.shape
        self._list = [None for i in range(4*r*c)]
        self._BuildTreeUtil(pixel_matrix, 0, bounds((0, c-1, 0, r-1)))

    def RenderTree(self) :
        image_size = self.image_size
        r,c = image_size[1], image_size[0]
        pixel_matrix = np.empty(image_size, dtype='uint16')
        b = bounds((0, c-1, 0, r-1))
        self._RenderTreeUtil(pixel_matrix, 0, b)
        return pixel_matrix

    def _compressTreeUtil(self, index, b, value=None):
        if 4*index+4>self.length:
            return

        if b.left > b.right or b.top > b.bottom:
            return 0
        if (b.left == b.right and b.top == b.bottom) :
            if value is not None:
                self._list[index] = value

        mean = self._list[index]
        mid_v=(b.right+b.left)//2
        mid_h=(b.bottom+b.top)//2

        if value is not None:
            self._list[index] = value
            self._compressTreeUtil(4*index+1,bounds((b.left, mid_v, b.top, mid_h)), value)
            self._compressTreeUtil(4*index+2,bounds((mid_v+1, b.right, b.top, mid_h)), value)
            self._compressTreeUtil(4*index+3,bounds((b.left, mid_v, mid_h+1, b.right)), value)
            self._compressTreeUtil(4*index+4,bounds((mid_v+1, b.right, mid_h+1, b.bottom)), value)
        else:
            quadrant2 = self.GetDeviation(4*index+1)
            quadrant1 = self.GetDeviation(4*index+2)
            quadrant3 = self.GetDeviation(4*index+3)
            quadrant4 = self.GetDeviation(4*index+4)

            maximum = max(quadrant1,quadrant2,quadrant3,quadrant4)

            if quadrant2 != maximum:
                self._compressTreeUtil(4*index+1,bounds((b.left, mid_v, b.top, mid_h)), self._list[4*index+1])
            else:
                self._compressTreeUtil(4*index+1,bounds((b.left, mid_v, b.top, mid_h)), None)
            if quadrant1 != maximum:
                self._compressTreeUtil(4*index+2,bounds((mid_v+1, b.right, b.top, mid_h)), self._list[4*index+2])
            else:
                self._compressTreeUtil(4*index+2,bounds((mid_v+1, b.right, b.top, mid_h)), None)
            if quadrant3 != maximum:
                self._compressTreeUtil(4*index+3,bounds((b.left, mid_v, mid_h+1, b.right)), self._list[4*index+3])
            else:
                self._compressTreeUtil(4*index+3,bounds((b.left, mid_v, mid_h+1, b.right)), None)
            if quadrant4 != maximum:
                self._compressTreeUtil(4*index+4,bounds((mid_v+1, b.right, mid_h+1, b.bottom)), self._list[4*index+4])
            else:
                self._compressTreeUtil(4*index+4,bounds((mid_v+1, b.right, mid_h+1, b.bottom)), None)
        

    def GetDeviation(self, index):
        children = [4*index+1,4*index+2,4*index+3,4*index+4]
        deviation = 0
        mean = self._list[index]
        for child in children:
            if child<self.length and self._list[child]:
                deviation += abs(mean - self._list[child])
        return deviation
                
    def compressTree(self,r ,c) :
        self._compressTreeUtil(0, bounds((0, c-1, 0, r-1)),None)
    
    
    @property
    def length(self):
        return len(self._list)
    
    @property
    def image_size(self):
        return self._image_size

    def printTree(self) :
        print(self._list)

qt = QuadTree()
qt.BuildTree(np.zeros((2,2),dtype='uint16'))
qt.printTree()
matrix = qt.RenderTree()
print(matrix)
