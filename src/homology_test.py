import homologies_alt
import numpy as np

poset = [1, 2, 4, 6, 8]

arr = np.array([
    [5,   6,   7,   6,   5],
    [4,   1,   2,  -1,   5],
    [4,   9,  15,  24,   4]])

homologies_alt.pixellize(arr, poset)

print arr
print homologies_alt.get_homologies(arr, 1)
