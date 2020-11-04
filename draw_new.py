#yuansc <yuansicheng@ihep.ac.cn>

import ROOT as rt
import time
import os
import numpy as np


def readTree(path):
	print("readTree: reading " + path)
	try:
		myfile = rt.TFile(path)
	except:
		print("can not open file: " + path)
		return False
	tree = myfile.Get('DataCollSvc')
	entries = tree.GetEntriesFast()
	return myfile, tree, entries

def getBranchData(tree, entries, branch_name = ''):
	#if branch_name not in tree
	if branch_name not in [b.GetName() for b in list(tree.GetListOfBranches())]:
		print("getBranchData: can not find a branch named " + branch_name)
		return False

	data = []
	for i in range(entries):
		tree.GetEntry(i)
		exec("data.append(list(tree." + branch_name + "))")
		#exec("print(i, tree." + branch_name + ")")
	return data

def flattenBranchData(data):
	if not data:
		print("flattenBranchData: error")
		return False

	data_flatten = []
	for d in data:
		data_flatten += d
	return data_flatten

def list2TVector(li):
	v = rt.TVector(0, len(li)-1)
	for i in range(len(li)):
		v[i] = li[i]
	return v

def createTGraph(x, y, title="", line_color=1, line_width=1, x_axis_range=None, 
	y_axis_range=None, x_axis_title="", y_axis_title="", marker_size=0.5, 
	marker_color=1, marker_style=None):
	print("createTGraph: creating TGraph " + title)

	x_vector = list2TVector(x)
	y_vector = list2TVector(y)

	g = rt.TGraph(x_vector, y_vector)
	g.SetLineColor(line_color)
	g.SetLineWidth(line_width)

	if marker_style:
		g.SetMarkerStyle(marker_style)

	g.SetMarkerSize(marker_size)
	g.SetMarkerColor(marker_color)

	x_axis = g.GetXaxis()
	y_axis = g.GetYaxis()

	x_axis.SetTitle(x_axis_title)
	y_axis.SetTitle(y_axis_title)

	if x_axis_range:		
		x_axis.SetRangeUser(x_axis_range[0], x_axis_range[1])
	if y_axis_range:		
		y_axis.SetRangeUser(y_axis_range[0], y_axis_range[1])

	g.SetTitle(title)

	return g

def createLegend(d, position=[0.7,0.8,0.9,0.9]):
	print("createLegend: creating legend...")

	legend = rt.TLegend(position[0], position[1], position[2], position[3])

	for key in d.keys():
		legend.AddEntry(key, d[key])

	return legend


def getMomentums(path):
	with open(path+"job.sh","r") as f:
		for line in f.readlines():
			line = line.split("=")
			#print(line)
			if line[0] == "MOMENTUMS":
				return int(line[-1])

def mean(li, round_num=2):
	return round(sum(li)/len(li), round_num)

def var(li):
	return round(np.var(li), 2)

def substractLists(l1, l2):
	if len(l1) != len(l2):
		print("substractLists: len(l1) != len(l2)")
	return [l1[i]-l2[i] for i in range(len(l1))]

def getYaxisRange(li, factor=0.1):
	data = flattenBranchData(li)
	#print(li, data)
	l_max = max(data)
	l_min = min(data)
	l_diff = l_max - l_min
	return [l_min-factor*l_diff, l_max+factor*l_diff]

def findAbnormalPoints(x, li, factor=0.5):
	if factor >= 1:
		factor = 0.5
	li_mean = mean(li)
	lower_limit = li_mean - (li_mean - min(li))*factor
	upper_limit = li_mean + (max(li) - li_mean)*factor

	x_abnormal = []
	li_abnormal = []

	for i in range(len(li)):
		if li[i] < lower_limit or li[i] > upper_limit:
			x_abnormal.append(x[i])
			li_abnormal.append(li[i])

	return x_abnormal, li_abnormal


