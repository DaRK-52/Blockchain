#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 3.6

import copy
import torch
from torch import nn
import numpy as np

def SquareSum(w1, w2):
    sum = 0
    for k in w1.keys():
        if (sum == 0):
            sum = pow(w1[k] - w2[k], 2)
        else:
            sum = sum + pow(w1[k] - w2[k], 2)
    return sum

def FedAvg(w):
    w_avg = copy.deepcopy(w[0])
    for k in w_avg.keys():
        for i in range(1, len(w)):
            w_avg[k] += w[i][k]
        w_avg[k] = torch.div(w_avg[k], len(w))
    return w_avg

def MultiKrum(w):
    d = [[for i in range(len(w))] for j in range(len(w))]
    score = [for i in range(len(w))]
    for i in range(len(w)):
        for j in range(len(w)):
            if (i == j):
                continue
            d[i][j] = SquareSum(w[i], w[j])
    
    for i in range(len(w)):
        score[i] = sum(d[i])
    sorted_indices = np.argsort(score[:], axis = 0)
    sorted_w = w[sorted_indices]

    w_avg = copy.deepcopy(sorted_w[0])
    for k in w_avg.keys():
        for i in range(1, len(w) * 2 / 3):
            w_avg[k] += sorted_w[i][k]
        w_avg[k] = torch.div(w_avg[k], len(w) * 2 / 3)
    return w_avg

            