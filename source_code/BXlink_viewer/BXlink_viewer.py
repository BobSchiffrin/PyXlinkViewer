'''
BXlink_viewer.py

This class is used in the PyXlinkViewer plugin for PyMOL to store and control the
display of xlinks (and mono-links) observed by mass spectrometry

Copyright (C) Bob Schiffrin March 2020

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Any queries, suggestions, or bug reports (!) please contact Bob Schiffrin:
b.schiffrin@leeds.ac.uk

'''

from pymol import cmd
from pymol.cgo import *
import math

from Obs_xlink import Obs_xlink
from Obs_mono import Obs_mono
from BJwalk_file_reader import BJwalk_file_reader


class BXlink_viewer():

    def __init__(self):

        self.obs_xlinks = []   # list of observed xlinks
        self.obs_monos = []   #list of observed mono-links

        # initialise the threshold distance which defines whether an xlink is satisfied or violated
        self.threshold = 0.0

        # this variable controls the size of spheres drawn at the CA position of mono-link sites
        self.mono_size = 0.0

        # store the PyMOL object associated with class instance
        self.obj = ""
       
        # name of the file containing xlinks and mono-links
        self.xlink_file = ""

        # file type - only jwalk style files at present, but easily extendable at a later date
        self.xlink_file_type = ""

        # set the default radius of the cylinder
        self.radius = 0.5

        # only use C-alpha carbon distances for distance calculations - easily extendable for other atoms 
        self.atom_type = 'ca'

        # initialise colours
        self.satisfied_colour = [0. ,0. ,1.]  # initialise to blue
        self.violated_colour = [1. ,0. , 0.]  # initialise to red
        self.mono_colour = [1. ,1. , 0.]  # initialise to yellow

        # hold the state of check boxes
        self.show_satisied = True
        self.show_violated = True
        self.show_inter = True
        self.show_intra = True
        self.show_mono = False

        # keep a count of how many xlinks are satisfied/violated for the selected threshold
        self.num_sat = 0
        self.mum_viol = 0


  
#------------------------------------------------------------------------------------
# Functions to set member variables of the class:

    def set_xlink_file(self, file):
        self.xlink_file = file

    def set_xlink_file_type(self, file_type):
        self.xlink_file_type = file_type

    def set_obj(self, obj):
        self.obj = obj

#---------------------------------
    def set_show_satisfied(self, bool_sat):
        self.show_satisied = bool_sat

    def set_show_violated(self, bool_viol):
        self.show_violated = bool_viol

    def set_show_inter(self, bool_inter):
        self.show_inter = bool_inter

    def set_show_intra(self, bool_intra):
        self.show_intra = bool_intra

    def set_show_mono(self, bool_mono):
        self.show_mono = bool_mono
#---------------------------------

    def set_satisfied_colour(self, rgb_list):
        self.satisfied_colour = rgb_list

    def set_violated_colour(self, rgb_list):
        self.violated_colour = rgb_list

    def set_mono_colour(self, rgb_list):
        self.mono_colour = rgb_list

#---------------------------------
    def set_threshold(self, dist):
        self.threshold = dist

    def set_radius(self, width):
        self.radius = width

    def set_mono_size(self, size):
        self.mono_size = size

#---------------------------------
    
    def set_num_sat(self, num):
        self.num_sat = num

    def set_num_viol(self, num):
        self.set_num_viol = num


#------------------------------------------------------------------------------------

    def parse_xlink_file(self):
        '''
        Extract and store the xlink and mono-link data from the xlink file. Only jwalk style
        files supported at the present time to allow maximum user flexibility
        '''

        if self.xlink_file_type == 'jwalk':
            reader = BJwalk_file_reader(self.xlink_file)
            self.obs_xlinks, self.obs_monos = reader.read()


#------------------------------------------------------------------------------------


    def get_dist(self,sele1, sele2) :
        '''
        Arguments are PyMOL selection strings for the two atoms for which the distance is required
        Returns the euclidean distance between them
        '''
        
        try:
            #first get a model for each selection
            model1 = cmd.get_model(sele1)
            model2 = cmd.get_model(sele2)

            #create variables initialised to zero to hold the sum of our coordinates
            x1,y1,z1,x2,y2,z2=0.,0.,0.,0.,0.,0.

            #loop through each atom in the model and sum them in variables x,y and z
            for a in model1.atom:
                x1+= a.coord[0]
                y1+= a.coord[1]
                z1+= a.coord[2]

            for a in model2.atom:
                x2+= a.coord[0]
                y2+= a.coord[1]
                z2+= a.coord[2]

            #calculate the difference vector between them
            diff_vector = [x1-x2, y1-y2, z1-z2]

            #calculate magnitude of the vector
            dist = math.sqrt((diff_vector[0]**2) + (diff_vector[1]**2) + (diff_vector[2]**2))
        
        except:
            # if fails just return the the distance as zero. This will occur when one or both residues involved are missing in the structure
            dist = 0.0


        return dist

