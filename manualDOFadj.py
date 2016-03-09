from assembly2lib import *
from PySide import QtGui, QtCore
import traceback
import degreesOfFreedom

moduleVars = {}

class ManualCommand:
    def Activated(self):
        from assembly2solver import solveConstraints
        constraintSystem = solveConstraints(FreeCAD.ActiveDocument)
        self.taskPanel = manualDOFadjPanel( constraintSystem )
        FreeCADGui.Control.showDialog( self.taskPanel )

    def GetResources(self): 
        msg = 'Manually adjust degrees of freedom.'
        return {
            'Pixmap' : ':/assembly2/icons/manualDOFadj.svg', 
            'MenuText': msg, 
            'ToolTip':  msg
            } 
manualCommand = ManualCommand()
FreeCADGui.addCommand('manualDOFadj', manualCommand)


class manualDOFadjPanel:
    def __init__(self, constraintSystem):
        self.constraintSystem = constraintSystem
        self.form = FreeCADGui.PySideUic.loadUi( ':/assembly2/ui/manualDOFadj.ui' )
        self.form.setWindowIcon(QtGui.QIcon( ':/assembly2/icons/manualDOFadj.svg' ) )
        self.form.groupBox_DOF.setTitle('%i Degrees-of-freedom: (Step 1: Choose One)' % len(constraintSystem.degreesOfFreedom))
        for i, d in enumerate(constraintSystem.degreesOfFreedom):
            item = QtGui.QListWidgetItem('%i. %s' % (i+1, str(d)[1:-1].replace('DegreeOfFreedom ','')), self.form.listWidget_DOF)
        self.form.listWidget_DOF.clicked.connect(self.selectionMade)
        self.form.pushButton_update_dof.clicked.connect( self.updateSelected)
        self.form.doubleSpinBox_degRad.valueChanged.connect(self.convertDeg2Rad)
    
    def convertDeg2Rad(self):
        d=self.form.doubleSpinBox_degRad.value()
        self.form.doubleSpinBox_editVal.setValue(d*numpy.pi/180)
        
    def _fillForm(self, degreesOfFreedomToAnimate):
        if len(self.constraintSystem.degreesOfFreedom) > 0:
            self.Y0 = numpy.array([ d.getValue() for d in degreesOfFreedomToAnimate] )
            self.form.doubleSpinBox_editVal.setValue( self.Y0[0] )
            if degreesOfFreedomToAnimate[0].rotational():
                self.form.label_2.setText('Edit: (radians)')
                self.form.label_3.setHidden(False)
                self.form.doubleSpinBox_degRad.setHidden(False)
                self.form.doubleSpinBox_degRad.setValue( self.Y0[0]*180/numpy.pi )
            else:
                self.form.label_2.setText('Edit:')
                self.form.label_3.setHidden(True)
                self.form.doubleSpinBox_degRad.setHidden(True)
                self.form.doubleSpinBox_degRad.setValue(0)
        else:
            FreeCAD.Console.PrintError('Nother to adjust! Constraint system has no degrees of freedom.')
            FreeCADGui.Control.closeDialog()

    def selectionMade(self):
        D_to_animate = []
        for index, d in enumerate( self.constraintSystem.degreesOfFreedom ):
            item = self.form.listWidget_DOF.item(index)
            if item.isSelected():
                D_to_animate.append( d )
        if len(D_to_animate) > 0:
            self._fillForm( D_to_animate)

    def updateSelected(self):
        D_to_animate = []
        for index, d in enumerate( self.constraintSystem.degreesOfFreedom ):
            item = self.form.listWidget_DOF.item(index)
            if item.isSelected():
                self.constraintSystem.degreesOfFreedom[index].setValue(self.form.doubleSpinBox_editVal.value())
                self.constraintSystem.update()
                self.constraintSystem.variableManager.updateFreeCADValues( self.constraintSystem.variableManager.X )
                self.form.doubleSpinBox_editVal.setValue( 0.0 )
        self.form.listWidget_DOF.clear();
        for i, d in enumerate(self.constraintSystem.degreesOfFreedom):
            item = QtGui.QListWidgetItem('%i. %s' % (i+1, str(d)[1:-1].replace('DegreeOfFreedom ','')), self.form.listWidget_DOF)


