#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Visualize MD trajectories using Pymol and Bokeh """

from __future__ import print_function

import os
import random
import argparse
import warnings
import subprocess
import numpy as np

from xmlrpclib import ServerProxy
from MDAnalysis import Universe
from bokeh.client import push_session
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import output_server, figure, curdoc
from matplotlib.cm import get_cmap
from matplotlib import colors

warnings.filterwarnings("ignore")

__author__ = "Jérôme Eberhardt"
__copyright__ = "Copyright 2016, Jérôme Eberhardt"

__lience__ = "MIT"
__maintainer__ = "Jérôme Eberhardt"
__email__ = "qksoneo@gmail.com"


class Visualize():

    def __init__(self, top_file, dcd_files, config_file):

        # Start Bokeh server
        if not self.is_screen_running("visu_bokeh"):
            print("Error: Bokeh is not running")
            sys.exit(1)

        # Start PyMOL
        if not self.is_screen_running("visu_pymol"):
            print("Error: Pymol is not running")
            sys.exit(1)

        # Open DCD trajectory
        self.u = Universe(top_file, dcd_files)

        # Read configuration file
        self.comments = self.read_comments(config_file)
        self.coord, self.frames, self.energy = self.read_configuration(config_file)

    def is_screen_running(self, sname):
        output = subprocess.check_output(["screen -ls; true"], shell=True)
        return [l for l in output.split("\n") if sname in l]

    def read_configuration(self, config_file):
        """
        Read configuration file
        """
        coord = None
        frames = None
        energy = None

        data = np.loadtxt(config_file)

        if data.shape[1] == 2:
            coord = np.fliplr(data[:, 0:])
            frames = np.arange(0, coord.shape[0])
            energy = None
        elif data.shape[1] == 3:
            coord = np.fliplr(data[:, 1:])
            frames = data[:, 0]
            energy = None
        elif data.shape[1] == 4:
            coord = np.fliplr(data[:, 1:3])
            frames = data[:, 0]
            energy = data[:, 3]
        else:
            print("Error: Cannot read coordinates file! (#Columns: %s)" % data.shape[1])
            sys.exit(1)

        return coord, frames, energy

    def read_comments(self, fname, comments="#"):
        with open(fname) as f:
            for line in f:
                if comments in line:
                    line = line.replace("%s " % comments, "")
                    return {pname: pvalue for pname, pvalue in zip(line.split(" ")[::2], line.split(" ")[1::2])}

            return None

    def update_pymol(self, indices):

        rpc_port = 9123

        if indices:

            frames = []

            for indice in indices:
                i, j = self.id_to_H_frame[indice]
                frames = np.concatenate((frames, np.trim_zeros(self.H_frame[i, j], "b")))

            nb_frames = frames.shape[0]

            if nb_frames > self.max_frame:
                print("Too much frames (%s). So we choose %s structures randomly." % (self.max_frame, nb_frames))
                frames = random.sample(frames, self.max_frame)

            try:
                pymol = ServerProxy(uri="http://localhost:%s/RPC2" % rpc_port)

                pymol.do("delete s*")

                for frame in frames:

                    frame = np.int(frame)

                    # Go to the frame
                    self.u.trajectory[frame]

                    # Write the PDB file
                    self.u.atoms.write("structure.pdb")

                    try:
                        pymol.load("%s/structure.pdb" % os.getcwd())
                    except:
                        print("Can\"t load PDB structure !")
                        pass

                    if self.cartoon:
                        pymol.show("cartoon")
                    else:
                        pymol.show("ribbon")

                    pymol.hide("lines")
                    pymol.do("copy s%s, structure" % frame)
                    pymol.delete("structure")
                    pymol.do("show sticks, organic")

                    if np.int(frames[0]) != frame and nb_frames > 1:
                        pymol.do("align s%d, s%d" % (frame, frames[0]))

                pymol.do("center %s" % frame)
            except:
                print("Connection issue with PyMol! (Cmd: pymol -R)")

    def get_selected_frames(self, attr, old, new):
        self.update_pymol(new["1d"]["indices"])

    def generate_color(sefl, value, cmap):
        return colors.rgb2hex(get_cmap(cmap)(value))

    def assignbins2D(self, coordinates, bin_size):

        x_min, x_max = np.min(coordinates[:, 0]), np.max(coordinates[:, 0])
        y_min, y_max = np.min(coordinates[:, 1]), np.max(coordinates[:, 1])

        x_length = (x_max - x_min)
        y_length = (y_max - y_min)

        x_center = x_min + (x_length/2)
        y_center = y_min + (y_length/2)

        if x_length > y_length:
            x_limit = np.array([x_center-(x_length/2)-0.5, x_center+(x_length/2)+0.5])
            y_limit = np.array([y_center-(x_length/2)-0.5, y_center+(x_length/2)+0.5])
        else:
            x_limit = np.array([x_center-(y_length/2)-0.5, x_center+(y_length/2)+0.5])
            y_limit = np.array([y_center-(y_length/2)-0.5, y_center+(y_length/2)+0.5])

        x_bins = np.arange(float(x_limit[0]), (float(x_limit[1]) + bin_size), bin_size)
        y_bins = np.arange(float(y_limit[0]), (float(y_limit[1]) + bin_size), bin_size)

        return x_bins, y_bins

    def show(self, bin_size=0.025, min_bin=0, max_frame=25, cartoon=False):

        # Store some informations
        self.bin_size = bin_size
        self.min_bin = min_bin
        self.max_frame = max_frame
        self.cartoon = cartoon
        self.H_frame = None
        self.id_to_H_frame = []

        title = ""
        xx, yy = [], []
        count, color, e = [], [], []

        # Get edges
        edges_x, edges_y = self.assignbins2D(self.coord, bin_size)

        # Get 2D histogram, just to have the number of conformation per bin
        H, edges_x, edges_y = np.histogram2d(self.coord[:, 0], self.coord[:, 1], bins=(edges_x, edges_y))
        # ... and replace all zeros by nan
        H[H == 0.] = np.nan

        # Initialize histogram array and frame array
        tmp = np.zeros(shape=(edges_x.shape[0], edges_y.shape[0], 1), dtype=np.int32)
        self.H_frame = np.zeros(shape=(edges_x.shape[0], edges_y.shape[0], np.int(np.nanmax(H))+10), dtype=np.int32)

        if self.energy is not None:
            H_energy = np.empty(shape=(edges_x.shape[0], edges_y.shape[0], np.int(np.nanmax(H))+10))
            H_energy.fill(np.nan)

        # For each coordinate, we put them in the right bin and add the frame number
        for i in xrange(0, self.frames.shape[0]):
            ix = np.int((self.coord[i, 0] - edges_x[0]) / bin_size)
            iy = np.int((self.coord[i, 1] - edges_y[0]) / bin_size)

            # Put frame numbers in a histogram too
            self.H_frame[ix, iy, tmp[ix, iy]] = self.frames[i]

            # The same for the energy, if we provide them
            if self.energy is not None:
                H_energy[ix, iy, tmp[ix, iy]] = self.energy[i]

            # Add 1 to the corresponding bin
            tmp[ix, iy] += 1

        if self.energy is not None:
            # get mean energy per bin
            H_energy = np.nanmean(H_energy, axis=2)

        # Get STD and MEAN conformations/energy
        if self.energy is not None:
            std = np.nanstd(H_energy)
            mean = np.nanmean(H_energy)
        else:
            std = np.int(np.nanstd(H))
            mean = np.int(np.nanmean(H))

        # Get min_hist and max_hist
        min_hist = mean - std
        max_hist = mean + std
        # Put min_hist equal to min_bin is lower than 0
        min_hist = min_hist if min_hist > 0 else min_bin

        unit = '#conf.' if self.energy is None else 'Kcal/mol'
        print("Min: %8.2f Max: %8.2f (%s)" % (min_hist, max_hist, unit))

        # Add we keep only the bin with structure
        for i in xrange(0, H.shape[0]):
            for j in xrange(0, H.shape[1]):

                if H[i, j] > min_bin:
                    xx.append(edges_x[i])
                    yy.append(edges_y[j])
                    self.id_to_H_frame.append((i, j))
                    count.append(H[i, j])

                    if self.energy is None:
                        value = 1. - (np.float(H[i, j]) - min_hist) / (max_hist - min_hist)
                    else:
                        value = (np.float(H_energy[i, j]) - min_hist) / (max_hist - min_hist)
                        e.append(H_energy[i, j])

                    color.append(self.generate_color(value, "jet"))

        TOOLS = "wheel_zoom,box_zoom,undo,redo,box_select,save,resize,reset,hover,crosshair,tap,pan"

        # Create the title with all the parameters contain in the file
        if self.comments:
            for key, value in self.comments.iteritems():
                title += "%s: %s " % (key, value)
        else:
            title = "#conformations: %s" % self.frames.shape[0]

        p = figure(plot_width=850, plot_height=850, tools=TOOLS, title=title,
                   webgl=True, title_text_font_size="12pt")

        # Create source
        source = ColumnDataSource(data={"xx": xx, "yy": yy, "count": count})
        if self.energy is not None:
            source.add(e, name="energy")

        # Create histogram
        p.rect("xx", "yy", width=bin_size, height=bin_size, color=color,
               line_alpha=color, line_color="black", source=source)

        # Create Hovertools
        tooltips = [("(X, Y)", "(@xx @yy)"), ("#Frames", "@count")]
        if self.energy is not None:
            tooltips += [("Energy (Kcal/mol)", "@energy")]

        hover = p.select({"type": HoverTool})
        hover.tooltips = tooltips

        output_server("visualize")

        # open a session to keep our local document in sync with server
        session = push_session(curdoc())
        # Update data when we select conformations
        source.on_change("selected", self.get_selected_frames)
        # Open the document in a browser
        session.show(p)
        # Run forever !!
        session.loop_until_closed()


