#MenuTitle: Compare Font Info > Instances
# -*- coding: utf-8 -*-
__doc__="""
Detailed report of Font Info > Instances for the two frontmost fontsand outputs a report in the Macro Window.
"""

import GlyphsApp
from compare import *

thisFont = Glyphs.fonts[0] # frontmost font
otherFont = Glyphs.fonts[1] # second font
thisFileName = thisFont.filepath.pathComponents()[-1]
otherFileName = otherFont.filepath.pathComponents()[-1]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print "Comparing Font Info > Instances for:".upper()
print
print "1. %s (family: %s)" % (thisFileName, thisFont.familyName)
print "   %s" % thisFont.filepath
print "2. %s (family: %s)" % (otherFileName, otherFont.familyName)
print "   %s" % otherFont.filepath
print 

for thisInstance, otherInstance in zip(thisFont.instances, otherFont.instances):
	print 
	print 
	print "   COMPARING INSTANCES:"
	print "   A. %s%s" % (
		"%s "%thisInstance.familyName if thisInstance.familyName else "",
		thisInstance.name,
		)
	print "   B. %s%s" % (
		"%s "%thisInstance.familyName if thisInstance.familyName else "",
		otherInstance.name,
		)
	print
	
	keyValueDict= {
		"Weight": (thisInstance.weight, otherInstance.weight),
		"Width": (thisInstance.width, otherInstance.width),
		"Name": (thisInstance.name, otherInstance.name),
	}
	for key in keyValueDict:
		thisValue, otherValue = keyValueDict[key]
		if thisValue == otherValue:
			print u"✅ %s value is the same: '%s'" % (key, thisValue)
		else:
			print u"⚠️ Different %s values:" % key
			print u"   A. '%s' in %s" % (thisValue, thisInstance.name)
			print u"   B. '%s' in %s" % (otherValue, otherInstance.name)
	
	if not len(thisFont.axes) == len(otherFont.axes):
		print u"❌ Different number of axes between fonts."
	else:
		for i in range(len(thisFont.axes)):
			thisValue, otherValue = thisInstance.axes[i], otherInstance.axes[i]
			if thisValue == otherValue:
				print u"✅ axis %i (%s/%s) value is the same: %i" % (
					i,
					thisFont.axes[i]["Tag"], otherFont.axes[i]["Tag"],
					thisValue,
					)
			else:
				print u"⚠️ Different values for axis %i (%s/%s):" % (
					i,
					thisFont.axes[i]["Tag"], otherFont.axes[i]["Tag"],
				)
				print u"   A. %.1f in %s" % (thisValue, thisInstance.name)
				print u"   B. %.1f in %s" % (otherValue, otherInstance.name)
		
	
	
	# count parameters:
	compareCount(
		"Custom Parameters", 
		len(thisInstance.customParameters), len(otherInstance.customParameters),
		thisInstance.name, otherInstance.name,
		)

		
	# comparing parameters:
	theseParameters = [p.name for p in thisInstance.customParameters]
	otherParameters = [p.name for p in otherInstance.customParameters]
	thisSet, otherSet = compareLists(theseParameters, otherParameters)
	if thisSet or otherSet:
		if otherSet:
			print u"❌ Parameters not in (A) %s:" % thisInstance.name
			print "   %s" % ("\n   ".join(otherSet))
		if thisSet:
			print u"❌ Parameters not in (B) %s:" % otherInstance.name
			print "   %s" % ("\n   ".join(thisSet))
	else:
		print u"✅ Same structure of parameters in both instances."
	
	# detailed comparison:
	for thisParameterName in [p.name for p in thisInstance.customParameters]:
		thisParameter = thisInstance.customParameters[thisParameterName]
		otherParameter = otherInstance.customParameters[thisParameterName]
		if otherParameter:
			if thisParameter == otherParameter:
				parameterContent = cleanUpAndShortenParameterContent(thisParameter)
				print u"💚 Parameter %s: same value (%s). OK." % (thisParameterName, parameterContent)
			else:
				thisContent = cleanUpAndShortenParameterContent(thisParameter)
				otherContent = cleanUpAndShortenParameterContent(otherParameter)
				print u"⚠️ Parameter %s: different values." % thisParameterName
				print u"    A. %s in %s" % (thisContent, thisInstance.name)
				print u"    B. %s in %s" % (otherContent, otherInstance.name)
				
				