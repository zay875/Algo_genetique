This folder contains the 32 problem instances generated for "Multi-Objective Sustainable Truck Scheduling in a Rail–Road Physical Internet Cross-Docking Hub Considering Energy Consumption". DOI: https://doi.org/10.3390/su11113127 

Each file contains the data for one instance. The files are named using the instances parameters as follows: Inst_"N"_"D"_"H".txt. Where N is the number of containers, D is the number of destinations and H is the number of available trucks. For instance, Inst_5_3_4.txt refers to the instance #20.

Each file is structured as follows:

///////////////////////////////////////////////////
// Inst_N_D_H
///////////////////////////////////////////////////

N	Total number of containers
K	Number of docks
D	Number of destinations
H	Total number of available trucks
Q	Truck's capacity

C_e	Energy cost for each PI-conveying unit
C_d	Vector containing the cost of using an outbound truck for each destination

I	Time to load one PI-container into the outbound trucks
Y	Vertical length of the Rail-Road section
V	Truck changeover time

L	Lengths of PI-containers
G	Destinations of PI-containers
P	Positions of the bottom left corner of the PI-containers in the wagons of the train
R	Positions of the outbound docks