#------------------------------------------------------------------------------------


    def draw_xlink(self, xl, bSatisfied):
        '''
        This takes in a xlink (Obs_xlink object) and draws it as a cylinder between the two ca atoms. The bSatisfied 
        argument is a boolean which gives whether the distance between the residues is under the threshold set.
        '''

        #make text for selection of the ca atom of both residues in xlink
        s1 = "obj " + self.obj + " and chain " + xl.chain1 + " and resi " + xl.resid1 + " and name " + self.atom_type
        s2 = "obj " + self.obj + " and chain " + xl.chain2 + " and resi " + xl.resid2 + " and name " + self.atom_type
 

        #get a model for each of the selections
        model1 = cmd.get_model(s1)
        model2 = cmd.get_model(s2)

        #get x,y,z coordinates of each ca atom 
        x1 = model1.atom[0].coord[0]
        y1 = model1.atom[0].coord[1]
        z1 = model1.atom[0].coord[2]
        x2 = model2.atom[0].coord[0]
        y2 = model2.atom[0].coord[1]
        z2 = model2.atom[0].coord[2]


        #set the rgb values of the cylinder
        if bSatisfied == True:
            r1 = self.satisfied_colour[0]; r2 = self.satisfied_colour[0] 
            g1 = self.satisfied_colour[1]; g2 = self.satisfied_colour[1] 
            b1 = self.satisfied_colour[2]; b2 = self.satisfied_colour[2] 
        elif bSatisfied == False:
            r1 = self.violated_colour[0]; r2 = self.violated_colour[0] 
            g1 = self.violated_colour[1]; g2 = self.violated_colour[1] 
            b1 = self.violated_colour[2]; b2 = self.violated_colour[2] 


        # create the object and draw the cylinder - radius of the cylinder defined by the user
        obj = [ CYLINDER, x1, y1, z1, x2, y2, z2, self.radius, r1, g1, b1, r2, g2, b2 ]
        cmd.load_cgo(obj, xl.obj_name)

        
#------------------------------------------------------------------------------

    def draw_mono(self, mono):
        '''
        This takes in a mono-link (Obs_mono object) and draws it as a sphere at the ca atom position in the residue.
        '''
        
        s1 = "obj " + self.obj + " and chain " + mono.chain + " and resi " + mono.resid + " and name " + self.atom_type

        model1 = cmd.get_model(s1)

        #get x,y,z coordinates of each ca atom 
        x1 = model1.atom[0].coord[0]
        y1 = model1.atom[0].coord[1]
        z1 = model1.atom[0].coord[2]

        #Create and draw the GCO sphere
        obj = [COLOR] + self.mono_colour + [SPHERE, x1, y1, z1, self.mono_size]
        cmd.load_cgo(obj, mono.obj_name)



#------------------------------------------------------------------------------

    def calculate_distances(self):
        '''
        Calculates distances between each observed xlink. Only called once after xlink file is opened
        '''

        # fill each obs_link distance so do this only once
        for xl in self.obs_xlinks:

            #first make the selections
            s1 = "obj " + self.obj + " and chain " + xl.chain1 + " and resi " + xl.resid1 + " and name " + self.atom_type
            s2 = "obj " + self.obj + " and chain " + xl.chain2 + " and resi " + xl.resid2 + " and name " + self.atom_type

            # deal with case where at least one residue is missing in the structure
            #test that are residues are in structure
            if cmd.count_atoms(s1) == 0 or cmd.count_atoms(s2) == 0:

                if cmd.count_atoms(s1) == 0 and cmd.count_atoms(s2) != 0:
                    xl.bRes1_in_obj = False
                    print('\nWarning: Residue {0} in chain {1} is not present in the selected PyMOL object, so the {0}_{1}-{2}_{3} xlink will not be displayed'.format(xl.resid1, xl.chain1, xl.resid2, xl.chain2))

                elif cmd.count_atoms(s1) != 0 and cmd.count_atoms(s2) == 0:
                    xl.bRes2_in_obj = False
                    print('\nWarning: Residue {2} in chain {3} is not present in the selected PyMOL object, so the {0}_{1}-{2}_{3} xlink will not be displayed'.format(xl.resid1, xl.chain1, xl.resid2, xl.chain2))


                elif cmd.count_atoms(s1) == 0 and cmd.count_atoms(s2) == 0:
                    xl.bRes1_in_obj = False
                    xl.bRes2_in_obj = False
                    print('\nWarning: Residue {0} in chain {1} and residue {2} in chain {3} are both not present in the selected PyMOL object, so the {0}_{1}-{2}_{3} xlink will not be displayed'.format(xl.resid1, xl.chain1, xl.resid2, xl.chain2))

            else: 
                xl.distance = self.get_dist(s1,s2)


