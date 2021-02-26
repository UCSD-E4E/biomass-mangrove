# ----------------------------------- #
# ----- Adjust DEM to Reference ----- #
# ----------------------------------- #
#
# Drone GPS measurements tend to be accurate altitude only in a relative
# sense. The actual measurements are often offset by 100m or more. This tool
# attempts to correct for this offset. The user must identify a point on the 
# model with a known elevation, create a marker named "Elevation Reference"
# and enter the correct elevation for the marker. This script will use the 
# altitude error for the marker to correct the offset for the entire model.

# Import modules
import Metashape
from PySide2 import QtGui, QtCore, QtWidgets

# Settings
corners_only = True


class AdjustDEM(QtWidgets.QDialog):

	def __init__(self, parent):
	
		# Define QT graphical elements
		QtWidgets.QDialog.__init__(self, parent)

		self.setWindowTitle("Adjust DEM to Reference")

		self.setMinimumHeight(160)
		
		self.btnQuit = QtWidgets.QPushButton("Quit")
		self.btnQuit.setFixedSize(100,50)
		
		self.btnP1 = QtWidgets.QPushButton("Adjust")
		self.btnP1.setFixedSize(100,50)
		
		self.pBar = QtWidgets.QProgressBar()
		self.pBar.setTextVisible(True)
		self.pBar.setFixedWidth(225)
		self.pBar.setFixedHeight(25)
		
		self.progTxt = QtWidgets.QLabel()
		self.progTxt.setText("Progress:")

		self.chnkTxt = QtWidgets.QLabel()
		self.chnkTxt.setText("Chunk:")

		self.chnkNm = QtWidgets.QLabel()
		self.chnkNm.setText(chunk.label)

		# Assemble QT graphical elements
		layout = QtWidgets.QGridLayout()
		layout.addWidget(self.chnkTxt, 0, 0, 1, 1)
		layout.addWidget(self.chnkNm, 0, 1, 1, 5)
		layout.addWidget(self.progTxt, 1, 0, 1, 6)
		layout.addWidget(self.pBar, 2, 0, 1, 6)
		layout.addWidget(self.btnP1, 3, 0, 1, 3)
		layout.addWidget(self.btnQuit, 3, 3, 1, 3)
		self.setLayout(layout)

		# Define button functions
		begin_level = lambda : self.adjust_dem()
		
		QtCore.QObject.connect(self.btnP1, QtCore.SIGNAL("clicked()"), 
			begin_level)
		QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL("clicked()"), 
			self, QtCore.SLOT("reject()"))	

		self.exec()
		
	def adjust_dem(self):
		print("Begin Adjusting.")

		# Variables
		ref_markers = []
		offset = 0

		# Find reference markers
		print("Locating reference markers...")
		for marker in chunk.markers:
			print("    candidate: {}".format(marker.label))
			if "Elevation Reference" in marker.label:
				print("  {}".format(marker.label))
				ref_markers.append(marker)

		# Abort if marker not found
		if ref_markers == []:
			print("Error Marker not found.")
			print("Please create at least one marker with 'Elevation Reference in the name.")
			return
		
		# Determine average offset
		marker_err = 0
		print("Determining elevation offset...")
		for marker in ref_markers:

			# Calculate offset
			marker_raw = marker.reference.location
			marker_adj = chunk.crs.project(chunk.transform.matrix.mulp(marker.position))
			marker_err += marker_raw.z - marker_adj.z
			print("  {} - Elevation offset: {}".format(marker.label, marker_err))

		# Create new offset vector
		avg_error = marker_err / len(ref_markers)
		offset = Metashape.Vector([0, 0, avg_error])
		print("Average Offset: {} m".format(avg_error))

		# Adjust cameras
		print("Adjusting cameras:")
		cam_count = len(chunk.cameras)
		for idx, cam in enumerate(chunk.cameras):
			old_vect = cam.reference.location
			if not old_vect:
				continue
			new_vect = old_vect + offset
			print("  Camera {} - Old Z: ({}) New Z: ({})".format(cam.label, old_vect.z, new_vect.z))
			cam.reference.location = new_vect
			self.pBar.setValue(int((idx + 1) / cam_count * 100))

		# Update transforms
		chunk.updateTransform()
		Metashape.app.update()


def main():

	# Global variables
	global doc, chunk, app
	doc = Metashape.app.document
	chunk = doc.chunk
	app = QtWidgets.QApplication.instance()

	parent = app.activeWindow()
	
	dlg = AdjustDEM(parent)
		
main()	
# PhotoScan.app.addMenuItem("Custom/Adjust DEM to Reference", main)
