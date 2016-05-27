#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import random
import argparse
import subprocess
import numpy as np

from xmlrpclib import ServerProxy
from MDAnalysis import Universe
from bokeh.client import push_session
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import output_server, figure, curdoc

def is_screen_running(sname):
    output = subprocess.check_output(["screen -ls; true"], shell=True)
    return [l for l in output.split('\n') if sname in l]

def update_pymol(indices):

    max_frames = 25
    rpc_port = 9123
    
    if indices:

        frames = []

        for indice in indices:
            i, j = id_to_H_frame[indice]
            frames = np.concatenate((frames, np.trim_zeros(H_frame[i,j], 'b')))

        nb_frames = frames.shape[0]

        if nb_frames > max_frames:
            print('Too much frames (%s). So we choose %s structures randomly.' % (max_frames, nb_frames))
            frames = random.sample(frames, max_frames)

        try:
            pymol = ServerProxy(uri="http://localhost:%s/RPC2" % rpc_port)

            pymol.do('delete s*')

            for frame in frames:

                frame = np.int(frame)

                # Go to the frame
                u.trajectory[frame]

                # Write the PDB file
                u.atoms.write("structure.pdb")

                try:
                    pymol.load('%s/structure.pdb' % os.getcwd())
                except:
                    print('Can\'t load PDB structure !')
                    pass

                pymol.show("ribbon")
                pymol.hide("lines")
                pymol.do("copy s%s, structure" % frame)
                pymol.delete('structure')
                pymol.do("show sticks, organic")

                if np.int(frames[0]) != frame and nb_frames > 1:
                    pymol.do("align s%d, s%d" % (frame, frames[0]))
            
            pymol.do("center")
        except:
            print("Connection issue with PyMol! (Cmd: pymol -R)")

def get_selected_frames(attr, old, new):
    update_pymol(new['1d']['indices'])

def get_comments_from_txt(fname, comments='#'):
    with open(fname) as f:
        for line in f:
            if comments in line:
                line = line.replace('%s '% comments, "")
                return {pname : pvalue for pname, pvalue in zip(line.split(' ')[::2], line.split(' ')[1::2])}

        return None

def visualize_configuration(top_file, dcd_files, config_file):

    # I know this is very nasty ...
    global u
    global H_frame
    global id_to_H_frame

    title = None

    # Open DCD trajectory
    u = Universe(top_file, dcd_files)
    # Get comments from config file
    prm = get_comments_from_txt(config_file)

    # Read configuration txt file
    try:
        frames, x, y = np.loadtxt(config_file, unpack=True)
    except:
        x, y = np.loadtxt(config_file, unpack=True)
        frames = np.arange(0, x.shape[0])

    bin_size = 0.025

    # Calculate edges
    xedges = np.arange(np.min(x), np.max(x) + bin_size, bin_size)
    yedges = np.arange(np.min(y), np.max(y) + bin_size, bin_size)

    # Compute an histogram, just to have the maximum bin
    H, xedges, yedges = np.histogram2d(x, y, bins=(xedges, yedges))

    # Initialize histogram array and frame array
    tmp = np.zeros(shape=(xedges.shape[0], yedges.shape[0], 1), dtype=np.int32)
    H_frame = np.zeros(shape=(xedges.shape[0], yedges.shape[0], np.int(np.max(H))+100), dtype=np.int32)

    # For each coordinate, we put them in the right bin and add the frame number
    for i in xrange(0, frames.shape[0]):
        ix = np.int((x[i] - xedges[0]) / bin_size)
        iy = np.int((y[i] - yedges[0]) / bin_size)
        
        H_frame[ix, iy, tmp[ix, iy]] = frames[i]
        # Add 1 to the corresponding bin
        tmp[ix, iy] += 1
    
    xx, yy = [], []
    id_to_H_frame = []
    count, alpha = [], []

    min_hist = np.float(np.min(H))
    max_hist = np.float(np.max(H))

    # Add we keep only the bin with structure
    for i in xrange(0, H.shape[0]):
        for j in xrange(0, H.shape[1]):

            if H[i,j] > 0:
                xx.append(xedges[i])
                yy.append(yedges[j])
                id_to_H_frame.append((i,j))
                count.append(H[i,j])
                alpha.append((np.float(H[i,j]) - min_hist) / (max_hist - min_hist))

    TOOLS = "wheel_zoom,box_zoom,undo,redo,box_select,save,resize,reset,hover,crosshair,tap,pan"

    if prm:
        title = '#Conf: %s Cycles: %s Rc: %s (Stress: %5.4f Corr: %5.4f)' % (frames.shape[0], 
                 prm['cycle'], prm['rc'], np.float(prm['stress']), np.float(prm['corr']))
    else:
        title = '#Conf: %s' % frames.shape[0]

    p = figure(plot_width=850, plot_height=850, tools=TOOLS, title=title, 
               webgl=True, title_text_font_size='12pt')

    #p.axis.visible = False

    source = ColumnDataSource(data={'xx': xx, 'yy': yy, 'count': count})
    p.rect('xx', 'yy', width=bin_size, height=bin_size, fill_alpha=alpha,
           line_alpha=alpha, fill_color='black', line_color='black', 
           source=source)

    hover = p.select({'type': HoverTool})
    hover.tooltips = [("(X, Y)", "(@xx @yy)"), ("#Frames", '@count')]

    output_server('visualize')

    # open a session to keep our local document in sync with server
    session = push_session(curdoc())
    # Update data when we select conformations
    source.on_change('selected', get_selected_frames)
    # Open the document in a browser
    session.show(p)
    # Run forever !!
    session.loop_until_closed()

def parse_options():
    parser = argparse.ArgumentParser(description='visu 2D configuration')
    parser.add_argument('-t', "--top", dest='top_file', required=True,
                        action="store", type=str,
                        help="psf or pdb file used for simulation")
    parser.add_argument('-d', "--dcd", dest='dcd_files', required=True,
                        action="store", type=str, nargs='+',
                        help = "list of dcd files")
    parser.add_argument('-c', "--configuration", dest='config_file',
                        required=True, action="store", type=str,
                        help="configuration file")

    args = parser.parse_args()

    return args

def main():

    options = parse_options()

    top_file = options.top_file
    dcd_files = options.dcd_files
    config_file = options.config_file

    if is_screen_running('visu_bokeh') and is_screen_running('visu_pymol'):
        # Visualize embedding
        visualize_configuration(top_file, dcd_files, config_file)
    else:
        print('Error: Bokeh/PyMOL are not running !')

if __name__ == '__main__':
    main()