def parse_options():
    parser = argparse.ArgumentParser(description="visu 2D configuration")
    parser.add_argument("-t", "--top", dest="top_file", required=True,
                        action="store", type=str,
                        help="psf or pdb file used for simulation")
    parser.add_argument("-d", "--dcd", dest="dcd_files", required=True,
                        action="store", type=str, nargs="+",
                        help="list of dcd files")
    parser.add_argument("-c", "--configuration", dest="config_file",
                        required=True, action="store", type=str,
                        help="configuration file")
    parser.add_argument("-b", "--bin", dest="bin_size", default=0.025,
                        action="store", type=float,
                        help="bin size of the histogram")
    parser.add_argument("--max-frame", dest="max_frame", default=25,
                        action="store", type=int,
                        help="maximum number of randomly picked frames")
    parser.add_argument("--min-bin", dest="min_bin", default=0,
                        action="store", type=int,
                        help="minimal number of frames needed to show the bin")
    parser.add_argument("--cartoon", dest="cartoon", default=False,
                        action="store_true",
                        help="Turn on cartoon representation in PyMOL")

    args = parser.parse_args()

    return args


def main():

    options = parse_options()

    top_file = options.top_file
    dcd_files = options.dcd_files
    config_file = options.config_file
    bin_size = options.bin_size
    cartoon = options.cartoon
    max_frame = options.max_frame
    min_bin = options.min_bin

    V = Visualize(top_file, dcd_files, config_file)
    V.show(bin_size, min_bin, max_frame, cartoon)

if __name__ == "__main__":
    main()
