# MD visualizer
Visualization and exploration of MD trajectories using Bokeh and PyMOL

## Prerequisites

You need, at a minimum:

* Python 2.7 or later
* NumPy
* Bokeh
* MDAnalysis
* xmlrpclib
* PyMOL

## Installation

I highly recommand you to install the Anaconda distribution (https://www.continuum.io/downloads) if you want a clean python environnment with nearly all the prerequisites already installed (NumPy, Bokeh).

For the rest, you just have to do this,
```bash
pip install xmlrpclib mdanalysis
```

## PyMOL issue

For some reasons I cannot explain (for now), pymol doesn't work with the Anaconda distribution. So I will recommand you to install PyMOL using the python already installed on your Pc (Ubuntu/Debian or MacOS).

## How-To

1 . First, you need to start Bokeh and PyMOL
```bash
python run_servers.py (Yep, that's all)
```

2 . Now, this is time to explore your MD trajectory
```bash
python visualize.py -t topology.psf -d traj.dcd -c coordinates_2d.txt
``` 

**Command line options**
* -t/--top: topology file (psf, pdb)
* -d/--dcd: single trajectory or list of trajectories (dcd, xtc)
* -c/--configuration: 2D coordinates obtained using your favorite dimensional reduction method (like SPE ?)