import argparse
import glob

import utils
import knn

def get_args():
  parser = argparse.ArgumentParser(description='Classify using kNN')
  parser.add_argument('--diagrams-dir', dest='diag_dir', default='train/diags/')
  parser.add_argument('-k', dest='k', type=int, default=1)
  return parser.parse_args()


if __name__ == '__main__':
  args = get_args()

  conf_matrix = [[0, 0], [0, 0]]
  
  for fname in glob.glob('{}/*.p'.format(args.diag_dir)):
    prob_class_1 = knn.classify_knn(fname, args.diag_dir, k=args.k)
    pred_cls = 1 if prob_class_1 >= 0.5 else 0
    real_cls = utils.get_class(fname)
    conf_matrix[pred_cls][real_cls] += 1
    print("{}: pred={} real={}".format(utils.get_bname(fname), pred_cls, real_cls))

  print(conf_matrix)
  
  all_samples = sum(sum(row) for row in conf_matrix)
  accuracy = (conf_matrix[0][0] + conf_matrix[1][1]) / all_samples
  print(accuracy)
