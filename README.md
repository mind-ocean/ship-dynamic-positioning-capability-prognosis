# ship-dynamic-positioning-capability-prognosis
This script allows for DP prognosis with DNV-ST-0111 level 1

The script is initiated from main.py, the ship input data are determined there at the beginning of the script.
The description of each variable is given in the docs folder in the DNV-ST-0111 standard and in the dissertation that is also provided there.
The script is only a part of the PHD that covers a subject of prognosis with all DNV levels esspecially the DP simulation.
The docs folder also contains the publication on the subject of thrust allocation applied in the script.


The rest of the .py files contain classes and functions that are called in main.py

The input data (in main) concerinig thrusters are specific and some of them are not arbitrary. All choices are available in thruster_loop.py

The results are fonunt in the RESULTS folder. Some examples are already given there.

Python version supporting the scrip is 3.8.12

The list of libraries and their version is given in file dp_libraries.txt

The script is engineered without code optimization or common programming practicies. It may be developed further or used as it is. 
The functionality is correct and results validated. The performance in sense of calcualtion time is few seconds.

