import cv2
import pickle
import os
import numpy as np
from matplotlib import pyplot as plt

import algos
import homologies

# TODO this must be changed if we want to use different datasets
ORIG_SIZE = 424
CROP_SIZE = 210
RES_SIZE = 70
CUT_MARGIN = (ORIG_SIZE - CROP_SIZE) // 2


def get_center(image):
  return (image.shape[0] // 2, image.shape[1] // 2)


#def load_image(name, greyscale=True, rotate=False, threshold=None, extract=False):
def load_image(name, rotate=False, rescale=False, threshold=None, simple=False):
  image = cv2.imread(name)
  image_cropped = image[CUT_MARGIN:-CUT_MARGIN, CUT_MARGIN:-CUT_MARGIN]

  if simple:
    # do nothing
    return image_cropped

  image_greyscale = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2GRAY)

  # choose the pixels belonging to the galaxy
  image_extracted = extract_galaxy(image_greyscale, threshold)

  if rotate:
    # BW map needed for findContours...
    _, galaxy_map = cv2.threshold(image_extracted, threshold, 255, 0)
    # contours needed for fitEllipse
    _, contours, _ = cv2.findContours(galaxy_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    galaxy_contours = np.concatenate(contours)
    # ellipse = (center, (minor axis length, major axis length), rotation)
    ellipse = cv2.fitEllipse(galaxy_contours)
    rot_mat = cv2.getRotationMatrix2D(ellipse[0],ellipse[2],1.0)

    # scale the image after rotationg, so that its width equals its height
    # it is perhaps more elegant to modify the rot_mat then to apply second transformation
    if rescale:
      scale_factor = ellipse[1][1] / ellipse[1][0]
      assert(scale_factor >= 1.0) # sanity check that OpenCV does its job
      rot_mat[0, 0] = rot_mat[0, 0] * scale_factor
      rot_mat[0, 1] = rot_mat[0, 1] * scale_factor
      rot_mat[0, 2] = (rot_mat[0, 2] * scale_factor +
                       get_center(image_extracted)[0] * (1.0 - scale_factor))
    image_rotated = cv2.warpAffine(image_extracted, rot_mat, image_extracted.shape,
                                   flags=cv2.INTER_LINEAR)

    image_resized = cv2.resize(image_rotated, (RES_SIZE, RES_SIZE), interpolation=cv2.INTER_AREA)

  else:
    # only resize
    image_resized = cv2.resize(image_extracted, (RES_SIZE, RES_SIZE), interpolation=cv2.INTER_AREA)

  return image_resized


# return a 0/1 map (same shape as 'image') indicating, which pixels have value at least 'threshold'
def pixels_at_least(image, threshold): # more readable then cv2.threshold
  res = np.zeros_like(image, dtype=int)
  for ix, val in np.ndenumerate(image):
    if val >= threshold:
      res[ix] = 1
  return res


# discard pixels with brightness below 'threshold' and keep only the connected component of the
# image's center
def extract_galaxy(image, threshold):
  res = np.copy(image)
  arr = pixels_at_least(image, threshold)
  visited = np.zeros_like(image, dtype=int)
  algos.bfs(get_center(image), arr, visited)
  for ix, val in np.ndenumerate(visited):
    if val == 0:
      res[ix] = 0
  return res


def distance(p1, p2):
  return np.linalg.norm(np.array(p1) - np.array(p2))


# make a generic filtration map of 'image' according to some 'function'
# NOTE: this is in fact a reversed filtration i. e. we will consider the sets of pixels
# with filtration index >= some value (not <= some value).
def make_generic_map(image, function):
  res = np.zeros_like(image, dtype=float)
  for ix, val in np.ndenumerate(image):
    if val > 0:
       res[ix] = function(ix, val)
  return res


# filtration = distance from center
def make_radial_map(image):
  def fun(ix, _):
    return distance(get_center(image), ix)
  return make_generic_map(image, fun)


# filtration = first coordinate (by default)
def make_coord_map(image, coord=0):
  def fun(ix, _):
    return ix[coord]
  return make_generic_map(image, fun)


# filtration = brightness
def make_brightness_map(image):
  def fun(_, val):
    return val
  return make_generic_map(image, fun)


# create a sequence of  equidistant numbers of length 'length'
def create_poset(min_value, max_value, length):
  assert(min_value < max_value)
  assert(length > 1)
  step = (max_value - min_value) / (length - 1)
  return [min_value + i * step for i in range(length)]


# create a persistance diagram for given 'image' (with filtration values) and poset
def get_diagram(image, poset):
  # ranks = ranks of maps induced by respective inclusions
  ranks = homologies.get_ranks(image, poset)
  n = len(poset)
  diagram = np.zeros((n, n), dtype=int)

  for i in range(0, n):
    for j in range(i + 1, n):
      # TODO this formula creates diagrams affected even by generators living only one 'moment'
      # these are the entries just above the diagonal
      # does it mean that it is messed up some +/-1 ?
      # I added an option to ignore these entries, it does not increase the efficiency, though
      diagram[i,j] = ranks[i,j-1] - ranks[i,j]
      if i > 0:
        diagram[i,j] += ranks[i-1,j] - ranks[i-1,j-1]

  return diagram


# write a pickle of a (diag, poset) pair. Later we use only the diag part, but why not save both
def write_diagram(diag, poset, _per_type, output_file):
  pickle.dump((diag, poset), open(output_file, "wb"))


# retrieve a diagram from a pickle dump
def read_diagram(input_file):
  diag, _ = pickle.load(open(input_file, "rb"))
  return diag


def get_bname(path):
  return os.path.splitext(os.path.basename(path))[0]


# with the current naming convention this checks whether the galaxy is
# 'smooth' (0) or 'not smooth' (1)
def get_class(diag_name):
  bname = get_bname(diag_name)
  return int(bname.split('_')[1])
