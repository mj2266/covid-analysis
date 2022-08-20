#!/bin/sh
./neighbor-districts-modified.sh
./edge-generator.sh
./case-generator.sh
./peaks-generator.sh
./vaccinated-count-generator.sh
./vaccination-population-ratio-generator.sh
./vaccine-type-ratio-generator.sh
./vaccinated-ratio-generator.sh
./complete-vaccination-generator.sh
echo "Completed, check the output folder"