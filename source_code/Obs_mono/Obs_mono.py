'''
Obs_mono.py

This class stores information about an experimentally observed mono-link (dead-end) - used by the PyXlinkViewer PyMOL plugin

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

class Obs_mono():
    
    def __init__(self):
       
        self.res = ""   
        self.chain = ""
        self.resid= ""
        self.resname = ""
        
        #name of the pymol object associated with drawn xlink
        self.obj_name = ""


    def __eq__(self,other) :
        '''
        Overloaded equality operator in order to remove duplicates in input XL file
        '''
        if self.resid == other.resid and self.chain == other.chain:
            return True
        else:
            return False


    def output(self):
        '''
        Prints chain and resid info to the screen. Used for debugging.
        '''
        print('Obs_mono: ' + self.resid + '_' + self.chain + '\n')

