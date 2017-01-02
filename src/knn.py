import find_closest
import utils


def simple_weight(position, dist):
  return 1.0 / position


def classify_knn(galaxy_diag, diag_dir, k=1, weight_fun=simple_weight):

  sum_all = 0.0
  sum_positives = 0.0

  candidates = find_closest.get_sorted_candidates(galaxy_diag, diag_dir)
  if k > 0:
    candidates = candidates[:k]
  for pos, (dist, diag_name) in enumerate(candidates, 1):
    weight = weight_fun(pos, dist)
    sum_all += weight
    cls = utils.get_class(diag_name)
    if cls == 1:
      sum_positives += weight
    else:
      assert(cls == 0)
  return sum_positives / sum_all
