import numpy as np
import tensorflow as tf
from sklearn.neighbors.kd_tree import KDTree
from collections import deque


class DND:
    def __init__(self, capacity=10 ** 4, p=10, lr=0.1):
        self.capacity = capacity
        self.p = p
        self.lr = lr
        self.memory_keys = []
        self.memory_values = []
        self.ages = np.zeros((capacity), np.int32)

    def lookup(self, h):
        if len(self.memory_values) == 0:
            return np.zeros((len(h), 1, len(h[0])), dtype=np.float32), np.zeros((len(h), 1), dtype=np.float32)
        keys = np.array(self.memory_keys, dtype=np.float32)
        values = np.array(self.memory_values, dtype=np.float32)
        size = keys.shape[0]
        if size < self.p:
            k = size
        else:
            k = self.p
        queried_keys = np.zeros((len(h), k, len(h[0])), dtype=np.float32)
        queried_values = np.zeros((len(h), k), dtype=np.float32)
        for i, encoded_state in enumerate(h):
            tree = KDTree(keys, leaf_size=50)
            distances, indices = tree.query(np.array([encoded_state], dtype=np.float32), k=k)
            queried_keys[i] = keys[indices]
            queried_values[i] = values[indices][-1]
            self.ages += 1
            self.ages[indices] = 0
        return queried_keys, queried_values

    def write(self, h, v):
        keys = np.array(self.memory_keys, dtype=np.float32)
        values = np.array(self.memory_values, dtype=np.float32)
        if len(self.memory_keys) > 0:
            tree = KDTree(keys, leaf_size=50)
            distance, index = tree.query(np.array([h], dtype=np.float32))
            if distance[0][0] == 0:
                index = index[0][0]
                self.memory_values[index] += self.lr * (v - self.memory_values[index])
                return
        if len(self.memory_values) < self.capacity:
            self.ages[len(self.memory_values) - 1] = 0
            self.memory_keys.append(h)
            self.memory_values.append(v)
        else:
            index = np.argmin(self.ages)
            self.memory_keys[index] = h
            self.memory_values[index] = v
            self.ages[index] = 0