if __name__ == "__main__":
	path = "/junofs/users/yuansc/eos-test/20201010/data/"


	#2nd round, evtmax=100
	#dirs_range = ["2020-10-21-22-03-05", "2020-10-21-22-03-55"]
	#2nd round, evtmax=200
	#dirs_range = ["2020-10-21-22-04-07", "2020-10-21-22-04-59"]
	#2nd round, evtmax=300
	#dirs_range = ["2020-10-21-22-05-12", "2020-10-21-22-06-01"]
	#2nd round, evtmax=400
	#dirs_range = ["2020-10-21-22-06-14", "2020-10-21-22-07-00"]
	#2nd round, evtmax=500
	dirs_range = ["2020-10-21-22-07-13", "2020-10-21-22-08-01"]

	dirs = [path+x+'/' for x in os.listdir(path) if x>= dirs_range[0] and x<= dirs_range[1] ]
	print('\n'.join(dirs))

	evtmax = 0
	'''
	mode = "detsim"
	branches = ["t_outputsvc_write", "m_after_output-m_before_output" ,
	"DetSimAlg", "mem_after_DSA-mem_before_DSA" ]
	'''

	mode = 'elecsim'
	branches = ['t_outputsvc_write', 'm_after_output-m_before_output', 
				't_pmtsimalg', 'm_after_pmtsimalg-m_before_pmtsimalg', 
				't_pmtsimalg_getoneevent', 'm_after_getoneevent-m_before_getoneevent']

	means = {}
	not_completed = []
	for branch in branches:
		means[branch] = []

	for d in dirs:
		momentums = getMomentums(d)

		file_list = os.listdir(d)
		if mode in ["detsim", "elecsim"]:
			try:
				lustre_file = d + [x for x in file_list if mode in x and "lustre" in x][0]
				eos_file = d + [x for x in file_list if mode in x and "eos" in x][0]
				tmp_file = d + [x for x in file_list if mode in x and "tmp" in x][0]
			except:
				print(d,' not completed!!!')
				not_completed.append(d)
				continue

		f_lustre, t_lustre, e_lustre = readTree(lustre_file)
		f_eos, t_eos, e_eos = readTree(eos_file)
		f_tmp, t_tmp, e_tmp = readTree(tmp_file)

		evtmax = e_tmp

		for branch in branches:
			if '-' not in branch:
				lustre_data = flattenBranchData(getBranchData(t_lustre, e_lustre, branch_name=branch))
				eos_data = flattenBranchData(getBranchData(t_eos, e_eos, branch_name=branch))
				tmp_data = flattenBranchData(getBranchData(t_tmp, e_tmp, branch_name=branch))
			else:
				branch_split = branch.split('-')

				lustre_data_after = flattenBranchData(getBranchData(t_lustre, e_lustre, branch_name=branch_split[0]))
				eos_data_after = flattenBranchData(getBranchData(t_eos, e_eos, branch_name=branch_split[0]))
				tmp_data_after = flattenBranchData(getBranchData(t_tmp, e_tmp, branch_name=branch_split[0]))

				lustre_data_before = flattenBranchData(getBranchData(t_lustre, e_lustre, branch_name=branch_split[1]))
				eos_data_before = flattenBranchData(getBranchData(t_eos, e_eos, branch_name=branch_split[1]))
				tmp_data_before = flattenBranchData(getBranchData(t_tmp, e_tmp, branch_name=branch_split[1]))

				lustre_data = substractLists(lustre_data_after, lustre_data_before)
				eos_data = substractLists(eos_data_after, eos_data_before)
				tmp_data = substractLists(tmp_data_after, tmp_data_before)

			x = range(len(lustre_data))

			means[branch].append([momentums, mean(lustre_data), mean(eos_data),mean(tmp_data)])

			y_title = "ms"
			if branch[0] =='m':
				y_title = 'mb'

			c = rt.TCanvas("c1","lustre_eos",200,10,2000,800)
			g1 = createTGraph(x, lustre_data, title=branch+", momentums="+str(momentums), 
				line_color=4, y_axis_range=getYaxisRange([lustre_data, eos_data, tmp_data]), 
				x_axis_title="entry", y_axis_title=y_title, marker_color=4, marker_style=20)
			g2 = createTGraph(x, eos_data, line_color=2, marker_color=2, marker_style=20)
			g3 = createTGraph(x, tmp_data, line_color=3, marker_color=3, marker_style=20)
			legend = createLegend({
				g1:"lustre,mean="+str(means[branch][-1][1])+",var="+str(var(lustre_data)), 
				g2:"eos,mean="+str(means[branch][-1][2])+",var="+str(var(eos_data)), 
				g3:"tmp,mean="+str(means[branch][-1][3])+",var="+str(var(tmp_data))
				})

			g1.Draw("ALP")
			g2.Draw("LP SAME")
			g3.Draw("LP SAME")
			legend.Draw("SAME")

			c.SaveAs(d+mode+'_'+branch+".png")

	#draw means
	#def getFirstElement(li):
		#return li[0]
	for key in means.keys():
		value = means[key]
		value.sort(key=lambda x: x[0])	
		momentums = [x[0] for x in means[key]]
		lustre_mean = [x[1] for x in means[key]]
		eos_mean = [x[2] for x in means[key]]
		tmp_mean = [x[3] for x in means[key]]

		y_title = "ms"
		if key[0] =='m':
			y_title = 'mb'
		
		c = rt.TCanvas("c1","lustre_eos",200,10,1000,800)
		g1 = createTGraph(momentums, lustre_mean, title=key+"_mean, evtmax="+str(evtmax), line_color=4, 
			marker_style=20, marker_color=4, marker_size=2, 
			x_axis_title="momentums/mev", y_axis_title=y_title, 
			y_axis_range=getYaxisRange([lustre_mean, eos_mean, tmp_mean]))
		g2 = createTGraph(momentums, eos_mean, line_color=2, marker_style=20, 
			marker_color=2, marker_size=2)
		g3 = createTGraph(momentums, tmp_mean, line_color=3, marker_style=20, 
			marker_color=3, marker_size=2)
		legend = createLegend({g1:"lustre", g2:"eos", g3:"tmp"}, position=[0.15, 0.7, 0.35, 0.85])

		g1.Draw("ACP")
		g2.Draw("CP SAME")
		g3.Draw("CP SAME")
		legend.Draw("SAME")

		name = path.replace("data/", "means_fig/")
		name += mode+'_'+key+"_means_"+str(evtmax)+".png"
		c.SaveAs(name)

	print('\n')
	print('\n'.join(not_completed))



		


	'''
	#test
	f, t, e = readTree("/junofs/users/yuansc/eos-test/20201010/data/2020-10-13-20-55-25/sample_detsim_dcs_lustre_2020-10-13-20-55-25.root")
	print(f, t, e)
	data = getBranchData(t, e, branch_name="t_outputsvc_write")
	data_flatten = flattenBranchData(data)

	x = range(e)
	c = rt.TCanvas("c1","test",200,10,2560,1600)
	g = createTGraph(x,data_flatten)
	g.Draw("ALP")
	legend = createLegend({g:"test_legend"})
	legend.Draw()
	c.SaveAs("test.png")
	'''
