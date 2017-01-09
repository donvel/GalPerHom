import argparse
import numpy as np
from matplotlib import pyplot as plt

import utils

def get_args():
  parser = argparse.ArgumentParser(description='Visualize threshold maps')
  parser.add_argument('--input-file', dest='input_file', default='train/img/galaxy_1_1000.jpg')
  parser.add_argument('--output-file', dest='output_file', default='train/maps/map.png')
  parser.add_argument('--threshold', dest='threshold', type=int, default=40)
  return parser.parse_args()


if __name__ == '__main__':
  args = get_args()
  
  
  image = utils.load_image(args.input_file)  

  galaxy_image = utils.extract_galaxy(image, args.threshold)

  plt.imshow(galaxy_image)
  plt.savefig(args.output_file) 
