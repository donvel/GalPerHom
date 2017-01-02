import argparse
import numpy as np
from matplotlib import pyplot as plt
from ortools.graph import pywrapgraph

import utils



def get_args():
  parser = argparse.ArgumentParser(description='Create persistence diagram')
  parser.add_argument('--galaxy1', dest='galaxy1', default='train/diags/galaxy1.p')
  parser.add_argument('--galaxy2', dest='galaxy2', default='train/diags/galaxy2.p')

  return parser.parse_args()


def get_verts(diag):
   return [(ix, val.item()) for (ix, val) in np.ndenumerate(diag) if val > 0]


def dist_from_diag(p):
  return p[1] - p[0]


def dist(p1, p2):
  return 2 * max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))


def write_flow(solver, parts):
  num_to_vertex = parts[0] + parts[1] + ["d0"] + ["d1"]

  print(' Edge    Flow   Cost')
  for i in range(solver.NumArcs()):
    if solver.Flow(i) > 0:
      tail = num_to_vertex[solver.Tail(i)]
      head = num_to_vertex[solver.Head(i)]
      cost = solver.Flow(i) * solver.UnitCost(i)
      print('{} -> {}   {}    {}'.format(
          tail,
          head,
          solver.Flow(i),
          cost))


REMOVE_CLOSE_TO_DIAG = False

def remove_close_to_diag(diag):
  res = np.copy(diag)
  for ((x,y), val) in np.ndenumerate(diag):
    if x + 1 == y:
      res[x,y] = 0
  return res


def get_distance(diag1, diag2):
  diags = [diag1, diag2]
  if REMOVE_CLOSE_TO_DIAG:
    diags = [remove_close_to_diag(d) for d in diags]
  solver = pywrapgraph.SimpleMinCostFlow()

  parts = [get_verts(d) for d in diags]
  ns = [len(p) for p in parts]
  n = sum(ns)
  tot_vals = [sum(val for (_, val) in p) for p in parts]
  tot_val = sum(tot_vals)
  INF = tot_val + 1

  diags = [n, n + 1]
  
  solver.SetNodeSupply(diags[0], -tot_vals[0])
  solver.SetNodeSupply(diags[1], tot_vals[1])
  solver.AddArcWithCapacityAndUnitCost(diags[1], diags[0], INF, 0)
  
  for i, (ix, val) in enumerate(parts[0]):
    solver.SetNodeSupply(i, val)
    solver.AddArcWithCapacityAndUnitCost(i, diags[0], INF, dist_from_diag(ix))

  for j, (jx, val) in enumerate(parts[1], ns[0]):
    solver.SetNodeSupply(j, -val)
    solver.AddArcWithCapacityAndUnitCost(diags[1], j, INF, dist_from_diag(jx))
  
  for i, (ix, val) in enumerate(parts[0]):
    for j, (jx, val) in enumerate(parts[1], ns[0]):
      solver.AddArcWithCapacityAndUnitCost(i, j, INF, dist(ix, jx))
  

  assert (solver.Solve() == solver.OPTIMAL)

  # write_flow(solver, parts) 

  return solver.OptimalCost() / 2.0


if __name__ == '__main__':
  args = get_args()
  diags = [utils.read_diagram(fn) for fn in (args.galaxy1, args.galaxy2)]
  for d in diags:
    print(d)
  
  distance = get_distance(d[0], d[1])
  print(distance)
