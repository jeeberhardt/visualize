# MD visualizer
Visualization and exploration of MD trajectories using Bokeh and PyMOL

## Prerequisites

You need, at a minimum (requirements):

* Python 2.7 (only for the moment)
* NumPy
* Bokeh
* MDAnalysis
* xmlrpclib
* PyMOL

And *screen* unix command.

## Installation

I highly recommand you to install the Anaconda distribution (https://www.continuum.io/downloads) if you want a clean python environnment with nearly all the prerequisites already installed (NumPy, Bokeh).

For the rest, you just have to do this.
```bash
pip install xmlrpclib mdanalysis
```

## PyMOL issue

For some reasons I cannot explain (for now), PyMOL doesn't work with the Anaconda distribution. So I will recommand you to install PyMOL using the python already installed on your Pc (Ubuntu/Debian or MacOS).

**If you already installed Anaconda**, you need to modify the PATH environment variable.

```bash
echo $PATH
```

You should have something like that if you have Anaconda properly installed:
```bash
/home/eberhardt/Applications/anaconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
```

Set the new PATH without Anaconda (**It's an example!**):
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
```

Download PyMOL (https://sourceforge.net/projects/pymol) and install it.

```bash
python setup.py build install
```

## How-To

1 . First, you need to start Bokeh and PyMOL.
```bash
python run_servers.py #(Yep, that's all)
```

2 . Now, it's time to explore your MD trajectory!
```bash
python visualize.py -t topology.psf -d traj.dcd -c coordinates_2d.txt
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

It's a simple txt file with 2, 3 or 4 columns:
 * 2 columns: [X Y]
 * 3 columns: [frame_idx X Y]
 * 4 columns: [frame_idx X Y energy]

## Citation
Soon ...

## License
MIT
