#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, gi, subprocess, time, serial, usbtmc, numpy
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
from gpiozero import LED
from binascii import unhexlify
from time import sleep
	
class Thermocouple:
  
    def __init__(self):
	self.CurrentTemperature = subprocess.check_output("sudo GetTemperature", shell=True)
	
    def GetTemperature(self):
	try:
	    self.CurrentTemperature = subprocess.check_output("sudo GetTemperature", shell=True)
	    return True
	except ValueError:
	    return True
	
class Multimeter:
    
    def __init__(self):
	self.instr = usbtmc.Instrument(10893, 4865) #Hardwired to connect to Agilent 34461A
	
    def getVoltage(self):
	#tmpValueStr = self.instr.ask("MEAS:VOLT:DC? DEF,MIN") #Takes too long which crashes code
	tmpValueStr = self.instr.ask("MEAS:VOLT:DC? 0.1,0.003")
	if (int(tmpValueStr[-3:]) > 30):
	    tmpValueStr = self.instr.ask("MEAS:VOLT:DC? 1,0.003")
	    
	    if (int(tmpValueStr[-3:]) > 30):
		tmpValueStr = self.instr.ask("MEAS:VOLT:DC? 10,0.003")
		
		if (int(tmpValueStr[-3:]) > 30):
		    tmpValueStr = self.instr.ask("MEAS:VOLT:DC? 100,0.003")
		    
	tmpValue = float(tmpValueStr)
	  
	return tmpValue
	
class Multiplexer:
  
    def __init__(self):
	self.CurrentInput = 0
	self.Pin0 = LED(20)
	#self.Pin1 = LED(6)
	#self.Pin2 = LED(13)
	#self.Pin3 = LED(19)
	self.EnablePin = LED(26)
	
    def SetEnableON(self):
	self.EnablePin.on()
	
    def SetEnableOFF(self):
	self.EnablePin.off()
	
    def SetInput(self, newInput):
	self.CurrentInput = newInput
	tmpNewInput = "{0:04b}".format(newInput)
	
	if (tmpNewInput[3]=='1'):
	    self.Pin0.on()
	else:
	    self.Pin0.off()
	    
	if (tmpNewInput[2]=='1'):
	    self.Pin1.on()
	else:
	    self.Pin1.off()
	    
	if (tmpNewInput[1]=='1'):
	    self.Pin2.on()
	else:
	    self.Pin2.off()
	    
	if (tmpNewInput[0]=='1'):
	    self.Pin3.on()
	else:
	    self.Pin3.off()
	    
    def GetInput(self):
	tmpInput = '0000'
	
	if (self.Pin0.value):
	    tmpInput[3] = '1'
	    
	if (self.Pin1.value):
	    tmpInput[2] = '1'
	    
	if (self.Pin2.value):
	    tmpInput[1] = '1'
	    
	if (self.Pin3.value):
	    tmpInput[0] = '1'
	    
	self.CurrentInput = int(tmpInput,2)
      
class SamplePanel:

    def __init__(self, gtkWindow, panelID):
	self.PanelID = panelID
	self.SampleName = "Sample_" + str(panelID)
	self.Resistor = float('1e6')
	self.MuxInput = 0
	self.MeasuredVoltage = 0
	self.CalculatedCurrent = 0
	self.PanelON = False
	self.SampleNameEntry = gtkWindow.glade.get_object("SampleName_" + str(panelID))
	self.R1kOhm = gtkWindow.glade.get_object("1kOhm_" + str(panelID))
	self.R100kOhm = gtkWindow.glade.get_object("100kOhm_" + str(panelID))
	self.R1MOhm = gtkWindow.glade.get_object("1MOhm_" + str(panelID))
	self.R10MOhm = gtkWindow.glade.get_object("10MOhm_" + str(panelID))
	self.MeasuredVoltageEntry = gtkWindow.glade.get_object("MeasuredVoltage_" + str(panelID))
	self.CalculatedCurrentEntry = gtkWindow.glade.get_object("CalculatedCurrent_" + str(panelID))
	self.MuxInputComboBox = gtkWindow.glade.get_object("MuxInput_" + str(panelID))
	
	self.R1MOhm.set_active(True)
	self.MuxInput = int(self.MuxInputComboBox.get_active_text())
	self.SampleName = self.SampleNameEntry.props.text
	
	if (self.SampleName==""):
	    self.SampleName = "Sample_" + str(panelID)
	    self.SampleNameEntry.props.text = self.SampleName


class DataLogger:
  
    def __init__(self):
	self.StartLogging = False
	self.SaveFolder = '/home/pi/Github/CurrentLeakTest/Data'
	self.AutoFileName = True
	self.FileName = 'CurrentLeakTest_20170105'
	  
	
