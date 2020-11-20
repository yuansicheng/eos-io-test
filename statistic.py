from create_jobs import connectSql
from draw_all_branches import *
import argparse
import os
import numpy as np

def reportError(db, cursor, timestamp):
	query="UPDATE jobs SET error=1 WHERE timestamp='{}';".format(str(timestamp))
	cursor.execute(query)
	db.commit()
	return

def addDataToSql(db, cursor, timestamp, branch, step, mode, data_mean, data_std, \
	data_max, data_min, data_median):
	query = "INSERT INTO statistic(timestamp, branch, step, mode, data_mean, data_std, data_max, data_min, data_median) VALUES('{}','{}','{}','{}',{},{},{},{},{});"\
			.format(timestamp, branch, step, mode, str(data_mean), str(data_std), str(data_max), str(data_min), str(data_median))
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

	file_list = os.listdir()
	for step in ['detsim', 'elecsim']:
		branch_num = {}
		for mode in ['tmp', 'lustre', 'eos']:
			try:
				file = [f for f in file_list if step in f and mode in f][0]
				file, tree, entries = readTree(file)
				branch_list = [b.GetName() for b in tree.GetListOfBranches()]
				branch_num[mode] = len(branch_list)
				for branch in branch_list:
					data = flattenBranchData(getBranchData(tree, entries, branch_name=branch))
					data_mean = np.mean(data)
					data_std = np.std(data)
					data_max = np.max(data)
					data_min = np.min(data)
					data_median = np.median(data)
					addDataToSql(db, cursor, timestamp, branch, step, mode, data_mean, \
						data_std, data_max, data_min, data_median)
				
			except:
				EreportError(db, cursor, timestamp)

			if branch_num:
				if len(set(branch_num.values())) != 1:
					reportError(db, cursor, timestamp)
			
	db.close()



