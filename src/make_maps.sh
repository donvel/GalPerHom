mkdir -p train/maps
for image in train/img/*.jpg
do
  bname=$(basename $image .jpg)
  outfile=train/maps/$bname.png
  python3 src/write_map.py --input-file $image --output-file $outfile
done
