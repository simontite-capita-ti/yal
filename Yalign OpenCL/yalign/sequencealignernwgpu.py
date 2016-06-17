# -*- coding: utf-8 -*-
"""
Module for handling sequence alignment.
"""
import numpy as np
import pyopencl as cl
from pyopencl import array
from clalign import Clp
import sys

# the three directions you can go in the traceback:
DIAG = 0 
UP = 1 
LEFT = 2

class CL:
    def __init__(self):

        # The following krz original line does nothing
        # cl.CommandQueue

        # The following krz original code breaks on a machine with no devices of type .GPU, however on the development
        # system there is a device called 'Intel Core i5.3210M CPU @ 2.50 GHz' on 'AMD Accelerated Parallel Processing',
        # which works with adventures_in_opencl/python/part1/main.py.
        # platform = cl.get_platforms()
        # my_gpu_devices = [platform[0].get_devices(device_type=cl.device_type.GPU)[0]] # This line causes error if empty list returned.

        platform = cl.get_platforms()
        device_list = platform[0].get_devices(device_type=cl.device_type.GPU)
        if len(device_list) == 0:
            device_list = platform[0].get_devices(device_type=cl.device_type.ALL)
        my_gpu_devices = [device_list[0]]

        self.ctx = cl.Context(devices=my_gpu_devices)
        #sys.stderr.write('Devices:\n' + '\n' + my_gpu_devices[0].__name__ + '\n')
        self.queue = cl.CommandQueue(self.ctx)

    def loadProgram(self, filename):
        #read in the OpenCL source file as a string
        #f = open(filename, 'r')
        #fstr = "".join(f.readlines())
      
        #create the program
        #self.program = cl.Program(self.ctx, fstr).build()
        self.program = cl.Program(self.ctx, Clp.program).build()

    def process(self,  s_matrix, n, m):
        mf = cl.mem_flags
        #initialize client side (CPU) arrays
        s = np.zeros((m +1) * (n+1), dtype = np.int32)
        s_m = s_matrix.flatten()
        #create OpenCL buffers
        self.s_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=s)
        self.s_matrix_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s_m)

        t_n = n+1
        t_m = m+1

        for d in range(0,  t_m + t_n -1):
            self.program.alignment_kernel(self.queue, (t_n, t_m,) , None, 
                                          self.s_buf,self.s_matrix_buf, np.int32(t_n), 
                                          np.int32(t_m), np.int32(d))
             
#        cl.enqueue_read_buffer(self.queue, self.s_buf, s).wait()
        cl.enqueue_copy(self.queue, s, self.s_buf)
        self.queue.finish() 
        self.s_buf.release()
        self.s_matrix_buf.release()
        return s

class SequenceAlignerNWGPU(object):
    """
    Aligns two sequences.
    """
    def __init__(self, score, threshold):
        self.score = score
        self.threshold = threshold
        self.s_matrix = None
        
        self.cl = CL()
        self.cl.loadProgram("align.cl")

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
            
        align1, align2 = self.needleman_wunsch_matrix( xs, ys, score, threshold )
        
        
        path = []
        n = len(align1)
        for i in range(0, n) :
            if align1[i] != -1 and align2[i] !=-1 :
                if (self.s_matrix[align1[i],align2[i]]):
                    path.append([align1[i], align2[i]])
        
        return path
                
        
    def needleman_wunsch_matrix(self, xs, ys, score, threshold ):
        """
        fill in the DP matrix according to the Needleman-Wunsch algorithm.
        Returns the matrix of scores and the matrix of pointers
        """
     
        n = len(xs)
        m = len(ys)
      
        
        ##### INITIALIZE SCORING MATRIX
        self.s_matrix = np.zeros( (n+1, m+1), dtype = np.int32  )
        for i in range(1,n+1):
            for j in range(1,m+1): 
                if score(xs[i-1] , ys[j-1]) < threshold:
                    self.s_matrix[i-1,j-1] = 1
                else:
                    self.s_matrix[i-1,j-1] = 0

     
        s = self.cl.process(self.s_matrix, n, m)
        
#         f = open("s.txt", "w")
#         for i in range(0, n +1):
#             for j in range(0,m+1):
#                 f.write(str(s[i*(m+1)+j] )+" ")
#             f.write("\n")
#         f.close()
        #### TRACE BEST PATH TO GET ALIGNMENT ####
        align1 = []
        align2 = []
        n, m = (len(xs), len(ys))
        i,j = n,m
        while (i > 0 and j > 0): 
            scroeDiag = -1
            if  self.s_matrix[i-1, j-1] == 1:
                scroeDiag = 1
            if (i > 0 and j > 0 and s[i * (m +1) +j] == s[(i-1) * (m+1) + j - 1] + scroeDiag):
                align1.insert(0, i-1) 
                align2.insert(0, j-1)
                i = i - 1;
                j = j - 1;
    
            elif (i > 0 and s[i * (m+1) +j] == s[(i-1) *(m+1) + j ] - 1 ):
                align1.insert(0, i -1)
                align2.insert(0, -1) 
                i -= 1
            else :
                align1.insert(0, -1)
                align2.insert(0, j-1)
                j -= 1
        return align1, align2 
        
    
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
