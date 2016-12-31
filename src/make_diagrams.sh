for image in train/img/*.jpg
  do
    bname=$(basename $image .jpg)
    pickle=train/diags/$bname.p
    python3 src/write_diagram.py --input-file $image --output-file $pickle
  done
