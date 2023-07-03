 
'''
Bob Schiffrin July 2023

draw_xlink.py

For use within PyMOL. This takes in two residues and draws a cylinder
between the two CA atoms of the residues with a custom colour and radius. 
The colour parameter can be a named colour from a dictionary or RGB values

Example usage:

First run this script to make the function at the command line. e.g

PyMOL>run draw_xlink.py

Then for example:

PyMOL>draw_xlink my_obj_name, A, 100, A, 400, green, radius=0.4

or 

PyMOL>draw_xlink my_obj_name, A, 21, B, 27, [0.0,0.0,1.0], radius=0.6

'''

from pymol.cgo import *
from pymol import cmd

# Dictionary look of some common colours - can be expanded if required
# Alternatively RGB values can be supplied to the draw_xlink function

colours_dict = {

    'red': [1.0, 0.0, 0.0],
    'green': [0.0, 1.0, 0.0],
    'blue': [0.0, 0.0, 1.0],
    'yellow': [1.0, 1.0, 0.0],
    'cyan': [0.0, 1.0, 1.0],
    'magenta': [1.0, 0.0, 1.0],
    'white': [1.0, 1.0, 1.0],
    'black': [0.0, 0.0, 0.0],
    'gray': [0.5, 0.5, 0.5],
    'orange': [1.0, 0.5, 0.0],
    'brown': [0.6, 0.3, 0.0],
    'purple': [0.5, 0.0, 0.5],
    'lime': [0.5, 1.0, 0.5],
    'pink': [1.0, 0.5, 0.5],
    'salmon': [0.9, 0.5, 0.3],
    'olive': [0.5, 0.5, 0.0],
}

@cmd.extend
def draw_xlink(obj, chain1, resid1, chain2, resid2, colour, radius=0.5):
    '''
    This takes in two residues and draws a cylinder between the two 
    CA atoms of the residues with a custom colour and radius. The colour
    parameter can be a named colour from a dictionary or RGB values
    '''

    # make text for selection of the ca atom of both residues in xlink
    s1 = "obj " + obj + " and chain " + chain1 + " and resi " + resid1 + " and name CA" 
    s2 = "obj " + obj + " and chain " + chain2 + " and resi " + resid2 + " and name CA"

    # get a model for each of the selections
    model1 = cmd.get_model(s1)
    model2 = cmd.get_model(s2)

    # get x,y,z coordinates of each ca atom 
    x1 = model1.atom[0].coord[0]
    y1 = model1.atom[0].coord[1]
    z1 = model1.atom[0].coord[2]
    x2 = model2.atom[0].coord[0]
    y2 = model2.atom[0].coord[1]
    z2 = model2.atom[0].coord[2]

    # set the rgb values of the cylinder
    if colour in colours_dict:
        r1, g1, b1 = colours_dict[colour]
        r2, g2, b2 = colours_dict[colour]
    else:
        try:
            rgb_values = [float(x) for x in colour[1:-1].split(',')]
            if len(rgb_values) == 3 and all(0 <= x <= 1 for x in rgb_values):
                r1, g1, b1 = rgb_values
                r2, g2, b2 = rgb_values
            else:
                print('Invalid RGB format, using default colour')
                r1, g1, b1 = 1.0, 1.0, 1.0  # Default to blue
                r2, g2, b2 = 1.0, 1.0, 1.0  # Default to blue
        except:
            print('Error parsing custom colour values, using default colour')
            r1, g1, b1 = 0.0, 0.0, 1.0  # Default to blue
            r2, g2, b2 = 0.0, 0.0, 1.0  # Default to blue

    # create the object and draw the cylinder - radius of the cylinder defaults to 0.5
    xlink_obj = [CYLINDER, x1, y1, z1, x2, y2, z2, float(radius), r1, g1, b1, r2, g2, b2]
    xlink_obj_name = f'{chain1}{resid1}_{chain2}{resid2}_custom'
    cmd.load_cgo(xlink_obj, xlink_obj_name)

    print('Done')





