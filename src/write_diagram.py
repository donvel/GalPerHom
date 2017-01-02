import argparse
import numpy as np
from matplotlib import pyplot as plt

import utils

def get_args():
  parser = argparse.ArgumentParser(description='Create persistence diagram')
  parser.add_argument('--input-file', dest='input_file', default='train/img/galaxy.jpg')
  parser.add_argument('--output-file', dest='output_file', default='train/diags/galaxy.p')
  parser.add_argument('--threshold', dest='threshold', type=int, default=40)
  parser.add_argument('--module-length', dest='length', type=int, default=10)
  parser.add_argument('--type', dest='type', default="radial")
  parser.add_argument('--show-figure', dest='show', action='store_true')
  return parser.parse_args()




if __name__ == '__main__':
  args = get_args()
  
  def show(img):
    if args.show:
      plt.figure()
      plt.imshow(img)
  
  image = utils.load_image(args.input_file)  
  show(image)

  galaxy_image = utils.extract_galaxy(image, args.threshold)
  show(galaxy_image)
 
  # galaxy_map = utils.pixels_at_least(galaxy_image, args.threshold)

  value_funs = {"radial": utils.make_radial_map,
                "level": utils.make_coord_map,
                "brightness": utils.make_brightness_map}

  value_map = value_funs[args.type](galaxy_image)
  show(value_map)

  poset = utils.create_poset(0, np.amax(value_map), args.length)
  per_diag = utils.get_diagram(value_map, poset)
  print(per_diag)

  utils.write_diagram(per_diag, poset, args.type, args.output_file)

  if args.show:
    plt.show()
