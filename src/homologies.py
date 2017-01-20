import numpy as np
from matplotlib import pyplot as plt

import utils
import algos

def get_ranks_for_i(image, poset, i):

  n = len(poset)
  res = np.zeros((n,))
  # print(poset[i])
  arr = utils.pixels_at_least(image, poset[i])
  visited = np.zeros_like(arr, dtype=int)
  
  # plt.figure()
  # plt.imshow(arr)

  # number of connected components (generators of 0-th homologies) of the i-th filtration
  # in image of the map induced by inclusion of the j-th filtration
  cc_in_image = 0
  
  stack = []
  for ix, val in np.ndenumerate(image):
    stack += [(val, ix)]
  
  # pixel with the largest value is at the top of the stack
  stack.sort() 

  for j in reversed(range(i, n)):
    while stack and stack[-1][0] >= poset[j]:
      ix = stack[-1][1]
      stack.pop()
      assert(arr[ix]) # sanity check that filtration_j is subset of filtration_i
      if not visited[ix]: # we add one more connected component (generator) contained in the
        # image of the induced map

        # this function marks the pixels of the component as visited
        algos.bfs(ix, arr, visited)
        cc_in_image += 1
    res[j] = cc_in_image
    # print(i,j,cc_in_image)
    
  return res


# get ranks of maps induced by respective inclusions of parts of 'image' filtered according
# to pixel values
# NOTE: this is in fact a reversed filtration i. e. we will consider the sets of pixels
# with filtration index >= some value (not <= some value).
def get_ranks(image, poset):
  n = len(poset)
  ranks = np.zeros((n,n))
  for i in range(n):
    # an optimization - ranks for the maps : filtration_j -> filtration_i can be computed
    # simultanously for all j > i
    ranks_for_i = get_ranks_for_i(image, poset, i)
    for j in range(n):
      ranks[i,j] = ranks_for_i[j]
  return ranks
