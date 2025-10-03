# Installation

## Install dependencies

```
sudo apt install graphviz libcanberra-gtk-module
```

## Setup a virtual python environement

```
python3 -m venv venv
pip install --upgrade pip -r requirements.txt --no-cache-dir
```



## Planning

Directly run one of the domain in root folder: [`cooking_pasta.py`, `box_prepare.py`, `car_maintenance`]. 

```
python3 coooking_pasta.py 0 
python3 coooking_pasta.py 0 --without_delay
python3 coooking_pasta.py 5
```

Each domain file takes as arguments an ID of initial state. Look into init_domain(n) to see which initial state correspond to which ID

## See plans

Produced plans are shown in the shell but for more legibility an image graph is generated in `domains_and_results/results/runs/<name_of_run>.png`

## Several runs

You can you the `test_runner.py` script to run each file or even run all problems of a domain.

Run the following for help:
```
python3 test_runner.py --help
```


All results are stored in domains_and_results/results/. A full log report is stored as "run.txt" and all runs are stored in domains_and_results/results/runs/. Each run has a picture of the solution tree and its associated text log file.
