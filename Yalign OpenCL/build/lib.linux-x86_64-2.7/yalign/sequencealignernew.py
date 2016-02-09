# -*- coding: utf-8 -*-
"""
Module for handling sequence alignment.
"""
import numpy as np
import time
# the three directions you can go in the traceback:
DIAG = 0 
UP = 1 
LEFT = 2

class SequenceAlignerNW(object):
    """
    Aligns two sequences.
    """
    def __init__(self, score, threshold):
        self.score = score
        self.threshold = threshold
        self.s_matrix = None

    def __call__(self, xs, ys, score=None, threshold=None):
        """
        Returns an alignment of sequences `xs` and `ys` such that it maximizes
        the sum of weights as given by the `score` function.
        The aligment format is a list of tuples `(i, j, cost)` such that:
            `i` and `j` are indexes of elements in `xs` and `ys` respectively.
            The alignment weight is sum(cost for i, j, cost in alignment).
            if `i == None` then `j` is not aligned to anything (is a gap).
            if `j == None` then `i` is not aligned to anything (is a gap).
        If `minimize` is `True` this function minimizes the sum of the weights
        instead.
        """
        if score is None:
            score = self.score
        if threshold is None:
            threshold = self.threshold
            
        ptr = self.needleman_wunsch_matrix( xs, ys, score, threshold )
        align1, align2 = self.needleman_wunsch_trace(xs, ys, ptr)
        
        path = []
        n = len(align1)
        for i in range(0, n) :
            if align1[i] != -1 and align2[i] !=-1 :
                w = self.s_matrix[align1[i],align2[i]]
                if (w < threshold):
                    path.append([align1[i], align2[i]])
        
        return path
                
        
    def needleman_wunsch_matrix(self, xs, ys, score, threshold ):
        """
        fill in the DP matrix according to the Needleman-Wunsch algorithm.
        Returns the matrix of scores and the matrix of pointers
        """
     
        match =  1  # match score
        mismatch = -1  # mismatch penalty
        indel = -1 # indel penalty
     
        n = len(xs)
        m = len(ys)
        s = np.zeros( (n+1, m+1) ) # DP matrix
        ptr = np.zeros( (n+1, m+1), dtype=int  ) # matrix of pointers
        
        ##### INITIALIZE SCORING MATRIX
        start_time = time.time()
        self.s_matrix = np.zeros( (n, m) ) 
        for i in range(0,n):
            for j in range(0,m): 
                self.s_matrix[i,j] = score(xs[i] , ys[j]) 
                
#        print("---fillscore time %s seconds ---" % (time.time() - start_time))
        ##### INITIALIZE SCORING MATRIX (base case) #####
     
        for i in range(1, n+1):
            s[i,0] = indel * i
        for j in range(1, m+1):
            s[0,j] = indel * j
     
        ########## INITIALIZE TRACEBACK MATRIX ##########
     
        # Tag first row by LEFT, indicating initial "-"s
        ptr[0,1:] = LEFT
     
        # Tag first column by UP, indicating initial "-"s
        ptr[1:,0] = UP
     
        #####################################################
     
        for i in range(1,n+1):
            for j in range(1,m+1): 
                # match
                if self.s_matrix[i-1 , j-1] < threshold:
                    s[i,j] = s[i-1,j-1] + match
                    ptr[i,j] = DIAG
                # mismatch
                else :
                    s[i,j] = s[i-1,j-1] + mismatch
                    ptr[i,j] = DIAG
                # indel penalty
                if s[i-1,j] + indel > s[i,j] :
                    s[i,j] = s[i-1,j] + indel
                    ptr[i,j] = UP
                # indel penalty
                if s[i, j-1] + indel > s[i,j]:
                    s[i,j] = s[i, j-1] + indel
                    ptr[i,j] = LEFT
     
        return ptr
    
    def needleman_wunsch_trace(self, xs, ys, ptr) :
     
        #### TRACE BEST PATH TO GET ALIGNMENT ####
        align1 = []
        align2 = []
        n, m = (len(xs), len(ys))
        i = n
        j = m
        curr = ptr[i, j]
        while (i > 0 or j > 0):        
            ptr[i,j] += 3
            if curr == DIAG :            
                align1.insert(0, i-1) 
                align2.insert(0, j-1)
                i -= 1
                j -= 1            
            elif curr == LEFT:
                align1.insert(0, -1)
                align2.insert(0, j-1)
                j -= 1            
            elif curr == UP:
                align1.insert(0, i-1)
                align2.insert(0, -1) 
                i -= 1
     
            curr = ptr[i,j]
     
        return align1, align2   
