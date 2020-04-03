'''
PyXlinkViewer init file

This is the main program for the PyXlinkViewer for PyMOL 2

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

from __future__ import absolute_import
from __future__ import print_function

import os
import sys


# make sure that the directory that contains this file is in users path
script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from BXlink_viewer import BXlink_viewer
from pymol import cmd

##-----------------------------------------------------------------------------


def __init_plugin__(app=None):
    '''
    Add an entry to the PyMOL "Plugin" menu
    '''
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('PyXlinkViewer', run_plugin_gui)


# global reference to avoid garbage collection of our dialog
dialog = None


##-----------------------------------------------------------------------------


def run_plugin_gui():
    '''
    Open our custom dialog
    '''
    global dialog

    if dialog is None:
        dialog = make_dialog()

    dialog.show()


def make_dialog():
    '''
    Function which initiates the dialog
    ''' 

    from pymol import cmd
    from pymol.Qt import QtWidgets, QtGui, QtCore  # note this gives the PyQt5 rather than PyQt4 interface
    from pymol.Qt.utils import loadUi
    from pymol.Qt.utils import getSaveFileNameWithExt

    import pymol.Qt
    Qt = QtCore.Qt

    #make a viewer object accessible by all functions
    viewer = BXlink_viewer()

    QFileDialog = QtWidgets.QFileDialog
    getOpenFileNames = QFileDialog.getOpenFileNames
    
    # create a new Window
    dialog = QtWidgets.QDialog()

    # populate the Window from our *.ui file which was created with the Qt Designer
    uifile = os.path.join(os.path.dirname(__file__), 'PyXlinkViewer.ui')
    form = loadUi(uifile, dialog)


#-------------------------------------------------------------------

    
    def open_file():
        '''
        Callback for the open_xlink_file button
        '''
        
        # get a filename using open file diagog - not the filename can have any extension  
        startdir = os.getcwd()

        open_fname = getOpenFileNames(dialog, 'Open file', startdir)[0]
        
        if open_fname:
        
            #need to convert list object returned by open file dialog to a string
            xlink_file = "".join(open_fname)       

            # only deal with files in jwalk format for now
            xlink_file_type = 'jwalk'

            viewer.set_xlink_file(xlink_file)
            viewer.set_xlink_file_type(xlink_file_type)
            viewer.parse_xlink_file()
            viewer.calculate_distances()
            viewer.test_monos_in_obj()
            populate_xlink_table()
            change_num_sat_viol()
            
            viewer.display()

#-------------------------------------------------------------------

    def populate_xlink_table():
        '''
        Populates the table with xlinks and mono-links according to which are currently set to be displayed
        '''

        obs_xlinks = viewer.obs_xlinks
        obs_monos = viewer.obs_monos

        w = form.table_xlinks
        
        #remove data if already 
        w.setRowCount(0)

        entries = []

        for xl in obs_xlinks:

            str_dist = '{0:3.1f}'.format(xl.distance)
            entry = [xl.chain1, xl.resid1, xl.chain2, xl.resid2, str_dist]

            bAdded_entry = False
            if xl.distance <= viewer.threshold and viewer.show_satisied == True:
                entries.append(entry)
                bAdded_entry = True

            if xl.distance > viewer.threshold and viewer.show_violated == True:
                entries.append(entry)
                bAdded_entry = True

            # check that inters should be shown
            if bAdded_entry and xl.chain1 != xl.chain2 and viewer.show_inter == False:
                entries.pop()

            if bAdded_entry and xl.chain1 == xl.chain2 and viewer.show_intra == False:
                entries.pop()
        

        #now add the monolinks to end of table
        for m in obs_monos:
            if viewer.show_mono == True:
                entry = [m.chain, m.resid, '-', '-', '-']
                entries.append(entry)

        if entries:
            w.setColumnCount(len(entries[0]))
            w.setRowCount(len(entries))

            for i, row in enumerate(entries):
                for j, col in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(col)
                    w.setItem(i, j, item)
                    #align text in centre of cell
                    item.setTextAlignment(Qt.AlignCenter)
        
            # set the columns to be equal width and fit in the table
            header = w.horizontalHeader()
            for i in range(0, len(entries[0])):  
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
            


#-------------------------------------------------------------------

    
    def export():
        '''
        Callback function for 'Export' button. Opens save file dialog and saves current table in csv format.
        For each entry in the table two additional columns are outputted. One containing the current threshold
        value, and one 'Sat/Viol' for which 'S' or 'V' is outputted depending on whether the xlink is satisfied
        or violated, given the currently set threshold value
        '''
        
        filename = getSaveFileNameWithExt(dialog, 'Save As...', filter='csv file (*.csv)')
       
        if filename:
        
            table = form.table_xlinks

            num_cols = table.columnCount()
            num_rows = table.rowCount()

            with open(filename, 'w') as f:

                for i in range(0, num_cols):

                    item = table.horizontalHeaderItem(i)
                    f.write(item.text() + ',')
                f.write('Threshold,Sat-Viol\n')

                for i in range(0, num_rows):
                    for j in range(0, num_cols):

                        item = table.item(i, j)
                        text = item.text()
                        f.write(text + ',')
                   
                    #last item retrieved was the distance for this xlink or a dash if a mono-link entry so use this to test if satisfied 
                    if text == '-':
                        f.write('-,-\n')
                    else:
                        f.write(str(viewer.threshold) + ',')

                        if float(text) <= viewer.threshold:
                            f.write('S\n')
                        else:
                            f.write('V\n')

#----------------------------------------------------------------------------------------------------
    
    # callback functions for checkboxes 

    def check_satisfied_click():
        viewer.set_show_satisfied(form.check_satisfied.isChecked())

        populate_xlink_table()
        viewer.update()


    def check_violated_click():
        viewer.set_show_violated(form.check_violated.isChecked())

        populate_xlink_table()
        viewer.update()

    def check_inter_click():
        viewer.set_show_inter(form.check_inter.isChecked())
        populate_xlink_table()
        viewer.update()

    def check_intra_click():
        viewer.set_show_intra(form.check_intra.isChecked())
        populate_xlink_table()
        viewer.update()

    def check_mono_click():
        viewer.set_show_mono(form.check_mono.isChecked())
        populate_xlink_table()
        viewer.update()

#---------------------------------------------------------------------------

    # Call back functions for colour change buttons

    def change_satisfied_colour():
        color = QtWidgets.QColorDialog.getColor()
        
        form.frame_satisfied_colour.setStyleSheet("QWidget { background-color: %s}" % color.name())

        rgb_list = [color.redF(), color.greenF(), color.blueF()]
        viewer.set_satisfied_colour(rgb_list)
        viewer.update()


    def change_violated_colour():
        color = QtWidgets.QColorDialog.getColor()
        
        form.frame_violated_colour.setStyleSheet("QWidget { background-color: %s}" % color.name())

        rgb_list = [color.redF(), color.greenF(), color.blueF()]
        viewer.set_violated_colour(rgb_list)
        viewer.update()


    def change_mono_colour():
        color = QtWidgets.QColorDialog.getColor()
        
        form.frame_mono_colour.setStyleSheet("QWidget { background-color: %s}" % color.name())

        rgb_list = [color.redF(), color.greenF(), color.blueF()]
        viewer.set_mono_colour(rgb_list)
        viewer.update()

#---------------------------------------------------------------------------

    # call back functions for doublespin boxes

    def change_threshold():
        viewer.set_threshold(form.doublespin_threshold.value())
        change_num_sat_viol()
        populate_xlink_table()
        viewer.update()


    def change_width():
        viewer.set_radius(form.doublespin_width.value())
        viewer.update()

    def change_mono_size():

        viewer.set_mono_size(form.doublespin_mono_size.value())
        viewer.update()


#---------------------------------------------------------------------------
    def change_num_sat_viol():
        '''
        Changes the numbers of satisfied and violated xlinks in line-edit boxes. Only called when a change to threshold value is made
        '''

        num_sat = 0
        num_viol  = 0

        for xl in viewer.obs_xlinks:
            
            # NB. check that both residues are in structure, if one is not, don't class as either sat or viol as not known
            if xl.distance <= viewer.threshold and xl.bRes1_in_obj == True and xl.bRes2_in_obj == True:
                num_sat += 1
              
            if xl.distance > viewer.threshold and xl.bRes1_in_obj == True and xl.bRes2_in_obj == True: 
                num_viol += 1


        form.line_edit_satisfied.setText(str(num_sat))
        form.line_edit_violated.setText(str(num_viol))

        form.line_edit_satisfied.setAlignment(Qt.AlignCenter)
        form.line_edit_violated.setAlignment(Qt.AlignCenter)


#-------------------------------------------------------------------------

    # initialise the viewer threshold and mono-size values in doublespin boxes - these are set in QtDesigner
    viewer.set_threshold(form.doublespin_threshold.value())
    viewer.set_mono_size(form.doublespin_mono_size.value())

    # initialise the widgets
    form.check_satisfied.setChecked(True)
    form.check_violated.setChecked(True)
    form.check_inter.setChecked(True)
    form.check_intra.setChecked(True)


    # stop object list box from resizing when objects are added
    w = form.list_select_object
    w.setFixedSize(149, 50)

    # fill the listbox with the current objects
    objects = cmd.get_names()

    for i, obj in enumerate(objects):
        item = QtWidgets.QListWidgetItem(obj)

        form.list_select_object.addItem(item)

        if i == 0: #select the first item in the QListWidget
            item.setSelected(True)
            viewer.set_obj(item.text())

    form.list_select_object.setFocus()

    # initialise colours in for satisfied, violated, and mono-links
    form.frame_satisfied_colour.setStyleSheet("QWidget { background-color: %s}" % '#0000FF')  # initialise to blue
    form.frame_violated_colour.setStyleSheet("QWidget { background-color: %s}" % '#FF0000')  # initialise to red
    form.frame_mono_colour.setStyleSheet("QWidget { background-color: %s}" % '#FFFF00')  # initialise to yellow

    # hook up the button callbacks
    form.button_open_xlink_file.clicked.connect(open_file)
    form.button_close.clicked.connect(dialog.close)
    form.button_satisfied_colour.clicked.connect(change_satisfied_colour)
    form.button_violated_colour.clicked.connect(change_violated_colour)
    form.button_mono_colour.clicked.connect(change_mono_colour)
    form.button_export.clicked.connect(export)

    # hook up the check box callbacks
    form.check_satisfied.clicked.connect(check_satisfied_click)
    form.check_violated.clicked.connect(check_violated_click)
    form.check_inter.clicked.connect(check_inter_click)
    form.check_intra.clicked.connect(check_intra_click)
    form.check_mono.clicked.connect(check_mono_click)

    # hook up the check box callbacks
    form.doublespin_threshold.valueChanged.connect(change_threshold)
    form.doublespin_width.valueChanged.connect(change_width)
    form.doublespin_mono_size.valueChanged.connect(change_mono_size)


    return dialog
