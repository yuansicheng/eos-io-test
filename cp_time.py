from create_jobs import connectSql
import argparse
import os
import numpy as np

def getCPData(source, target, filename, mode='lustre'):
	query_cp = "/usr/bin/time -f \"%e\" cp {} {} 2>&1".format(source+'/'+filename, target)
	query_rm = "rm {}".format(target+'/'+filename)
	if mode != 'lustre':
		query_cp = "/usr/bin/time -f \"%e\" eos cp {} {} 2>&1".format(source+'/'+filename, target)
		query_rm = 'eos ' + query_rm
	f = os.popen(query_cp)
	res = f.readlines()
	print(res)
	data = float(res[-1])
	#f.close()
	os.system(query_rm)
	return data

def addDataToSql(db, cursor, timestamp, step, mode, file_size, data_mean, data_std, \
	data_max, data_min, data_median):
	query = "INSERT INTO cp_time(timestamp, step, mode, file_size, data_mean, data_std, data_max, data_min, data_median) VALUES('{}','{}','{}',{},{},{},{},{},{});"\
			.format(timestamp, step, mode, str(file_size), str(data_mean), str(data_std), str(data_max), str(data_min), str(data_median))
	print(query)
	cursor.execute(query)
	db.commit()
	return



if __name__ == "__main__":
	db, cursor = connectSql(host='lxslc714.ihep.ac.cn')

	parser = argparse.ArgumentParser()
	parser.add_argument("timestamp")
	args = parser.parse_args()
	
	timestamp = args.timestamp

	tmp_dir = "/tmp/yuansc"
	lustre_dir = "/junofs/users/yuansc/eos-test/eos_io_test"
	eos_dir = "/eos/juno/user/yuansc/eos_io_test"

	for step in ['detsim', 'elecsim']:
		try:
			file = [f for f in os.listdir(tmp_dir) if step in f and timestamp in f][0]
		except:
			print(step, timestamp, 'not found')
			continue
		file_path = tmp_dir + '/' + file
		file_size = os.path.getsize(file_path)
		lustre_data = []
		eos_data = []
		for i in range(10):
			lustre_data.append(getCPData(tmp_dir, lustre_dir, file, mode='lustre'))
			eos_data.append(getCPData(tmp_dir, eos_dir, file, mode='eos'))

		addDataToSql(db, cursor, timestamp, step, 'lustre', file_size, np.mean(lustre_data), \
			np.std(lustre_data), np.max(lustre_data), np.min(lustre_data), np.median(lustre_data))
		addDataToSql(db, cursor, timestamp, step, 'eos', file_size, np.mean(eos_data), \
			np.std(eos_data), np.max(eos_data), np.min(eos_data), np.median(eos_data))

	db.close()