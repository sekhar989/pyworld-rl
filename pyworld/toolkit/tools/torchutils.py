#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:44:12 2019

@author: ben
"""

import torch
import torch.nn as nn
import numpy as np   

from . import datautils as du 

def as_shape(shape):
    if isinstance(shape, tuple):
        return shape
    elif isinstance(shape, int):
        return (shape,)
    else:
        raise ValueError("Invalid shape argument: {0}".format(str(shape)))

def collect(fun, *data, batch_size=128):
    if len(data) == 1:
        return torch.cat(du.__collect_singular(fun, *data, batch_size=batch_size), 0)
    else:
        raise NotImplementedError()

def load(model, *args, device = 'cpu', path = None, **kwargs):
    model_ = model(*args, **kwargs).to(device)
    if path is not None:
        model_.load_state_dict(torch.load(path))    
    return model_
        
def batch_to_numpy(batch, types, copy=False):
    return [np.array(batch[i], copy=copy, dtype=types[i]) for i in range(len(batch))]

def batch_to_tensor(batch, types, device='cpu'):
        return [types[i](batch[i]).to(device) for i in range(len(batch))]
    
def distance_matrix(x, y):
    x = x.view(x.shape[0], -1)
    y = y.view(y.shape[0], -1)
    dist_mat = torch.empty((x.shape[0], y.shape[0]), dtype=x.dtype)
    for i, row in enumerate(x.split(1)):
        r_v = row.expand_as(y)
        sq_dist = torch.sum((r_v - y) ** 2, 1)
        dist_mat[i] = sq_dist.view(1, -1)
    return dist_mat    

def to_numpy(x):
    '''
        Converts x to a numpy array, detaching gradient information and moving to cpu if neccessary.
    '''
    if isinstance(x, torch.Tensor):
        x = x.cpu()
        if x.requires_grad:
            x = x.detach()
        return x.numpy()
    elif isinstance(x, np.ndarray):
        return x
    else:
        raise TypeError

def to_numpyf(model):
    '''
        Use: Wraps the output of a function (model) to a numpy array using numpy(x).
    '''
    return lambda *x: to_numpy(model(*x))
    
def device(display=True):
    device = None
    if(torch.cuda.is_available()): 
        device = 'cuda'
    else:
        device = 'cpu'
    if display:
        print("USING DEVICE:", device)
    return device

def conv_output_shape(input_shape, channels, kernel_size=1, stride=1, pad=0, dilation=1):
    '''
        Get the output shape of a convolution given the input_shape.
        Arguments:
            input_shape: in CHW (or HW) format
            TODO
    '''
    from math import floor
    h_w = input_shape[-2:]

    if type(kernel_size) is not tuple:
        kernel_size = (kernel_size, kernel_size)
    h = floor( ((h_w[0] + (2 * pad) - ( dilation * (kernel_size[0] - 1) ) - 1 )/ stride) + 1)
    w = floor( ((h_w[1] + (2 * pad) - ( dilation * (kernel_size[1] - 1) ) - 1 )/ stride) + 1)
    return channels, h, w

def default_conv2d(input_shape):    
    assert len(input_shape) == 2
    s1 = conv_output_shape(input_shape, kernel_size=4, stride=2)
    s2 = conv_output_shape(s1, kernel_size=3, stride=1)
    s3 = conv_output_shape(s2, kernel_size=3, stride=1)
    
    layers = [nn.Conv2d(1, 16, kernel_size=4, stride=2),
              nn.Conv2d(16, 32, kernel_size=3, stride=1),
              nn.Conv2d(32, 64, kernel_size=3, stride=1)]
    
    return layers, [s1, s2, s3]
