import sys
import csv
import shutil

if len(sys.argv) != 4:
  print("chosen.txt images_dir output_dir")
  sys.exit()

chosen_filename = sys.argv[1]
images_dir = sys.argv[2]
out_dir = sys.argv[3]

with open(chosen_filename) as chosen_file:
  for it, line in enumerate(chosen_file, 1):
    gid, cl = line.split()
    print(gid, cl)
    shutil.copy("{}/{}.jpg".format(images_dir, gid), "{}/galaxy_{}_{}.jpg".format(out_dir, cl, it))
