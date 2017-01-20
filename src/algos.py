# TODO change it if we want to have an option of choosing a right nieghbor definition
OFFSETS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0)]


def in_range(p, arr):
  return p[0] >= 0 and p[0] < arr.shape[0] and p[1] >= 0 and p[1] < arr.shape[1]


def pt_sum(p1, p2):
  return (p1[0] + p2[0], p1[1] + p2[1])


def neighbors(pt, arr):
  ns = [pt_sum(pt, off) for off in OFFSETS if in_range(pt_sum(pt, off), arr)]
  return ns


# we pass the 'visited' array
# it is sometimes helpful to have it partially filled with 1s already
# the only effect of this function is filling it with addiotional 1s
def bfs(start, arr, visited):
  visited[start] = 1
  qu = [start]
  while qu:
    nqu = []
    ns = [n for el in qu for n in neighbors(el, arr)]
    for n in ns:
      if not visited[n] and arr[n]:
        nqu += [n]
        visited[n] = 1
    qu = nqu


