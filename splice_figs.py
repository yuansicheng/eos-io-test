from PIL import Image
import os

def spliceFigs(out_name, figs):
	if not figs:
		return False

	print("spliceFigs: splicing "+" and ".join(figs)+"...")
	figs = [Image.open(fig) for fig in figs]

	if len(set([fig.size for fig in figs])) != 1:
		print("spliceFigs: figs size is different")

	height_size = figs[0].size[1]
	width_size = figs[0].size[0]

	target = Image.new('RGB', (width_size, height_size*len(figs)))
	left = 0
	right = height_size
	for fig in figs:
		target.paste(fig,(0, left, width_size, right))
		left += height_size
		right += height_size

	target.save(out_name)
	print('save ', out_name)
	return True

if __name__ == "__main__":
	path = "/junofs/users/yuansc/eos-test/20201010/data/"

	#2nd round
	dirs_range = ["2020-10-21-22-03-05", "2020-10-21-22-08-01"]
	#2nd round, evtmax=100
	#dirs_range = ["2020-10-21-22-03-05", "2020-10-21-22-03-55"]
	#2nd round, evtmax=200
	#dirs_range = ["2020-10-21-22-04-07", "2020-10-21-22-04-59"]
	#2nd round, evtmax=300
	#dirs_range = ["2020-10-21-22-05-12", "2020-10-21-22-06-01"]
	#2nd round, evtmax=400
	#dirs_range = ["2020-10-21-22-06-14", "2020-10-21-22-07-00"]
	#2nd round, evtmax=500
	#dirs_range = ["2020-10-21-22-07-13", "2020-10-21-22-08-01"]

	dirs = [path+x+'/' for x in os.listdir(path) if x>= dirs_range[0] and x<= dirs_range[1] ]
	#print(dirs)

	'''
	output = {"detsim_DetSimAlg_time_and_memory.png":["detsim_DetSimAlg.png", "detsim_mem_after_DSA-mem_before_DSA.png"],
		"detsim_OutputSvc_time_and_memory.png":["detsim_t_outputsvc_write.png", "detsim_m_after_output-m_before_output.png"]}
	'''
	output = {"elecsim_t_pmtsimAlg_time_and_memory.png":["elecsim_t_pmtsimalg.png", "elecsim_m_after_pmtsimalg-m_before_pmtsimalg.png"],
		"elecsim_OutputSvc_time_and_memory.png":["elecsim_t_outputsvc_write.png", "elecsim_m_after_output-m_before_output.png"],
		"elecsim_getoneevent_time_and_memory.png":["elecsim_t_pmtsimalg_getoneevent.png","elecsim_m_after_getoneevent-m_before_getoneevent.png"]}

	for dir in dirs:
		for out_name in output.keys():
			#print([dir+f for f in output[out_name]])
			spliceFigs(dir+out_name, [dir+f for f in output[out_name]] )
