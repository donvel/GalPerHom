import argparse
import csv
import os
import shutil


def get_args():
  parser = argparse.ArgumentParser(description='copy galaxy images to training directory')
  parser.add_argument('--chosen', dest='chosen_filename', default='chosen_1000_09.txt')
  parser.add_argument('--images-dir', dest='images_dir', default='kaggle/images_training_rev1')
  parser.add_argument('--output-dir', dest='output_dir', default='train/img')

  return parser.parse_args()


if __name__ == '__main__':

  args = get_args()

  with open(args.chosen_filename) as chosen_file:
    for it, line in enumerate(chosen_file, 1):
      gid, cl = line.split()
      print(gid, cl)
      os.makedirs(args.output_dir, exist_ok=True)
      shutil.copy("{}/{}.jpg".format(args.images_dir, gid),
                  "{}/galaxy_{}_{}.jpg".format(args.output_dir, cl, it))
