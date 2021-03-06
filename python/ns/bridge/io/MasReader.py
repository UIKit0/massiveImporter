# The MIT License
#	
# Copyright (c) 2008 James Piechota
#	
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import os.path

import ns.bridge.data.MasSpec as MasSpec
import ns.bridge.data.Selection as Selection

def _handleTerrain( fileHandle, tokens, mas ):
	'''Load terrain information. For now only the terrain OBJ file is loaded'''
	for line in fileHandle:
		line = line.strip()
		if line == "End terrain":
			# End of terrain section. Parsing engine expects tokens for the
			# next line though, so get 'em and return
			#
			tokens = []
			try:
				tokens = fileHandle.next().strip.split()
			except:
				pass
			return tokens
		
		tokens = line.split()
		if tokens:
			if tokens[0] == "model":
				assert len(tokens) == 2
				mas.terrainFile = tokens[1]
			else:
				# skip the other tags for now
				pass
	return []

def _handlePlace( fileHandle, tokens, mas ):
	'''Load placement information. For now we only care about the CDL files.'''
	for line in fileHandle:
		line = line.strip()
		if line == "End place":
			# End of Place section. Parsing engine expects tokens for the
			# next line though, so get 'em and return
			#
			tokens = []
			try:
				tokens = fileHandle.next().strip.split()
			except:
				pass
			return tokens
				
		tokens = line.split()
		if tokens:
			if tokens[0] == "group":
				# ignore everything but CDL files.
				# Here's hoping that group statements only contain 3 lines
				# otherwise I gotta start looking at whitespace to figure
				# out when the group statement is done
				#
				id = int(tokens[1])
				name = tokens[2]
				for i in range(3):
					tokens = fileHandle.next().strip().split()
					if tokens[0] == "cdl" and len(tokens) > 1:
						mas.cdlFiles.append( MasSpec.CdlFile( tokens[1], name ) )
				# Create a group and add it to the groups array indexed
				# by its 'id'
				#
				group = MasSpec.Group( id, name )
				if id >= len(mas.groups):
					mas.groups.extend([ None ] * (id - len(mas.groups) + 1))
				mas.groups[id] = group
			elif tokens[0] == "selection":
				if len(tokens) != 2:
					continue
				name = tokens[1]
				selection = Selection.Selection()
				line = fileHandle.next().strip()
				while line != "end selection":
					tokens = line.split()
					if not tokens:
						continue
					selection.addRanges(tokens)
					line = fileHandle.next().strip()
				mas.selectionGroup.addSelection( name, selection )
			elif tokens[0] == "generator":
				line = fileHandle.next().strip()
				while line != "end generator":
					tokens = line.split()
					if not tokens:
						continue
					if tokens[0] == "number":
						mas.numAgents += int(tokens[1])
					line = fileHandle.next().strip()
			elif tokens[0] == "lock":
				# lock id [p0.x p0.y p0.z] [p.x p.y p.z] [n.x n.y n.z] [r.x r.y r.z] h d flow terrain
				#
				# For now we only care about the associated group id and
				# position
				group = int(tokens[1])
				position = ( float(tokens[2].replace("[", "")), float(tokens[3]), float(tokens[4].replace("]", "")) )
				mas.locators.append(MasSpec.Locator(group, position))
			else:
				# skip the other tags for now
				pass
	return []

def read(masFile):
	'''Load information about the Massive setup'''
 
	mas = MasSpec.MasSpec()
	if isinstance(masFile, basestring):
		mas.setMasFile(masFile)
		fileHandle = open(masFile, "r")
	else:
		fileHandle = masFile

 	try:
 		try:
			for line in fileHandle:
				tokens = line.strip().split()
		 		if tokens:
		 			if tokens[0] == "Terrain":
		 				tokens = _handleTerrain( fileHandle, tokens, mas )
		 			elif tokens[0] == "Place":
		 				tokens = _handlePlace( fileHandle, tokens, mas )
		 			else:
		 				pass
		finally:
		 	if fileHandle != masFile:
		 		# I opened fileHandle so I have to close it
		 		fileHandle.close()
	except:
	 	print >> sys.stderr, "Error reading MAS file."
	 	raise
	 	
 	return mas
 

        
