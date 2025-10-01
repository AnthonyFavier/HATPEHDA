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

Easier to directly go in subfolder with `cd domains_and_results`

### Exploration

Run one of the problem file, e.g.
```
python3 stack_empiler_2.py
```

### Generate policy from explored search space
```
python3 choice_updater.py
```


### Visualize solution
```
python3 render.py
```

**Note**: May need to run `unset GTK_PATH` to render