class widgetIDs(object):
  
    def __init__(self, gtkWindow):
	self.ControlPanel = gtkWindow.glade.get_object("ControlPanel")
	
	#Data logger
	self.dataLogPower_button = gtkWindow.glade.get_object("dataLogPower_button")
	self.dataLogChooseFolder = gtkWindow.glade.get_object("dataLogChooseFolder")
	self.dataLogAutoName_checkbutton = gtkWindow.glade.get_object("dataLogAutoName_checkbutton")
	self.dataLogFileNameEntry = gtkWindow.glade.get_object("dataLogFileNameEntry")
	
	#System status
	self.messageLine = gtkWindow.glade.get_object("messageLine")
	self.PBSTemperatureLabel = gtkWindow.glade.get_object("PBSTemperatureLabel")
	self.MasterPower_button = gtkWindow.glade.get_object("MasterPower_button")
	
	#Sample panels
	self.ONswitch_1 = gtkWindow.glade.get_object("ONswitch_" + str(1))
	self.ONswitch_2 = gtkWindow.glade.get_object("ONswitch_" + str(2))
	self.ONswitch_3 = gtkWindow.glade.get_object("ONswitch_" + str(3))
	self.ONswitch_4 = gtkWindow.glade.get_object("ONswitch_" + str(4))
	self.ONswitch_5 = gtkWindow.glade.get_object("ONswitch_" + str(5))
	self.ONswitch_6 = gtkWindow.glade.get_object("ONswitch_" + str(6))
	self.ONswitch_7 = gtkWindow.glade.get_object("ONswitch_" + str(7))
	self.ONswitch_8 = gtkWindow.glade.get_object("ONswitch_" + str(8))
	self.ONswitch_9 = gtkWindow.glade.get_object("ONswitch_" + str(9))
	#self. = gtkWindow.glade.get_object("")
  
