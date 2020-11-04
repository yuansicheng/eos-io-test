import os
import datetime
import time

def getTimestamp():
	now=datetime.datetime.now()
	return now.strftime("%Y-%m-%d-%H-%M-%S")

def createJob(args):
	os.chdir("/junofs/users/yuansc/eos-test/20201010/")

	new_dir="data/"+args["TIMESTAMP"]
	os.mkdir(new_dir)

	os.system("cp job.sh "+new_dir)
	os.chdir(new_dir)

	file_data=""
	with open("job.sh","r") as f:
		for line in f:
			for key in args.keys():
				if "PY_"+key in line:
					line=line.replace("PY_"+key,args[key])
			file_data+=line
	with open("job.sh","w") as f:
		f.write(file_data)

	os.system("chmod 755 job.sh")

	if args["NODE"]:
		#hep_sub job.sh -os SL6 -wn jnws053.ihep.ac.cn
		os.system("hep_sub job.sh -os SL6 -wn "+args["NODE"])
	else:
 		os.system("hep_sub job.sh -os SL6")


	time.sleep(2)
	return



os.system("export PATH=/afs/ihep.ac.cn/soft/common/sysgroup/hep_job/bin:$PATH")

args={}
args["EVTMAX"]="10"
#args["NODE"]=None
args["NODE"] = "jnws053.ihep.ac.cn"

MOMENTUMS_list=range(1,20)
EVTMAX_list = [100, 200, 300, 400, 500]
'''
#test
MOMENTUMS_list = [1]
EVTMAX_list = [10]
'''
job_num = 1

for e in EVTMAX_list:
	args["EVTMAX"] = str(e)
	for m in MOMENTUMS_list:
		args["TIMESTAMP"]=getTimestamp()
		args["MOMENTUMS"]=str(m)
		print("creating job "+str(job_num)+"...")
		job_num  += 1
		createJob(args)
	time.sleep(10)




