import cv2
import pickle
import os
import numpy as np
from matplotlib import pyplot as plt

import algos
import homologies


ORIG_SIZE = 424
CROP_SIZE = 210
RES_SIZE = 70
CUT_MARGIN = (ORIG_SIZE - CROP_SIZE) // 2


def get_origin(image):
  return (image.shape[0] // 2, image.shape[1] // 2)


#def load_image(name, greyscale=True, rotate=False, threshold=None, extract=False):
def load_image(name, rotate=False, rescale=False, threshold=None, simple=False):
  image = cv2.imread(name)
  image_cropped = image[CUT_MARGIN:-CUT_MARGIN, CUT_MARGIN:-CUT_MARGIN]

  if simple:
    return image_cropped

  image_greyscale = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2GRAY)
  image_extracted = extract_galaxy(image_greyscale, threshold)

  if rotate:
    _, galaxy_map = cv2.threshold(image_extracted, threshold, 255, 0)
    _, contours, _ = cv2.findContours(galaxy_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    galaxy_contours = np.concatenate(contours)
    ellipse = cv2.fitEllipse(galaxy_contours)
    rot_mat = cv2.getRotationMatrix2D(ellipse[0],ellipse[2],1.0)

    # scale ellipse to circle
    if rescale:
      scale_factor = ellipse[1][1] / ellipse[1][0]
      assert(scale_factor >= 1.0)
      rot_mat[0, 0] = rot_mat[0, 0] * scale_factor
      rot_mat[0, 1] = rot_mat[0, 1] * scale_factor
      rot_mat[0, 2] = (rot_mat[0, 2] * scale_factor +
                       get_origin(image_extracted)[0] * (1.0 - scale_factor))
    image_rotated = cv2.warpAffine(image_extracted, rot_mat, image_extracted.shape,
                                   flags=cv2.INTER_LINEAR)

    image_resized = cv2.resize(image_rotated, (RES_SIZE, RES_SIZE), interpolation=cv2.INTER_AREA)

  else:
    image_resized = cv2.resize(image_extracted, (RES_SIZE, RES_SIZE), interpolation=cv2.INTER_AREA)

  return image_resized


def pixels_at_least(image, threshold): # more readable then cv2.threshold
  res = np.zeros_like(image, dtype=int)
  for ix, val in np.ndenumerate(image):
    if val >= threshold:
      res[ix] = 1
  return res


def extract_galaxy(image, threshold):
  res = np.copy(image)
  arr = pixels_at_least(image, threshold)
  visited = np.zeros_like(image, dtype=int)
  algos.bfs(get_origin(image), arr, visited)
  for ix, val in np.ndenumerate(visited):
    if val == 0:
      res[ix] = 0
  return res


def distance(p1, p2):
  return np.linalg.norm(np.array(p1) - np.array(p2))


def make_generic_map(image, function):
  res = np.zeros_like(image, dtype=float)
  for ix, val in np.ndenumerate(image):
    if val > 0:
       res[ix] = function(ix, val)
  return res


def make_radial_map(image):
  def fun(ix, _):
    return distance(get_origin(image), ix)
  return make_generic_map(image, fun)


def make_coord_map(image, coord=0):
  def fun(ix, _):
    return ix[coord]
  return make_generic_map(image, fun)


def make_brightness_map(image):
  def fun(_, val):
    return val
  return make_generic_map(image, fun)


def create_poset(min_value, max_value, length):
  assert(min_value < max_value)
  assert(length > 1)
  step = (max_value - min_value) / (length - 1)
  return [min_value + i * step for i in range(length)]


def get_diagram(image, poset):
  ranks = homologies.get_ranks(image, poset)
  n = len(poset)
  diagram = np.zeros((n, n), dtype=int)

  for i in range(0, n):
    for j in range(i + 1, n):
      diagram[i,j] = ranks[i,j-1] - ranks[i,j]
      if i > 0:
        diagram[i,j] += ranks[i-1,j] - ranks[i-1,j-1]

  return diagram


def write_diagram(diag, poset, _per_type, output_file):
  pickle.dump((diag, poset), open(output_file, "wb"))


def read_diagram(input_file):
  diag, _ = pickle.load(open(input_file, "rb"))
  return diag


def get_bname(path):
  return os.path.splitext(os.path.basename(path))[0]


def get_class(diag_name):
  bname = get_bname(diag_name)
  return int(bname.split('_')[1])