class AgingSystemControl:

    def __init__(self):
        self.gladefile = "CurrentLeakTestControl.glade" 
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)
        
        #Create widget wtrusture
        self.wg = widgetIDs(self)
        self.wg.ControlPanel = self.glade.get_object("ControlPanel")
        self.wg.ControlPanel.show_all()
	self.wg.ControlPanel.connect("delete-event", Gtk.main_quit)
	#print(dir(self.glade.get_object("ThermostatManualPower_button").props))
	
	
	#Create bath status object
	self.thermocouple = Thermocouple()
	
	#Create test panel
	self.SamplePanels = list([0,0,0,0,0,0,0,0,0])
	
	#Create multiplexer object
	self.mux = Multiplexer()
	
	#Create multimeter object
	self.multimeter = Multimeter()
	
	
	#Create data logger object
	self.dLogger = DataLogger()
	#print(dir(self.wg.dataLogChooseFolder.props))
	self.dLogger.AutoFileName = self.wg.dataLogAutoName_checkbutton.get_active()
	self.wg.dataLogChooseFolder.set_filename(self.dLogger.SaveFolder)
	#Create timer to log every minute
	#GObject.timeout_add_seconds(15, self.LogData)
	GObject.timeout_add_seconds(10, self.MeasureVoltagesPeriodic)
	
	#connections
	self.wg.dataLogAutoName_checkbutton.connect("toggled", self.AutoFileNameCheckButton_callback)
	self.wg.dataLogPower_button.connect("notify::active", self.DataLogPower_button_callback)
	self.wg.dataLogChooseFolder.connect("selection-changed", self.DataLogChooseFolder_callback)
	
	self.wg.ONswitch_1.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_2.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_3.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_4.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_5.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_6.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_7.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_8.connect("notify::active", self.ONswitch_callback)
	self.wg.ONswitch_9.connect("notify::active", self.ONswitch_callback)
	
	#Create timer to update system
	self.Timer_Window_Update = GObject.timeout_add_seconds(1, self.WindowUpdate)
	
	
    #Define general use methods
    def is_number(self, s):
	try:
	    float(s)
	    return True
	except ValueError:
	    return False
	
    #Define callback for ONswitch
    def ONswitch_callback(self, switch, gparam):
	tmpPanelID = Gtk.Buildable.get_name(switch)
	if (switch.get_active()):
	    self.SamplePanels[int(tmpPanelID[9])-1] = SamplePanel(self, int(tmpPanelID[9]))
	    self.SamplePanels[int(tmpPanelID[9])-1].SampleNameEntry.set_sensitive(False)
	    self.SamplePanels[int(tmpPanelID[9])-1].MuxInputComboBox.set_sensitive(False)
	    self.SamplePanels[int(tmpPanelID[9])-1].PanelON = True
	    print("Panel = " + str(self.SamplePanels[int(tmpPanelID[9])-1].PanelID))
	    print("SampleName = " + self.SamplePanels[int(tmpPanelID[9])-1].SampleName)
	    print("MuxInput = " + str(self.SamplePanels[int(tmpPanelID[9])-1].MuxInput))
	    print("Measured Voltage [V] = " + str(self.SamplePanels[int(tmpPanelID[9])-1].MeasuredVoltage))
	else:
	    self.SamplePanels[int(tmpPanelID[9])-1].R1kOhm.set_active(True)
	    self.SamplePanels[int(tmpPanelID[9])-1].SampleNameEntry.set_sensitive(True)
	    self.SamplePanels[int(tmpPanelID[9])-1].MuxInputComboBox.set_sensitive(True)
	    self.SamplePanels[int(tmpPanelID[9])-1].PanelON = False
	    self.SamplePanels[int(tmpPanelID[9])-1].MeasuredVoltageEntry.props.label = "0.0"
	    self.SamplePanels[int(tmpPanelID[9])-1].CalculatedCurrentEntry.props.label = "0.0"
	    
	    self.SamplePanels[int(tmpPanelID[9])-1] = 0 #Remove handle from list

	    
    #Define callbacks for data logging module
    def DataLogPower_button_callback(self, switch, gparam):
	if (switch.get_active()):
	  self.dLogger.FileName = 'CurrentLeakTest_' + time.strftime("%Y%m%d_%H%M%S") + '.txt'
	  print self.dLogger.FileName
	self.dLogger.StartLogging = switch.get_active()
	
    def AutoFileNameCheckButton_callback(self, button):
	self.dLogger.AutoFileName = button.get_active()
	self.wg.dataLogFileNameEntry.props.visible = not button.get_active()
	
    def DataLogChooseFolder_callback(self, button):
	self.dLogger.SaveFolder =  self.wg.dataLogChooseFolder.get_filename()
	    
	  
    #Function to perform mesurement periodically
    def MeasureVoltagesPeriodic(self):
	tmpSuccess = self.MeasureVoltages()
	if tmpSuccess:
	    self.LogData()
	    self.MessageLineAndLog('Last measurement performed on ' + time.strftime("%Y%m%d %H%M%S"))
	return True
    
    #Function to perform voltage measurement
    def MeasureVoltages(self):
	#Update Sample Panel values
	for iPanel in range(0,9):
	    if (self.SamplePanels[iPanel] != 0):
		try:
		  #Should add shile loop to make sure mux is set properly
		    self.mux.SetInput(self.SamplePanels[iPanel].MuxInput)
		    sleep(0.1)
		    self.SamplePanels[iPanel].MeasuredVoltage = float(self.multimeter.getVoltage())
		    tmpActiveResistor = next(radio for radio in self.SamplePanels[iPanel].R1kOhm.get_group() if radio.get_active())
		    tmpActiveResistorValue = tmpActiveResistor.props.label
		    self.SamplePanels[iPanel].Resistor = float(tmpActiveResistorValue[0:3])
		    self.SamplePanels[iPanel].CalculatedCurrent = (self.SamplePanels[iPanel].MeasuredVoltage / self.SamplePanels[iPanel].Resistor * 10**9) #Calculate current and convert to nA
		except ValueError:
		    self.MessageLineAndLog('Voltage measurement failed in panel ' + str(iPanel+1) + ' on ' + time.strftime("%Y%m%d_%H%M%S"))
		    return False
	return True    
    
    #Function to periodically update window
    def WindowUpdate(self):
	try:
	    #Bath status
	    self.thermocouple.GetTemperature()
	    self.wg.PBSTemperatureLabel.props.label = self.thermocouple.CurrentTemperature[0:4] + ' C'
	
	    #Update Sample Panel values
	    for iPanel in range(0,9):
		if (self.SamplePanels[iPanel] != 0):
		    self.SamplePanels[iPanel].MeasuredVoltageEntry.props.label = str(self.SamplePanels[iPanel].MeasuredVoltage)
		    self.SamplePanels[iPanel].CalculatedCurrentEntry.props.label = str(self.SamplePanels[iPanel].CalculatedCurrent)
	
	    #Data logging
	    self.wg.dataLogPower_button.set_active(self.dLogger.StartLogging)
	    self.wg.dataLogFileNameEntry.props.visible = not self.dLogger.AutoFileName
	    return True
	except ValueError:
	    return True
    
    #Function to log data
    def LogData(self):
	if (self.dLogger.StartLogging):
	    for iPanel in range(0,9):
		if (self.SamplePanels[iPanel] != 0):
		    tmpFileName = self.dLogger.SaveFolder + '/' + self.SamplePanels[iPanel].SampleName
		    tmpLogFile = open(tmpFileName, 'a+')
		    tmpLogFile.write(time.strftime("%Y%m%d_%H%M%S") + '\t' + str(self.thermocouple.CurrentTemperature[0:4]) + '\t' + str(self.SamplePanels[iPanel].MeasuredVoltage) + '\t' + str(self.SamplePanels[iPanel].Resistor) + '\t' + str(self.SamplePanels[iPanel].MuxInput) + '\n')
		    tmpLogFile.close()
		    
     #Function to log data
    def MessageLineAndLog(self, strMessage):
	self.wg.messageLine.props.label = strMessage
	if (self.dLogger.StartLogging):
	  tmpFileName = self.dLogger.SaveFolder + '/' + self.dLogger.FileName
	  tmpLogFile = open(tmpFileName, 'a+')
	  tmpLogFile.write(time.strftime("%Y%m%d_%H%M%S") + ' \t' + strMessage + '\n')
	  tmpLogFile.close()

if __name__ == "__main__":
    try:
        win = AgingSystemControl()
	Gtk.main()
    except KeyboardInterrupt:
        pass

