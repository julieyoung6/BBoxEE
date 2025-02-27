# -*- coding: utf-8 -*-
#
# Bounding Box Editor and Exporter (BBoxEE)
# Author: Julie Young
#
# --------------------------------------------------------------------------
#
# This file is part of Animal Detection Network's (Andenet)
# Bounding Box Editor and Exporter (BBoxEE)
#
# BBoxEE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BBoxEE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------------------------------------------
import os
import sys
from PyQt6 import QtCore, QtWidgets, uic

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(__file__)
DIALOG, _ = uic.loadUiType(os.path.join(bundle_dir, 'filter_dialog.ui'))


class FilterDialog(QtWidgets.QDialog, DIALOG):
    filtered_list = QtCore.pyqtSignal(list)
    BBX_file_selected = QtCore.pyqtSignal(str)

    def __init__(self, data, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('Filter')
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.activateWindow()
        self.data = data
        self.parent = parent
        self.redisplay_filter_results = False

        self.pb_cancel.clicked.connect(self.close)
        self.pb_filter_confirmed.clicked.connect(self.filter_type)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setWindowTitle('Matching BBX Files')
        self.list_widget.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.list_widget.itemDoubleClicked.connect(self.double_click)

    def double_click(self, item_clicked):
        file_selected = item_clicked.text()

        self.redisplay_filter_results = True

        self.list_widget.close()
        self.close()

        self.BBX_file_selected.emit(file_selected)

    def filter(self):
        input_label = self.input_label.text()
        temp_image_list = []

        if self.cb_flagged.isChecked():
            temp_image_list = temp_image_list + self.data['review']

        if input_label != "":
            for image in self.data['images']:
                ann = self.data['images'][image]['annotations']
                for a in ann:
                    if self.match(input_label, a['label']):
                        temp_image_list.append(image)

        if len(temp_image_list) == 0:
            message = ('No results')
            QtWidgets.QMessageBox.warning(self,
                                          'WARNING',
                                          message,
                                          QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            temp_image_list.sort()
            self.filtered_list.emit(temp_image_list)
            self.close()

    def filterBBX(self):
        if self.data:
            needle = self.input_label.text()
            temp_bbx_list = []
            matches = False

            for bbx_file in self.data:
                if self.cb_flagged.isChecked() and self.data[bbx_file]['flagged_images']:
                    matches = True
                    temp_bbx_list.append(bbx_file)
                    continue
                if needle != '' and bbx_file not in temp_bbx_list:
                    for label in self.data[bbx_file]['labels']:
                        if self.match(needle, label):
                            temp_bbx_list.append(bbx_file)
                            matches = True

            if matches:
                self.list_widget.clear()

                for bbx_file in temp_bbx_list:
                    self.list_widget.addItem(bbx_file)

                # resize widget
                max_width = int(self.parent.width() * .8)
                max_height = int(self.parent.height() * .8)
                width = 300
                height = 100

                width = self.list_widget.sizeHintForColumn(0)
                if width > max_width:
                    width = max_width
                height = self.list_widget.sizeHintForRow(0) * self.list_widget.count()
                if height < 200:
                    height = 200
                elif height > max_height:
                    height = max_height
                width += 25

                # centering widget around filter dialog
                centerX = self.pos().x() + self.width() / 2
                centerY = self.pos().y() + self.height() / 2
                list_widget_posX = int(centerX - width / 2)
                list_widget_posY = int(centerY - height / 2)

                self.list_widget.resize(width, height)
                self.list_widget.move(list_widget_posX, list_widget_posY)
                self.list_widget.show()

            else:
                QtWidgets.QMessageBox.information(self, 'Matching BBX Files', 'No bbx files were found containing the label: {}'.format(needle))

    def filter_type(self):
        if "schema" in self.data:
            self.filter()
        else:
            self.filterBBX()

    def match(self, needle, haystack):
        if self.cb_case_sensitive.isChecked() is False:
            needle = needle.lower()
            haystack = haystack.lower()

        if self.cb_exact_match.isChecked():
            return needle == haystack
        else:
            return needle in haystack

    def redisplay(self):
        if self.redisplay_filter_results:
            self.show()
            self.filterBBX()
            self.redisplay_filter_results = False
