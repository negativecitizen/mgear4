from functools import partial

from mgear.shifter.component import guide
from mgear.core import pyqt
from mgear.vendor.Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget

from . import settingsUI as sui


# guide info
AUTHOR = "anima inc."
URL = "www.studioanima.co.jp"
EMAIL = ""
VERSION = [1, 1, 0]
TYPE = "chain_IK_spline_variable_FK_01"
NAME = "chain"
DESCRIPTION = "IK chain with a spline driven joints. And variable number of \
FK controls. \nIK is master, FK Slave"

##########################################################
# CLASS
##########################################################


class Guide(guide.ComponentGuide):
    """Component Guide Class"""

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    def postInit(self):
        """Initialize the position for the guide"""

        self.save_transform = ["root", "#_loc"]
        self.save_blade = ["blade"]
        self.addMinMax("#_loc", 1, -1)

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)
        self.blade = self.addBlade("blade", self.root, self.locs[0])

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)
        self.addDispCurve("crvRef", centers, 3)

    def addParameters(self):
        """Add the configurations settings"""

        self.pNeutralPose = self.addParam("neutralpose", "bool", True)
        self.pOverrideNegate = self.addParam("overrideNegate", "bool", False)
        self.pfkNb = self.addParam("fkNb", "long", 5, 1)

        self.pPosition = self.addParam("position", "double", 0, 0, 1)
        self.pMaxStretch = self.addParam("maxstretch", "double", 1, 1)
        self.pMaxSquash = self.addParam("maxsquash", "double", 1, 0, 1)
        self.pSoftness = self.addParam("softness", "double", 0, 0, 1)

        self.pIKSolver = self.addEnumParam(
            "ctlOrientation", ["xz", "yz", "zx"], 0
        )

        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)

##########################################################
# Setting Page
##########################################################


class settingsTab(QtWidgets.QDialog, sui.Ui_Form):

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)
        self.setupUi(self)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):

    def __init__(self, parent=None):
        self.toolName = TYPE
        # Delete old instances of the componet settings window.
        pyqt.deleteInstances(self, MayaQDockWidget)

        super(self.__class__, self).__init__(parent=parent)
        self.settingsTab = settingsTab()

        self.setup_componentSettingWindow()
        self.create_componentControls()
        self.populate_componentControls()
        self.create_componentLayout()
        self.create_componentConnections()

    def setup_componentSettingWindow(self):
        self.mayaMainWindow = pyqt.maya_main_window()

        self.setObjectName(self.toolName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(TYPE)
        self.resize(350, 350)

    def create_componentControls(self):
        return

    def populate_componentControls(self):
        """Populate Controls

        Populate the controls values from the custom attributes of the
        component.

        """
        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        # populate component settings
        self.populateCheck(self.settingsTab.overrideNegate_checkBox,
                           "overrideNegate")

        self.settingsTab.fkNb_spinBox.setValue(
            self.root.attr("fkNb").get())
        self.settingsTab.softness_slider.setValue(
            int(self.root.attr("softness").get() * 100))
        self.settingsTab.position_spinBox.setValue(
            int(self.root.attr("position").get() * 100))
        self.settingsTab.position_slider.setValue(
            int(self.root.attr("position").get() * 100))
        self.settingsTab.softness_spinBox.setValue(
            int(self.root.attr("softness").get() * 100))
        self.settingsTab.maxStretch_spinBox.setValue(
            self.root.attr("maxstretch").get())
        self.settingsTab.maxSquash_spinBox.setValue(
            self.root.attr("maxsquash").get())

        self.settingsTab.ctlOri_comboBox.setCurrentIndex(
            self.root.attr("ctlOrientation").get()
        )

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.overrideNegate_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.overrideNegate_checkBox,
                    "overrideNegate"))
        self.settingsTab.fkNb_spinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.fkNb_spinBox,
                    "fkNb"))
        self.settingsTab.softness_slider.valueChanged.connect(
            partial(self.updateSlider,
                    self.settingsTab.softness_slider,
                    "softness"))
        self.settingsTab.softness_spinBox.valueChanged.connect(
            partial(self.updateSlider,
                    self.settingsTab.softness_spinBox,
                    "softness"))
        self.settingsTab.position_slider.valueChanged.connect(
            partial(self.updateSlider,
                    self.settingsTab.position_slider,
                    "position"))
        self.settingsTab.position_spinBox.valueChanged.connect(
            partial(self.updateSlider,
                    self.settingsTab.position_spinBox,
                    "position"))
        self.settingsTab.maxStretch_spinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.maxStretch_spinBox,
                    "maxstretch"))
        self.settingsTab.maxSquash_spinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.maxSquash_spinBox,
                    "maxsquash"))

        self.settingsTab.ctlOri_comboBox.currentIndexChanged.connect(
            partial(
                self.updateComboBox,
                self.settingsTab.ctlOri_comboBox,
                "ctlOrientation",
            )
        )

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
