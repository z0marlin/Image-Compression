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

class QuadTree:
    def __init__(self):
        self._list=[]
    
    def _BuildTreeUtil(self, pixel_array, index, b):
        print(b,index)
        if b.left > b.right or b.top > b.bottom or index >= self.size :
            return 0
        if (b.left == b.right and b.top == b.bottom) :
            self._list[index]=pixel_array[b.left,b.top]
            return self._list[index]

        mid_v=(b.right+b.left)//2
        mid_h=(b.bottom+b.top)//2
        self._list[index] = (
        self._BuildTreeUtil(pixel_array, 4*index+1, bounds((b.left,mid_v,b.top,mid_h)))+
        self._BuildTreeUtil(pixel_array, 4*index+2, bounds((mid_v+1, b.right, b.top, mid_h)))+
        self._BuildTreeUtil(pixel_array, 4*index+3, bounds((b.left, mid_v, mid_h+1, b.bottom)))+
        self._BuildTreeUtil(pixel_array, 4*index+4, bounds((mid_v+1, b.right, mid_h+1, b.bottom))))
        self._list[index]//=4
        return self._list[index]

    def BuildTree(self, pixel_array ) :
        r,c = pixel_array.shape
        self._list = [None for i in range(2*r*c)]
        self._BuildTreeUtil(pixel_array, 0, bounds((0, c-1, 0, r-1)))
    
    @property
    def size(self):
        return len(self._list)

    def printTree(self) :
        print(self._list)

# qt = QuadTree()
# qt.BuildTree(np.zeros((2,2),dtype='int64'))
# qt.printTree()