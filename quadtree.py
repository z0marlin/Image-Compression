import numpy as np
from statistics import mean, pstdev

class QuadTreeNode :
    
    def __init__(self, greyscale, homogenity = False) :
        self.greyscale = greyscale
        self.homogenity = homogenity

    def __add__(self, other) :
        return self.greyscale + other.greyscale
    
    def __nonzero__(self) :
        return self.homogenity

class region :

    def __init__(self, boundaries) :
        self._boundaries = boundaries

    @property
    def left(self) :
        return self._boundaries[0]

    @property
    def right(self):
        return self._boundaries[1]
    
    @property
    def top(self):
        return self._boundaries[2]
    
    @property
    def bottom(self):
        return self._boundaries[3]

    @staticmethod
    def CheckBounds(quadrant):
        return quadrant.left <= quadrant.right and quadrant.top <= quadrant.bottom
    
    @staticmethod
    def IsPixel(region_) :
        return region_.left == region_.right and region_.top == region_.bottom
        
    def __str__(self):
        return str(self._boundaries)

class QuadTree :

    DEVIATION_THRESHOLD = 0.07

    def __init__(self) :
        self._list=[]
        self._image_size=(0,0) 

    def _BuildTreeUtil(self, pixel_matrix, index, quadrant):

        if not region.CheckBounds(quadrant) :
            return 0

        if region.IsPixel(quadrant) :
            self._list[index] = QuadTreeNode(pixel_matrix[quadrant.left, quadrant.top], True)

        vertical_middle = (quadrant.right+quadrant.left)//2
        horizontal_middle = (quadrant.top+quadrant.bottom)//2


        quad_top_left = region((quadrant.left, vertical_middle, quadrant.top, horizontal_middle))
        quad_top_right = region((vertical_middle+1, quadrant.right, quadrant.top, horizontal_middle))
        quad_bottom_left = region((quadrant.left, vertical_middle, horizontal_middle+1, quadrant.bottom))
        quad_bottom_right = region((vertical_middle+1, quadrant.right, horizontal_middle+1, quadrant.bottom))

        val = (
        self._BuildTreeUtil(pixel_matrix, 4*index+1, quad_top_left)+
        self._BuildTreeUtil(pixel_matrix, 4*index+2, quad_top_right)+
        self._BuildTreeUtil(pixel_matrix, 4*index+3, quad_bottom_left)+
        self._BuildTreeUtil(pixel_matrix, 4*index+4, quad_bottom_right))//4
        
        self._list[index] = QuadTreeNode(val)
        return self._list[index]

    def _RenderTreeUtil(self, pixel_matrix, index, quadrant) :
        if not region.CheckBounds(quadrant) :
            return
        if region.IsPixel(quadrant) :
            pixel_matrix[quadrant.left, quadrant.top] = self._list[index].greyscale
            return

        vertical_middle = (quadrant.right + quadrant.left)//2
        horizontal_middle = (quadrant.top + quadrant.bottom)//2

        quad_top_left = region((quadrant.left, vertical_middle, quadrant.top, horizontal_middle))
        quad_top_right = region((vertical_middle+1, quadrant.right, quadrant.top, horizontal_middle))
        quad_bottom_left = region((quadrant.left, vertical_middle, horizontal_middle+1, quadrant.bottom))
        quad_bottom_right = region((vertical_middle+1, quadrant.right, horizontal_middle+1, quadrant.bottom))

        self._RenderTreeUtil(pixel_matrix, 4*index+1, quad_top_left)
        self._RenderTreeUtil(pixel_matrix, 4*index+2, quad_top_right)
        self._RenderTreeUtil(pixel_matrix, 4*index+3, quad_bottom_left)
        self._RenderTreeUtil(pixel_matrix, 4*index+4, quad_bottom_right)

    def _FillDescendants(self, index, quadrant, value) :

        if not region.CheckBounds(quadrant) :
            return
        if region.IsPixel(quadrant) :
            self._list[index].greyscale = value
            self._list[index].homogenity = True 
            return
        
        vertical_middle = (quadrant.left + quadrant.right) // 2
        horizontal_middle = (quadrant.top + quadrant.bottom) // 2

        quad_top_left = region((quadrant.left, vertical_middle, quadrant.top, horizontal_middle))
        quad_top_right = region((vertical_middle+1, quadrant.right, quadrant.top, horizontal_middle))
        quad_bottom_left = region((quadrant.left, vertical_middle, horizontal_middle+1, quadrant.bottom))
        quad_bottom_right = region((vertical_middle+1, quadrant.right, horizontal_middle+1, quadrant.bottom))

        self._list[index].greyscale = value
        self._list[index].homogenity = True
        self._FillDescendants(4*index+1, quad_top_left, value)
        self._FillDescendants(4*index+2, quad_top_right, value)
        self._FillDescendants(4*index+3, quad_bottom_left, value)
        self._FillDescendants(4*index+4, quad_bottom_right, value)

    def _PruneTree(self, index, quadrant) :

        if not region.CheckBounds(quadrant) :
            return 0
        if region.IsPixel(quadrant) :
            return self._list[index].greyscale


        vertical_middle = (quadrant.left + quadrant.right) // 2
        horizontal_middle = (quadrant.top + quadrant.bottom) // 2

        quad_top_left = region((quadrant.left, vertical_middle, quadrant.top, horizontal_middle))
        quad_top_right = region((vertical_middle+1, quadrant.right, quadrant.top, horizontal_middle))
        quad_bottom_left = region((quadrant.left, vertical_middle, horizontal_middle+1, quadrant.bottom))
        quad_bottom_right = region((vertical_middle+1, quadrant.right, horizontal_middle+1, quadrant.bottom))

        value_tl = self._PruneTree(4*index+1, quad_top_left)
        value_tr = self._PruneTree(4*index+2, quad_top_right)
        value_bl = self._PruneTree(4*index+3, quad_bottom_left)
        value_br = self._PruneTree(4*index+4, quad_bottom_right)

        average = mean([value_tl, value_tr, value_bl, value_br])
        deviation = pstdev([value_tl, value_tr, value_bl, value_br])

        homogenity = self._list[4*index+1] and self._list[4*index+2] and self._list[4*index+3] and self._list[4*index+4]

        if deviation <= self.DEVIATION_THRESHOLD and homogenity :
            self._FillDescendants(index,quadrant, int(average))
            self._list[index].greyscale = int(average)
            self._list[index].homogenity = True

        return self._list[index].greyscale

    def BuildTree(self, pixel_matrix) :
        c,r = self._image_size = pixel_matrix.shape
        self._list = [None for i in range(3*r*c)]
        self._BuildTreeUtil(pixel_matrix, 0, region((0, c-1, 0, r-1)))

    def RenderTree(self) :
        c,r = image_size = self.image_size
        pixel_matrix = np.empty(image_size, dtype='uint16')
        quadrant = region((0, c-1, 0, r-1))
        self._RenderTreeUtil(pixel_matrix, 0, quadrant)
        return pixel_matrix
                   
    def CompressTree(self) :
        c,r = self.image_size
        self._PruneTree(0, region((0, c-1, 0, r-1)))

    @property
    def image_size(self):
        return self._image_size
    
            