#------------------------------------------------------------------------------

    def display(self):
        '''
        This function decides which xlinks should be shown based on user selections, and draws and an xlink if required.
        Also, draws all mono-links if user has checked the show_monos checkbox
        '''

        # get the current view in viewer 
        current_view = cmd.get_view()
        
        colour = ""

        for xl in self.obs_xlinks:

            if xl.distance != 0:  # test for case where one or both residues missing from structure in which case xlink not drawn

              
                # This is a rather convoluted set of else-if statements, but thoroughly tests the state of user checkboxes
                if xl.distance <= self.threshold and self.show_satisied == True and xl.chain1 != xl.chain2 and self.show_inter == True:
                    colour = self.satisfied_colour
                    bSatisfied = True

                elif xl.distance <= self.threshold and self.show_satisied == True and xl.chain1 != xl.chain2 and self.show_inter == False:
                    colour = ""


                elif xl.distance <= self.threshold and self.show_satisied == False and xl.chain1 != xl.chain2 and self.show_inter == True:
                    colour = ""

                elif xl.distance <= self.threshold and self.show_satisied == False and xl.chain1 != xl.chain2 and self.show_inter == False:
                    colour = ""

                ####

                elif xl.distance <= self.threshold and self.show_satisied == True and xl.chain1 == xl.chain2 and self.show_intra == True:
                    colour = self.satisfied_colour
                    bSatisfied = True

                elif xl.distance <= self.threshold and self.show_satisied == True and xl.chain1 == xl.chain2 and self.show_intra == False:
                    colour = ""

                elif xl.distance <= self.threshold and self.show_satisied == False and xl.chain1 == xl.chain2 and self.show_intra == True:
                    colour = ""

                elif xl.distance <= self.threshold and self.show_satisied == False and xl.chain1 == xl.chain2 and self.show_intra == False:
                    colour = ""

                #### ###
                
                elif xl.distance > self.threshold and self.show_violated == True and xl.chain1 != xl.chain2 and self.show_inter == True:
                    colour = self.violated_colour
                    bSatisfied = False

                elif xl.distance > self.threshold and self.show_violated == True and xl.chain1 != xl.chain2 and self.show_inter == False:
                    colour = ""

                elif xl.distance > self.threshold and self.show_violated == False and xl.chain1 != xl.chain2 and self.show_inter == True:
                    colour = ""

                elif xl.distance > self.threshold and self.show_violated == False and xl.chain1 != xl.chain2 and self.show_inter == False:
                    colour = ""

                #####

                elif xl.distance > self.threshold and self.show_violated == True and xl.chain1 == xl.chain2 and self.show_intra == True:
                    colour = self.violated_colour
                    bSatisfied = False

                elif xl.distance > self.threshold and self.show_violated == True and xl.chain1 == xl.chain2 and self.show_intra == False:
                    colour = ""

                elif xl.distance > self.threshold and self.show_violated == False and xl.chain1 == xl.chain2 and self.show_intra == True:
                    colour = ""

                elif xl.distance > self.threshold and self.show_violated == False and xl.chain1 == xl.chain2 and self.show_intra == False:
                    colour = ""

                if colour:
                    self.draw_xlink(xl, bSatisfied)
        

        # now display mono-links if selected to be displayed user
        if self.show_mono == True:

            for mono in self.obs_monos:
                self.draw_mono(mono)

        #return to the original view
        cmd.set_view(current_view)


#------------------------------------------------------------------------------

    def update(self):
        '''
        Remove current objects and redraw xlinks and mono-links with current threshold and display settings.
        NB. If this becomes slow for large datasets this could be altered to only change objects affected by user
        interactions with the main dialog
        '''

        self.delete_objects()
        self.display()

#------------------------------------------------------------------------------

    def delete_objects(self):
        '''
        Remove all PyMOL objects created for xlinks and mono-links
        '''
        
        for xl in self.obs_xlinks:
            cmd.delete(xl.obj_name)
        
        for mono in self.obs_monos:
            cmd.delete(mono.obj_name)

##-----------------------------------------------------------------------------


    def output_obs_links(self):
        '''
        This function outputs the residue and chain information for all xlinks.
        Used for debugging.
        '''

        for xl in self.obs_xlinks:
            xl.output()



