import argparse
import csv

def get_args():
  parser = argparse.ArgumentParser(description='choose galaxies for the training set and write \
                                   their names to --output-file')
  parser.add_argument('--class', dest='class_filename', default='kaggle/training_solutions_rev1.csv')
  parser.add_argument('--output-file', dest='output_filename', default='chosen_1000_09.txt')
  parser.add_argument('--threshold', dest='prob_threshold', type=float, default=0.9,
                      help="Choose only galaxies classified with probability above --threshold")
  parser.add_argument('--samples', dest='samples_num', type=int, default=1000)
  parser.add_argument('--preserve-ratio', dest='preserve_ratio', action='store_true',
                      help="If this option is set, exactly half of galaxies in each class is chosen")

  return parser.parse_args()

if __name__ == '__main__':

  args = get_args()
  
  assert(args.prob_threshold > 0.5)
  assert(args.samples_num > 0)
  chosen_gids = []

  if not args.preserve_ratio:
    half = args.samples_num // 2
    target_nums = (half, args.samples_num - half)
  class_nums = [0, 0]

  with open(args.class_filename) as class_file:
    class_csv = csv.reader(class_file)
    next(class_csv, None)  # skip the headers
    for row in class_csv:
      gid = row[0]
      probs = [float(p) for p in row[1:3]]
      for cl, prob in enumerate(probs):
        if (prob > args.prob_threshold and
            (args.preserve_ratio or class_nums[cl-1] < target_nums[cl-1])):
          chosen_gids += [(cl, gid)]
          class_nums[cl-1] += 1
      if len(chosen_gids) == args.samples_num:
        break

  chosen_gids.sort()

  with open(args.output_filename, 'w') as output_file:
    for cl, gid in chosen_gids:
      print(gid, cl, file=output_file)
