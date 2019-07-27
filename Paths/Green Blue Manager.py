#MenuTitle: Blue Green Manager
# -*- coding: utf-8 -*-
__doc__="""
Define an angle above which a node will be set to blue, below which it will be set to green.
"""

import vanilla
from math import degrees, atan2

def angle( firstPoint, secondPoint ):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return degrees(atan2(yDiff,xDiff))

class GreenBlueManager( object ):
	def __init__( self ):
		self.Tool = GlyphsPathPlugin.alloc().init()
		
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 245
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Green Blue Manager", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.GreenBlueManager.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 5, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*2), u"Validates the connection state of nodes, green vs. blue, according to the angle between them. Optionally corrects green/blue state and handles.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2.5
		
		self.w.thresholdAngleText = vanilla.TextBox( (inset, linePos, 110, 14), u"Threshold Angle:", sizeStyle='small', selectable=True )
		self.w.thresholdAngle = vanilla.EditText( (inset+110, linePos-2, -inset, 19), "11", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.completeFont = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Process complete font (otherwise selection)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.completeFont.getNSButton().setToolTip_("If checked, will go through all active (i.e., master, brace and bracket) layers of all glyphs. If unchecked, will only go through selected layers. Careful: can take a minute.")
		linePos += lineHeight
		
		self.w.fixGreenBlue = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Fix green vs. blue connection for on-curves", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.fixGreenBlue.getNSButton().setToolTip_("Sets the green/blue state of an on-curve node according to the connection angle. Any connection below the threshold angle will be green, otherwise blue. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle.")
		linePos += lineHeight
		
		self.w.realignHandles = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Realign handles attached to green nodes", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.realignHandles.getNSButton().setToolTip_("If a BCP (grey handle) follows a green node, it will be aligned to the previous two points. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle.")
		linePos += lineHeight
		
		self.w.reportInMacroWindow = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Detailed report in Macro window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportInMacroWindow.getNSButton().setToolTip_("If enabled, will output a detailed report in Window > Macro Panel.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		# linePos+=lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Treat Points", sizeStyle='regular', callback=self.GreenBlueManagerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Set Green Or Blue According To Angle' could not load preferences. Will resort to defaults"
		
		self.checkGUI()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def checkGUI(self, sender=None):
		if not self.w.realignHandles.get() and not self.w.fixGreenBlue.get():
			self.w.runButton.setTitle("New Tab")
		else:
			self.w.runButton.setTitle("Treat Points")
		
	def SavePreferences( self, sender=None ):
		self.checkGUI(sender=sender)
		try:
			Glyphs.defaults["com.mekkablue.GreenBlueManager.thresholdAngle"] = self.w.thresholdAngle.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.completeFont"] = self.w.completeFont.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"] = self.w.fixGreenBlue.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"] = self.w.realignHandles.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"] = self.w.reportInMacroWindow.get()
		except:
			return False
			
		return True

	def LoadPreferences( self, sender=None ):
		self.checkGUI(sender=sender)
		try:
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.thresholdAngle", 11 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.completeFont", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.fixGreenBlue", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.realignHandles", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.reportInMacroWindow", 1 )
			self.w.thresholdAngle.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.thresholdAngle"] )
			self.w.completeFont.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.completeFont"] )
			self.w.fixGreenBlue.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"] )
			self.w.realignHandles.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"] )
			self.w.reportInMacroWindow.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"] )
		except:
			return False
			
		return True
	
	def realignLayer(self, thisLayer):
		moveForward = NSPoint( 1, 0 )
		moveBackward = NSPoint( -1, 0 )
		noModifier = NSNumber.numberWithUnsignedInteger_(0)
		layerCount = 0
		
		if thisLayer:
			for thisPath in thisLayer.paths:
				oldPathCoordinates = [n.position for n in thisPath.nodes]
				for thisNode in thisPath.nodes:
					if thisNode.type == GSOFFCURVE:
						oldPosition = NSPoint(thisNode.position.x, thisNode.position.y)
						selectedNode = NSMutableArray.arrayWithObject_(thisNode)
						thisLayer.setSelection_( selectedNode )
						self.Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_( thisLayer, thisLayer, moveForward, noModifier )
						self.Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_( thisLayer, thisLayer, moveBackward, noModifier )
				
				for i,coordinate in enumerate(oldPathCoordinates):
					if thisPath.nodes[i].position != coordinate:
						layerCount += 1
				
						# put handle back if not desired by user:
						if not Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"]:
							thisPath.nodes[i].position = coordinate
		thisLayer.setSelection_( () )
		
		if Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"]:
			if layerCount:
				if Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"]:
					print u"   ⚠️ Realigned %i handle%s." % ( layerCount, "" if layerCount==1 else "s" )
				else:
					print u"   ❌ %i handle%s are unaligned." % ( layerCount, "" if layerCount==1 else "s" )
			else:
				print u"   ✅ All BCPs OK."

		return layerCount
	
	def fixConnectionsOnLayer(self, thisLayer):
		thresholdAngle = float(Glyphs.defaults["com.mekkablue.GreenBlueManager.thresholdAngle"])
		layerCount = 0
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				if thisNode.type == OFFCURVE:
					hotNode = None
					if thisNode.prevNode.type != OFFCURVE:
						hotNode = thisNode.prevNode
					elif thisNode.nextNode.type != OFFCURVE:
						hotNode = thisNode.nextNode
					if not hotNode is None:
						angleDiff = abs( angle(hotNode.prevNode, hotNode) - angle(hotNode, hotNode.nextNode) )
						if angleDiff <= thresholdAngle and hotNode.connection != GSSMOOTH:
							layerCount += 1
							if Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"]:
								hotNode.connection = GSSMOOTH
						elif angleDiff > thresholdAngle and hotNode.connection != GSSHARP:
							layerCount += 1
							if Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"]:
								hotNode.connection = GSSHARP
		
		if Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"]:
			print "%s, layer '%s'" % (thisLayer.parent.name, thisLayer.name)
			if layerCount:
				if Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"]:
					print "   ⚠️ Fixed %s connection%s" % ( layerCount, "" if layerCount==1 else "s" )
				else:
					print "   ❌ %s wrong connection%s" % ( layerCount, "" if layerCount==1 else "s" )
			else:
				print "   ✅ All connections OK."
		
		return layerCount
	
	def GreenBlueManagerMain( self, sender ):
		try:
			thisFont = Glyphs.font
			
			if not thisFont:
				Message(title="Green Blue Manager Error", message="Could not determine a frontmost font. The script requires at least one open font.", OKButton=None)
			else:
				if Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"]:
					Glyphs.clearLog()
			
				# determine which layers to process:
				if Glyphs.defaults["com.mekkablue.GreenBlueManager.completeFont"]:
					layersToBeProcessed = []
					for thisGlyph in thisFont.glyphs:
						for thisLayer in thisGlyph.layers:
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								layersToBeProcessed.append(thisLayer)
				else:
					layersToBeProcessed = Glyphs.font.selectedLayers
			
				numberOfLayers = len(layersToBeProcessed)
				affectedLayersFixedConnections = []
				affectedLayersRealignedHandles = []
			
				# process layers:
				for i, thisLayer in enumerate(layersToBeProcessed):
					self.w.progress.set(100.0/numberOfLayers*i)
					thisGlyph = thisLayer.parent
				
					thisGlyph.beginUndo() # begin undo grouping
				
					numberOfFixes = self.fixConnectionsOnLayer( thisLayer )
					if numberOfFixes and numberOfLayers:
						affectedLayersFixedConnections.append( thisLayer )
				
					numberOfAligns = self.realignLayer( thisLayer )
					if numberOfAligns and numberOfLayers:
						affectedLayersRealignedHandles.append( thisLayer )
				
					thisGlyph.endUndo()   # end undo grouping
			
				print "\nDone. Processed %i layers." % numberOfLayers
				self.w.progress.set(100)
				
				if Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"]:
					Glyphs.showMacroWindow()
			
				if numberOfLayers == 1:
					if Glyphs.font.currentTab:
						Glyphs.font.currentTab.forceRedraw()
				else:
					onlyReport = not Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"] and not Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"]
					if onlyReport:
						titles = ("Wrong green/blue","Unaligned BCPs")
					else:
						titles = ("Fixed green/blue","Aligned BCPs")

					# opens new Edit tab:
					newTab = thisFont.newTab()
					if numberOfFixes:
						newTab.text += "%s:\n" % titles[0]
						newTab.layers += affectedLayersFixedConnections
						newTab.text += "\n\n"
					if numberOfAligns:
						newTab.text += "%s:\n" % titles[1]
						newTab.layers += affectedLayersRealignedHandles
				
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "\nGreen Blue Manager Error: %s" % e
			import traceback
			print traceback.format_exc()
			print

GreenBlueManager()