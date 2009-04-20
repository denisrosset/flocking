#!/bin/sh

python complete_31_analysis.py 0 8 > 31_analysis0 &
python complete_31_analysis.py 1 8 > 31_analysis1 &
python complete_31_analysis.py 2 8 > 31_analysis2 &
python complete_31_analysis.py 3 8 > 31_analysis3 &
python complete_31_analysis.py 4 8 > 31_analysis4 &
python complete_31_analysis.py 5 8 > 31_analysis5 &
python complete_31_analysis.py 6 8 > 31_analysis6 &
python complete_31_analysis.py 7 8 > 31_analysis7 &

wait

cat 31_analysis0 31_analysis1 31_analysis2 31_analysis3 31_analysis4 31_analysis5 31_analysis6 31_analysis7 > 31_analysis.txt
