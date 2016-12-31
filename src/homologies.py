import numpy as np
from matplotlib import pyplot as plt

import utils
import algos

def get_ranks_for_i(image, poset, i):

  n = len(poset)
  res = np.zeros((n,))
  print(poset[i])
  arr = utils.pixels_at_least(image, poset[i])
  visited = np.zeros_like(arr, dtype=int)
  
  # plt.figure()
  # plt.imshow(arr)

  cc_in_image = 0 # image of a map, not to be confused with the input argument
  
  stack = []
  for ix, val in np.ndenumerate(image):
    stack += [(val, ix)]
  
  stack.sort()

  for j in reversed(range(i, n)):
    while stack and stack[-1][0] >= poset[j]:
      ix = stack[-1][1]
      stack.pop()
      assert(arr[ix])
      if not visited[ix]:
        algos.bfs(ix, arr, visited)
        cc_in_image += 1
    res[j] = cc_in_image
    print(i,j,cc_in_image)
    
  return res


def get_ranks(image, poset):
  n = len(poset)
  ranks = np.zeros((n,n))
  for i in range(n):
    ranks_for_i = get_ranks_for_i(image, poset, i)
    for j in range(n):
      ranks[i,j] = ranks_for_i[j]
  return ranks
