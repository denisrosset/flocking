#!/bin/sh

python complete_33_analysis.py 0 8 > 33_analysis0 &
python complete_33_analysis.py 1 8 > 33_analysis1 &
python complete_33_analysis.py 2 8 > 33_analysis2 &
python complete_33_analysis.py 3 8 > 33_analysis3 &
python complete_33_analysis.py 4 8 > 33_analysis4 &
python complete_33_analysis.py 5 8 > 33_analysis5 &
python complete_33_analysis.py 6 8 > 33_analysis6 &
python complete_33_analysis.py 7 8 > 33_analysis7 &

wait

cat 33_analysis0 33_analysis1 33_analysis2 33_analysis3 33_analysis4 33_analysis5 33_analysis6 33_analysis7 > 33_analysis.txt

