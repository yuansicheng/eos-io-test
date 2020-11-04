import ROOT as rt
import time
import os

'''
#test
myfile = "data/2020-10-13-20-55-23/sample_detsim_dcs_lustre_2020-10-13-20-55-23.root"
myfile = rt.TFile(myfile)

mychain = myfile.Get('DataCollSvc')
entries = mychain.GetEntriesFast()

for i in range(entries):
	if i==10:
		break
	mychain.GetEntry(i)
	print(list(mychain.totalPE), type(mychain.totalPE))
'''

def readTree(file):
	print("readTree: reading " + file)
	myfile = rt.TFile(file)
	mychain = myfile.Get('DataCollSvc')
	entries = mychain.GetEntriesFast()

	t_outputsvc_write_list = []

	for i in range(entries):
		mychain.GetEntry(i)
		t_outputsvc_write_list += list(mychain.t_outputsvc_write)

	return t_outputsvc_write_list

def list2vector(li):
	v = rt.std.vector(float)()
	for i in li:
		v.push_back(i)
	return v

def list2TVector(li):
	v = rt.TVector(0, len(li)-1)
	for i in range(len(li)):
		v[i] = li[i]
	return v

def draw_lustre_and_eos(path, momentums, mode="detsim", out_name="t_outputsvc_write.png"):
	if path[-1] != "/":
		path += "/"
	file_list = os.listdir(path)
	if mode in ["detsim", "elecsim"]:
		lustre_file = path + [x for x in file_list if mode in x and "lustre" in x][0]
		eos_file = path + [x for x in file_list if mode in x and "eos" in x][0]
	else:
		return

	t_lustre = readTree(lustre_file)
	t_eos = readTree(eos_file)

	print("draw_lustre_and_eos: " + path + "\ndrawing...")
	#t_lustre = t_lustre[1:]
	#t_eos = t_eos[1:]

	x = range(len(t_lustre))


	x_vector = list2TVector(x)
	t_lustre_vector = list2TVector(t_lustre)
	t_eos_vector = list2TVector(t_eos)

	#print(len(x), x_vector, t_lustre_vector)

	c = rt.TCanvas("c1","Graph Draw Options",200,10,2560,1600)

	
	g1 = rt.TGraph(x_vector, t_lustre_vector)
	g1.SetLineColor(4)

	axis = g1.GetYaxis()
	axis.SetRangeUser(min(t_lustre+ t_eos)-1,max(t_lustre+ t_eos)+1)

	g1.SetTitle("OutputSvc->Write()  momentums = "+str(momentums))

	g1.Draw("ALP")
	 
	
	g2 = rt.TGraph(x_vector, t_eos_vector)
	g2.SetLineColor(2)	
	g2.Draw("SAME")

	t_lustre_mean = round(sum(t_lustre)/len(t_lustre),2)
	t_eos_mean = round(sum(t_eos)/len(t_eos),2)

	legend = rt.TLegend(.70, .80, .90, .90)
	legend.AddEntry(g1, "lustre, mean="+str(t_lustre_mean))
	legend.AddEntry(g2, "eos, mean="+str(t_eos_mean))
	legend.Draw("SAME")

	print("momentums = " + str(momentums))
	print("t_lustre = ", t_lustre)
	print("t_eos = ", t_eos)
	print("")

	c.SaveAs(path + out_name)

	return [t_lustre_mean, t_eos_mean]

def getMomentums(path):
	with open(path+"job.sh","r") as f:
		for line in f.readlines():
			line = line.split("=")
			#print(line)
			if line[0] == "MOMENTUMS":
				return int(line[-1])


if __name__ == "__main__":
	path = "/junofs/users/yuansc/eos-test/20201010/data/"
	dirs = [path+x+'/' for x in os.listdir(path)]

	means = {}

	for d in dirs:
		momentums = getMomentums(d)
		print(d," ", momentums)
		means[momentums] = draw_lustre_and_eos(d, momentums)


	#draw means
	keys = list(means.keys())
	keys.sort()
	lustre_means = [means[x][0] for x in keys]
	eos_means = [means[x][1] for x in keys]
	print("drawing means pic...")
	
	keys_vector = list2TVector(keys)
	lustre_means_vector = list2TVector(lustre_means)
	eos_means_vector = list2TVector(eos_means)

	print(0)

	c = rt.TCanvas("c1","Graph Draw Options",200,10,2560,1600)
	g1 = rt.TGraph(keys_vector, lustre_means_vector)
	g1.SetLineColor(4)

	axis = g1.GetYaxis()
	axis.SetRangeUser(min(lustre_means+ eos_means)-1,max(lustre_means+ eos_means)+1)

	g1.SetTitle("OutputSvc->Write()  momentums = "+str(momentums))

	g1.Draw("AC*")
	 
	
	g2 = rt.TGraph(keys_vector, eos_means_vector)
	g2.SetLineColor(2)	
	g2.Draw("C* SAME")

	legend = rt.TLegend(.20, .70, .40, .85)
	legend.AddEntry(g1, "lustre")
	legend.AddEntry(g2, "eos")
	legend.Draw("SAME")

	c.SaveAs("/junofs/users/yuansc/eos-test/20201010/t_outputsvc_write_means.png")
	

	#print(keys, lustre_means, eos_means)