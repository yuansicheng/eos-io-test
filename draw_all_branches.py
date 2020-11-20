#yuansc <yuansicheng@ihep.ac.cn>
# -*- coding: utf-8 -*-

import ROOT as rt
import time
import os
import numpy as np
import argparse

from create_jobs import connectSql


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
	return round(np.mean(li), round_num)

def var(li, round_num=2):
	return round(np.var(li), round_num)

def std(li, round_num=2):
	return round(np.std(li), round_num)

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

def getValueFromSql(cursor, db, timestamp, key):
	query = "SELECT {} FROM {} WHERE timestamp=\'{}\';".format(key, db, timestamp)
	#print(query)
	cursor.execute(query)
	res = cursor.fetchall()[0][0]
	#print(res)
	return res


if __name__ == "__main__":

	db, cursor = connectSql(host='lxslc714.ihep.ac.cn')

	parser = argparse.ArgumentParser()
	parser.add_argument("timestamp")
	args = parser.parse_args()
	
	timestamp = args.timestamp

	if not getValueFromSql(cursor, 'jobs', timestamp, 'error'):

		file_list = os.listdir()

		for step in ['detsim', 'elecsim']:

			lustre_file = [x for x in file_list if step in x and "lustre" in x][0]
			eos_file = [x for x in file_list if step in x and "eos" in x][0]
			tmp_file = [x for x in file_list if step in x and "tmp" in x][0]

			f_lustre, t_lustre, e_lustre = readTree(lustre_file)
			f_eos, t_eos, e_eos = readTree(eos_file)
			f_tmp, t_tmp, e_tmp = readTree(tmp_file)

			branch_list = [b.GetName() for b in t_lustre.GetListOfBranches()]
			evtmax = getValueFromSql(cursor, 'jobs', timestamp, 'evtmax')
			momentums = getValueFromSql(cursor, 'jobs', timestamp, 'momentums')
			print(evtmax, momentums)

			for branch in branch_list:
			#for branch in []:
				lustre_data = flattenBranchData(getBranchData(t_lustre, e_lustre, branch_name=branch))
				eos_data = flattenBranchData(getBranchData(t_eos, e_eos, branch_name=branch))
				tmp_data = flattenBranchData(getBranchData(t_tmp, e_tmp, branch_name=branch))

				x = range(len(lustre_data))

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
					g1:"lustre,mean="+str(mean(lustre_data))+",std="+str(std(lustre_data)), 
					g2:"eos,mean="+str(mean(eos_data))+",std="+str(std(eos_data)), 
					g3:"tmp,mean="+str(mean(tmp_data))+",std="+str(std(tmp_data))
					})

				g1.Draw("ALP")
				g2.Draw("LP SAME")
				g3.Draw("LP SAME")
				legend.Draw("SAME")

				c.SaveAs(step+'_'+branch+".png")






