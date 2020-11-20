import os
import datetime
import time
import pymysql

def getTimestamp():
	now=datetime.datetime.now()
	return now.strftime("%Y-%m-%d-%H-%M-%S")

def connectSql(host='localhost', 
	port = 8766, 
	user = 'root', 
	password = '!QAZ2wsx3edc', 
	db = 'eos_io_test'):
	db = pymysql.connect(host=host, port=port, user=user, password=password, db=db)
	cursor = db.cursor()
	return db, cursor

def insertSQL(db, cursor, data):
	job_id = data['job_id']
	query = "INSERT INTO jobs(job_id) VALUES("+str(job_id)+");"
	cursor.execute(query)
	db.commit()
	for key in data.keys():
		if isinstance(data[key], str):
			query = "UPDATE jobs SET {}='{}' WHERE job_id={};".format(key.lower(), str(args[key]), str(job_id))
		else:
			query = "UPDATE jobs SET {}={} WHERE job_id={};".format(key.lower(), str(args[key]), str(job_id))			
		cursor.execute(query)

		print(query)
		db.commit()
			
	return



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
		#os.system("hep_sub job.sh -os SL6 -wn "+args["NODE"])
		#2020.11.15 use os.popen instead of os.system in order to get job_id directly
		f = os.popen("hep_sub job.sh -os SL6 -wn "+args["NODE"]) 

	else:
		#os.system("hep_sub job.sh -os SL6")
		f = os.popen("hep_sub job.sh -os SL6")

	f_lines = f.readlines()
	job_id = int(f_lines[0].split()[-1][:-1])
	#print(f_lines[0], f_lines[0].split())
	f.close()

	args['job_id'] = job_id
	global db, cursor
	print(args['NODE'])
	insertSQL(db, cursor, args)

	time.sleep(2)
	return job_id


if __name__ == '__main__':

	db, cursor = connectSql()

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
			print('job_id', createJob(args))
		time.sleep(10)

	db.close()




