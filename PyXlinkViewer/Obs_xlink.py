'''
Obs_xlink.py

This class stores information about an experimentally observed xlink - used by the PyXlinkViewer PyMOL plugin

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

class Obs_xlink():
    
    def __init__(self):
       
        self.res1 = ""
        self.res2 = ""
        
        self.chain1 = ""
        self.chain2 = ""
    
        self.resid1= ""
        self.resid2 = ""

        self.resname1 = ""
        self.resanme2 = ""

        self.distance = 0.0
        
        #name of the pymol object associated with drawn xlink
        self.obj_name = ""

        # define 2 booleans to keep a record of if the residues in the xlink are present in the PyMOL object
        self.bRes1_in_obj = True
        self.bRes2_in_obj = True

    
    def __eq__(self,other) :
        '''
        Overloaded equality operator in order to remove duplicates in input XL file
        '''
        if self.resid1 == other.resid1 and self.resid2 == other.resid2 and self.chain1 == other.chain1 and self.chain2 == other.chain2:
            return True
        else:
            return False



    def output(self):
        '''
        Outputs the data for the observed xlink. Used for debugging purposes
        '''
        print(self.res1 + ' ' +  self.chain1 + ' ' + self.resid1 + ' ' + self.res2 + ' ' + self.chain2 + ' ' + self.resid2 + ' ' + str(self.distance))

