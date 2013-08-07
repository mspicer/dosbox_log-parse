########################################################################
# parse.py - Script to parse Dosbox log file and output in a useful way. 
# Author: Mike Spicer 
# Copyright (c) 2013 Mike Spicer <mls@mikespicer.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
########################################################################
import sys
import os

def main(argv):
	path = os.path.dirname(os.path.abspath(__file__))
	print "*****"+ path
	print argv
	if len(argv) > 1:
		fname = argv
	else:
		fname = "LOGCPU.TXT" #os.path.join(os.path.abspath(path), "CPULOG.TXT") #path+"CPULOG.TXT"

	print fname
#	search(fname, ['EDX:00000378', 'in '])
	#search(fname, ['in   al,40'])
	buildTreeHTML("subset.txt")

def buildTreeHTML(fname):
	HTML = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<title>dosbox instructions sample</title>
		<meta charset="utf-8" />
		<style>
		.css-treeview ul,.css-treeview li{{padding:0;margin:0;list-style:none}}
		.css-treeview input{{position:absolute;opacity:0}}
		.css-treeview{{font:normal 11px "Segoe UI", Arial, Sans-serif;-moz-user-select:none;-webkit-user-select:none;user-select:none}}
		.css-treeview a{{color:#00f;text-decoration:none}}
		.css-treeview a:hover{{text-decoration:underline}}
		.css-treeview input+label+ul{{margin:0 0 0 22px}}
		.css-treeview input~ ul{{display:none}}
		.css-treeview label,.css-treeview label::before{{cursor:pointer}}
		.css-treeview input:disabled+label{{cursor:default;opacity:.6}}
		.css-treeview input:checked:not(:disabled)~ ul{{display:block}}
		.css-treeview label,.css-treeview label::before{{background:url(icons.png) no-repeat}}
		.css-treeview label,.css-treeview a,.css-treeview label::before{{display:inline-block;height:16px;line-height:16px;, vertical-align:middle}}
		.css-treeview label{{background-position:18px 0}}
		.css-treeview label::before{{content:"";width:16px;margin:0 22px 0 0;vertical-align:middle;background-position:0 -32px}}
		.css-treeview input:checked+label::before{{background-position:0 -16px}}
		@media screen and (-webkit-min-device-pixel-ratio:0){{.css-treeview {{ -webkit-animation:webkit-adjacent-element-selector-bugfix infinite 1s}}
		@-webkit-keyframes webkit-adjacent-element-selector-bugfix{{from {{ padding:0}}
		to{{padding:0}}
	}}
	</style>
	</head>
	<body>
		{body}
	</body>
</html>
	"""
	MY_TREE = """
		<div class="css-treeview">
			{basetree}
		</div>
	"""
	SUBTREE = """
		<ul>{subtree}</ul>
	"""

	NODE = """
		<li><input type="checkbox" name="" id="" /><label for="">{data}</label>{child}</li>
	"""
	NODEC = """
		<li><input type="checkbox" name="" id="" checked="checked"/><label for="">{data}</label>{child}</li>
	"""

#	body=''
#	base = ''
	nodes = ''
	depth = 0
	parent_nodes = [] # stack of parent strings
	ite = 0
	#for f in open(fname):
	ofile = open(fname, "rb")
	while True:
		f = ofile.readline()
		if not f: 
			print "Iteration: " +str(ite)+ f

			break
		print "Iteration: "+str(ite) + "  | Depth: " + str(depth) + " LEN(nodes): " + str(len(nodes))
		ite += 1
		if "call " in f: # create a new subtree
			depth+=1
			nodes += NODE.format(data=f, child="{subt-d"+str(depth)+"}")
			print "Insert: {subt-d"+str(depth)+"}"
			parent_nodes.append(nodes)
			nodes = ''


		elif len(parent_nodes)>0 and "ret" in f: # returning from a subtree
			nodes += NODEC.format(data=f, child="") # add the return opcode to the list
			subt = SUBTREE.format(subtree=nodes) # add the current node list to the subtree
			nodes = parent_nodes.pop() # restore our node state before the subtree
			print "Replace subt-d"+str(depth)
			node_dict = {"subt-d"+str(depth):subt} # construct the node dictionary that has the entire subtree
			nodes = nodes.format(**node_dict) # replace the placeholder with the subtree
			depth-=1 # decrement the call stack
			subt = ''

		else: 
			nodes += NODEC.format(data=f, child='')

	
	if depth>0:
		subt = SUBTREE.format(subtree=nodes) # add the current node list to the subtree
		nodes = parent_nodes.pop() # restore our node state before the subtree
		print "*Interrupted Call Stack subt-d"+str(depth)
		node_dict = {"subt-d"+str(depth):subt} # construct the node dictionary that has the entire subtree
		nodes = nodes.format(**node_dict) # replace the placeholder with the subtree
		depth-=1 # decrement the call stack

	ofile.close()
	body = MY_TREE.format(basetree=nodes)
	fo = open('awesomeTree.html','w')
	fo.write(HTML.format(body=body))
	fo.close()

	
def search(fname, terms):
	LISTMAX = 4
	l_cnt = 0
	p_inst = []
	f = open(fname)
	#for l in f:
	while True:
		l = f.readline()
		# break if there are not any more lines
		if not l: break

		#if "EDX:00000378" in l and "in " in l:
		if all(t in l for t in terms):
			print "-- New Iteration --"
			# print previous N items
			for inst in p_inst:
				print inst
			# print found instruction
			print l

			# print future instructions
			current_line = f.tell()
			for x in range(LISTMAX):
				print f.readline()
			# reset the file position to where we started
			f.seek(current_line)


		else:	
			p_inst.append(l)
			l_cnt+=1
			if l_cnt > LISTMAX:
				p_inst.pop(0)
				l_cnt-=1


if __name__ == "__main__":
    sys.exit(main(sys.argv))