[![DOI](https://zenodo.org/badge/59821258.svg)](https://zenodo.org/badge/latestdoi/59821258)

# Visualize
Visualization and exploration tool for MD trajectories using Bokeh and PyMOL

![Visualize demo](http://i.imgur.com/8te1x4J.gif)

## Prerequisites

You need, at a minimum (requirements):

* Python 2.7 (only for the moment)
* NumPy
* Bokeh (=0.12.10)
* MDAnalysis
* xmlrpclib
* PyMOL

And *screen* unix command.

## Installation

I highly recommand you to install the Anaconda distribution (https://www.continuum.io/downloads) if you want a clean python environnment with nearly all the prerequisites already installed (NumPy, Bokeh).

For the rest, you just have to do this.
```bash
pip install xmlrpclib 

conda config --append channels conda-forge
conda install mdanalysis

conda install -c schrodinger pymol
```

## How-To

1 . First, you need to start Bokeh and PyMOL.
```bash
python run_servers.py #(Yep, that's all)
```

2 . Now, it's time to explore your MD trajectory!
```bash
python visualize.py -t topology.psf -d traj.dcd -c coordinates_2d.csv
``` 

**Command line options**
* -t/--top: topology file (psf, pdb)
* -d/--dcd: single trajectory or list of trajectories (dcd, xtc)
* -c/--configuration: 2D coordinates obtained using your favorite dimensional reduction method (like SPE ?)
* -b/--bin: size of the histogram's bin (default: 0.025)
* --max-frame: maximum number of randomly picked frames (default: 25)
* --min-bin: minimal number of frames needed to show the bin (default: 0)
* --cartoon: Turn on cartoon representation in PyMOL (default: False)

**Coordinates file format**

It's a simple csv file with 2, 3 or 4 columns:
 * 2 columns: [X,Y]
 * 3 columns: [frame_idx,X,Y]
 * 4 columns: [frame_idx,X,Y,energy]

## Citation
1. Jérôme Eberhardt. (2017, February 2). jeeberhardt/visualize. Zenodo. http://doi.org/10.5281/zenodo.268039

## License
MIT
