#!/bin/bash

# Loop through all .pkl files in the current directory
for file in *.pkl; do
  # Compress the file using gzip
  echo "Compressing $file..."
  gzip -9c < $file > $file.gz
done

echo "All *.pkl files compressed successfully!"
