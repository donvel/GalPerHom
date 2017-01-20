"""
Create persistence diagram for a given image and argument set
"""
import argparse
import numpy as np
from matplotlib import pyplot as plt

import utils

def get_args():
  parser = argparse.ArgumentParser(description='Create persistence diagram')
  parser.add_argument('--input-file', dest='input_file', default='train/img/galaxy_1_1000.jpg',
                      help="input image")
  parser.add_argument('--output-file', dest='output_file', default='galaxy.p',
                      help="output file with persistency diagram (pickled Python object)")
  parser.add_argument('--threshold', dest='threshold', type=int, default=30,
                      help="brightness threshold used to extract the galaxy pixels")
  parser.add_argument('--module-length', dest='length', type=int, default=10)
  parser.add_argument('--type', dest='type', default="radial",
                      help="choose from radial, level (x coordinate), brightness")
  parser.add_argument('--show-figure', dest='show', action='store_true',
                      help="show galaxy image with filters applied")
  parser.add_argument('--rotate-image', dest='rotate', action='store_true',
                      help="normalize rotation")
  parser.add_argument('--rescale-image', dest='rescale', action='store_true',
                      help="must be used with --rotate, scale along y-axis so that W = H")
  return parser.parse_args()



if __name__ == '__main__':
  args = get_args()

  def show(img):
    if args.show:
      plt.figure()
      plt.imshow(img)

  # loads the preprocessed galaxy image
  galaxy_image = utils.load_image(args.input_file, rotate=args.rotate,
                                  rescale=args.rescale, threshold=args.threshold)
  show(galaxy_image)

  # choose the function used for filtration
  value_funs = {"radial": utils.make_radial_map,
                "level": utils.make_coord_map,
                "brightness": utils.make_brightness_map}

  # value_map is an image with filtration level stored at pixel's coords
  value_map = value_funs[args.type](galaxy_image)
  show(value_map)

  # TODO maybe np.amin(value_map) would be better than 0, but some functions may assume
  # that the values are >= 0
  # poset = finite subset of R used to index the vector spaces in the persistence module
  poset = utils.create_poset(0, np.amax(value_map), args.length)

  # get persistence diagram for the given value_map and poset
  per_diag = utils.get_diagram(value_map, poset)
  print(per_diag)

  # save diagram to a file
  utils.write_diagram(per_diag, poset, args.type, args.output_file)

  if args.show:
    plt.show()
