
for type in radial level brightness
do
  mkdir -p train/diags/$type
  for image in train/img/*.jpg
  do
    bname=$(basename $image .jpg)
    pickle=train/diags/$type/$bname.p
    echo "python3 src/write_diagram.py --input-file $image --output-file $pickle"
  done
done
