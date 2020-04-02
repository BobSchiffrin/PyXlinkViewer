'''
BJwalk_file_reader.py

This class is used in the PyXlinkViewer plugin for PyMOL to read in a file containing
chain and residue information for xlinks and monolinks in jwalk format. The file must
contain data in the format:

   <resid1>|<chain1>|<resid1>|<chain1>|

for xlinks, and:

   <resid>|<chain>|

for mono-links.  The parser deals with the cases where the user has added additional
whitespace at the end of a line, or added empty lines, however these will need to be
edited to remove if the file is to be used with jwalk.

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

from Obs_xlink import Obs_xlink
from Obs_mono import Obs_mono


class BJwalk_file_reader:
    def __init__(self, filename) :

        self.filename = filename

        # initialise lists of xlinks (of class Obs_xlink) and mono-links (of class Obs_mono)
        self.xlinks = []
        self.monos = []

    def read(self):

        with open(self.filename, 'rb') as f:

            for line in f:

                #deal with case where user has left some trailing whitespace at the end of a line 
                line = line.rstrip()

                if line: #test for case where user has added additional empty lines
                    data = line.split('|')


                    if len(data) == 3:

                        mono = Obs_mono()
                        mono.resid = data[0]
                        mono.chain = data[1]
                        mono.obj_name = mono.chain + '_' + mono.resid
                        self.monos.append(mono)

                    elif len(data) == 5:
                        xl = Obs_xlink()
                        xl.resid1 = data[0]
                        xl.chain1 = data[1]
                        xl.resid2 = data[2]
                        xl.chain2 = data[3]
                        xl.obj_name = xl.chain1 + '_' + xl.resid1 + '-' + xl.chain2 + '_' + xl.resid2
                        self.xlinks.append(xl)
                    else:
                        return None

                

        return self.xlinks, self.monos

            