import numpy as np

DEVIATION_THRESHOLD = 0.07

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

    @staticmethod
    def checkBounds(b):
        return b.left <= b.right and b.top <= b.bottom
        

    def __str__(self):
        return str(self._b)
        
class QuadTree:

    def __init__(self):
        self._list=[]
        self._image_size=(0,0)
    
    def _BuildTreeUtil(self, pixel_matrix, index, b):
        # print(b,index)
        if not bounds.checkBounds(b) : 
            return 0
        if (b.left == b.right and b.top == b.bottom) :
            self._list[index]=(pixel_matrix[b.left,b.top], True)
            return self._list[index][0]

        mid_v=(b.right+b.left)//2
        mid_h=(b.bottom+b.top)//2
        val = (
        self._BuildTreeUtil(pixel_matrix, 4*index+1, bounds((b.left,mid_v,b.top,mid_h)))+
        self._BuildTreeUtil(pixel_matrix, 4*index+2, bounds((mid_v+1, b.right, b.top, mid_h)))+
        self._BuildTreeUtil(pixel_matrix, 4*index+3, bounds((b.left, mid_v, mid_h+1, b.bottom)))+
        self._BuildTreeUtil(pixel_matrix, 4*index+4, bounds((mid_v+1, b.right, mid_h+1, b.bottom))))//4
        self._list[index] = (val, False)
        return val

    def _RenderTreeUtil(self, pixel_matrix, index, b) :
        if not bounds.checkBounds(b) :
            return
        if b.left==b.right and b.top==b.bottom :
            pixel_matrix[b.left, b.top] = self._list[index][0]
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

    def _FillDescendants(self, index, quadrant, value) :
        if not bounds.checkBounds(quadrant) :
            return
        if quadrant.left == quadrant.right and quadrant.top == quadrant.bottom :
            self._list[index] = (value, True)
            return

        # print('--',quadrant,index,'--')

        vertical_middle = (quadrant.left + quadrant.right) // 2
        horizontal_middle = (quadrant.top + quadrant.bottom) // 2
        quad_top_left = bounds((quadrant.left, vertical_middle, quadrant.top, horizontal_middle))
        quad_top_right = bounds((vertical_middle+1, quadrant.right, quadrant.top, horizontal_middle))
        quad_bottom_left = bounds((quadrant.left, vertical_middle, horizontal_middle+1, quadrant.bottom))
        quad_bottom_right = bounds((vertical_middle+1, quadrant.right, horizontal_middle+1, quadrant.bottom))
        self._list[index] = (value,True)
        self._FillDescendants(4*index+1, quad_top_left, value)
        self._FillDescendants(4*index+2, quad_top_right, value)
        self._FillDescendants(4*index+3, quad_bottom_left, value)
        self._FillDescendants(4*index+4, quad_bottom_right, value)


    def _GetDeviation(self,a,b,c,d,avg) :
        if avg == 0: #all black
            return 0 
        square_sum = (avg-a)**2 + (avg-b)**2 + (avg-c)**2 + (avg-d)**2
        rms = (square_sum/4)**0.5
        return rms/avg
        
 
    def _PruneTree(self, index, quadrant) :
        if not bounds.checkBounds(quadrant) :
            return 0
        if quadrant.left==quadrant.right and quadrant.top==quadrant.bottom :
            return self._list[index][0]


        vertical_middle = (quadrant.left + quadrant.right) // 2
        horizontal_middle = (quadrant.top + quadrant.bottom) // 2
        quad_top_left = bounds((quadrant.left, vertical_middle, quadrant.top, horizontal_middle))
        quad_top_right = bounds((vertical_middle+1, quadrant.right, quadrant.top, horizontal_middle))
        quad_bottom_left = bounds((quadrant.left, vertical_middle, horizontal_middle+1, quadrant.bottom))
        quad_bottom_right = bounds((vertical_middle+1, quadrant.right, horizontal_middle+1, quadrant.bottom))
        qt_tl = self._PruneTree(4*index+1, quad_top_left)
        qt_tr = self._PruneTree(4*index+2, quad_top_right)
        qt_bl = self._PruneTree(4*index+3, quad_bottom_left)
        qt_br = self._PruneTree(4*index+4, quad_bottom_right)
        value = (qt_tl+qt_tr+qt_bl+qt_br)/4
        homogenous = self._list[4*index+1][1] and self._list[4*index+2][1] and self._list[4*index+3][1] and self._list[4*index+4][1]
        #print('--',qt_tl, qt_tr, qt_bl, qt_br,'--')
        if self._GetDeviation(qt_tl, qt_tr, qt_bl, qt_br, value) <= DEVIATION_THRESHOLD and homogenous:
            self._FillDescendants(index, quadrant, int(value))
            self._list[index] = (int(value),True)

        return self._list[index][0]

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
                   
    def compressTree(self) :
        c,r = self.image_size
        self._PruneTree(0, bounds((0, c-1, 0, r-1)))
    
    
    @property
    def length(self):
        return len(self._list)
    
    @property
    def image_size(self):
        return self._image_size

    def printTree(self) :
        print(self._list)

# qt = QuadTree()
# qt.BuildTree(np.zeros((2,2),dtype='uint16'))
# qt.printTree()
# matrix = qt.RenderTree()
# print(matrix)
