import sys
import json
import time
import numpy as np
import subprocess
import matplotlib.pyplot as plt

SCALE = 0.001
REL_OUT_FILENAME="plots/"+str(sys.argv[1])
FORMAT=".png"

class DataPoints:
	def __init__(self):
		self.reads = {
	    "mins" : [],
	    "maxes" : [],
	    "means" : [],
	    "stddevs" : []
		}
		self.writes = {
	    "mins" : [],
	    "maxes" : [],
	    "means" : [],
	    "stddevs" : []
		}

  # add a data point as the min, the max, the mean and stddev
  # of the sample chosen for read operations.
	def add_read(self, min, max, mean, stdev):
		self.reads['mins'].append(min)
		self.reads['maxes'].append(max)
		self.reads['means'].append(mean)
		self.reads['stddevs'].append(stdev)

  # add a data point as the min, the max, the mean and stddev
  # of the sample chosen for this sample of write operations
	def add_write(self, min, max, mean, stdev):
		self.writes['mins'].append(min)
		self.writes['maxes'].append(max)
		self.writes['means'].append(mean)
		self.writes['stddevs'].append(stdev)

# saves a graph from the given values
def generate_graphs_from_means(scull_latency, rust_latency):
	labels=["C", "Rust"]
	box_w = 0.4

	# calculate ranges correctly
	c_max_writes = max(scull_latency.writes['means'])
	c_min_reads = min(scull_latency.reads['means'])
	rust_max_writes = max(rust_latency.writes['means'])
	rust_min_reads = min(rust_latency.reads['means'])
	max_scull = max(c_max_writes, rust_max_writes)
	min_scull = min(c_min_reads, rust_min_reads)

	fig, ax = plt.subplots(1,2)
	fig.tight_layout(pad=0.6)
	plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.4)
	ax[0].set_title('latency for readings')
	ax[1].set_title('latency for writings')
	ax[0].boxplot([scull_latency.reads['means'], rust_latency.reads['means']], labels=labels, widths=box_w)
	ax[1].boxplot([scull_latency.writes['means'], rust_latency.writes['means']], labels=labels, widths=box_w)
	for plot in ax:
		plot.set_ylim(0, max_scull + min_scull)
		plot.set_ylabel("µsec")
	plt.savefig(REL_OUT_FILENAME+FORMAT)

def main(filename, out_dir):
	ret = 0
	rust_scull = DataPoints()
	c_scull = DataPoints()
	as_dict = {}

	with open("./"+out_dir+"/"+filename) as handle:
		as_dict = json.load(handle)

	for i in as_dict['jobs']:
		wlat = i['write']['lat_ns']
		rlat = i['read']['lat_ns']
		ret += 1
		if i['job options'] and i['job options']['filename'] == "/dev/scull":
			c_scull.add_write(
				wlat['min'] * SCALE,
				wlat['max'] * SCALE,
				wlat['mean'] * SCALE,
				wlat['stddev'] * SCALE
			)
			c_scull.add_read(
				rlat['min'] * SCALE,
				rlat['max'] * SCALE,
				rlat['mean'] * SCALE,
				rlat['stddev'] * SCALE
			)
		else:
			rust_scull.add_write(
				wlat['min'] * SCALE,
				wlat['max'] * SCALE,
				wlat['mean'] * SCALE,
				wlat['stddev'] * SCALE
			)
			rust_scull.add_read(
				rlat['min'] * SCALE,
				rlat['max'] * SCALE,
				rlat['mean'] * SCALE,
				rlat['stddev'] * SCALE
			)
	print(ret)
	generate_graphs_from_means(c_scull, rust_scull)

if __name__ == "__main__":
  # filename and out_path
	if(sys.argv[1] and sys.argv[2]):
		main(sys.argv[1], sys.argv[2])
	else:
		print("argument missing (filename, output_directory)")
