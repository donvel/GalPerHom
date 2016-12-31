import sys
import csv

if len(sys.argv) != 4:
  print("classification.csv probability_threshold no_of_samples")
  sys.exit()

class_filename = sys.argv[1]
prob_threshold = float(sys.argv[2])
assert prob_threshold > 0.5
samples_num = int(sys.argv[3])
assert samples_num > 0
chosen_gids = []


with open(class_filename) as class_file:
  class_csv = csv.reader(class_file)
  next(class_csv, None)  # skip the headers
  for row in class_csv:
    gid = row[0]
    probs = [float(p) for p in row[1:4]]
    for cl, prob in enumerate(probs):
      if prob > prob_threshold and cl != 2:
        chosen_gids += [(cl, gid)]
        break
    if len(chosen_gids) == samples_num:
      break

chosen_gids.sort()

for cl, gid in chosen_gids:
  print(gid, cl)
