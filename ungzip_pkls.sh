#!/bin/bash

# Loop through all .pkl files in the current directory
for file in *.gz; do
  # Compress the file using gzip
  echo "Decompressing $file..."
  gzip -dc < $file > ${file%.gz}
done

echo "All *.pkl files compressed successfully!"
