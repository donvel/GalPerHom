import argparse
import glob
import utils

import bottleneck

HEAD_NUM = 10

def get_args():
  parser = argparse.ArgumentParser(description='Create persistence diagram')
  parser.add_argument('--galaxy-diag', dest='galaxy_diag', default='train/diags/galaxy.p')
  parser.add_argument('--dir', dest='dir', default='train/diags/')

  return parser.parse_args()



if __name__ == '__main__':
  args = get_args()
  print(args.galaxy_diag)
  target_diag = utils.read_diagram(args.galaxy_diag)
 
  candidates = []

  for fname in glob.glob('{}/*.p'.format(args.dir)):
    other_diag = utils.read_diagram(fname)
    candidates += [(bottleneck.get_distance(target_diag, other_diag), fname)]
  
  candidates.sort()

  for dist, name in candidates[:HEAD_NUM]:
    print(dist, name)
