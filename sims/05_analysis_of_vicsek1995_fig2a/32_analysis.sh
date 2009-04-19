#!/bin/sh

python complete_32_analysis.py 0 8 > 32_analysis0 &
python complete_32_analysis.py 1 8 > 32_analysis1 &
python complete_32_analysis.py 2 8 > 32_analysis2 &
python complete_32_analysis.py 3 8 > 32_analysis3 &
python complete_32_analysis.py 4 8 > 32_analysis4 &
python complete_32_analysis.py 5 8 > 32_analysis5 &
python complete_32_analysis.py 6 8 > 32_analysis6 &
python complete_32_analysis.py 7 8 > 32_analysis7 &

wait

cat 32_analysis0 32_analysis1 32_analysis2 32_analysis3 32_analysis4 32_analysis5 32_analysis6 32_analysis7 > 32_analysis.txt

