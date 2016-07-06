"""CODE WRITTEN BY WILLIAM C
JULY 2016
APPLY AFFINITY ANALYSIS ON OECD
ILIBRARY USAGE DATASET BY USING
APRIORI ALGORITHM"""

import os
import csv
import sys
from collections import Counter
from collections import defaultdict
from operator import itemgetter


class Apriori(object):
	"""docstring for Apriori"""
	def __init__(self,data_path):
		self.data_path = data_path

	def data_filter(self):
		with open (self.data_path, newline='') as csvfile:
			reader = csv.reader(csvfile,delimiter = ',')
			record_by_ip = dict()
			seen_ip = set()
			#read in data to a dictionary
			for idx, row in enumerate(reader):
				#group by ip
				if row[0] not in seen_ip:
					record_by_ip[row[0]] = [row[1]]  #dict[ip] = [content]
					seen_ip.add(row[0])
				else:
					if row[1] not in set(record_by_ip.get(row[0])):     # if content hasn't appeared in [contents]
						record_by_ip.get(row[0]).append(row[1])         # dict[ip] = [content1, content2, ...]

		"""150 IPs downloaded contents records
			Increase the size of the sample  and the test data 
			will significantly increase the running time of this script"""
		sort_by_ip = sorted(record_by_ip.keys(),key=lambda k:len(record_by_ip.get(k)), reverse = True)[0:150]
		test_set = sorted(record_by_ip.keys(),key=lambda k:len(record_by_ip.get(k)), reverse = True)[0:300]

		lst_of_contents = []	# all contents from corresponding IPs
		ip_dict = dict() 		# corresponding sample from record_by_ip

		for ip in sort_by_ip:
			for c in record_by_ip.get(ip):
				lst_of_contents.append(c)

			ip_dict[ip] = record_by_ip.get(ip)

		self.test_dict = dict()
		for ip in test_set:
			self.test_dict[ip] = record_by_ip.get(ip)

		return ip_dict,Counter(lst_of_contents).most_common(200)

	def set_up_content_dict(self,contents):
		content_dict = dict()
		self.look_up_dict = dict()
		for idx, content in enumerate(contents):
			if content[1] > min_support:
				content_dict[content[0]] = idx
				self.look_up_dict[idx] = content[0]
		return content_dict

	def set_up_ip_itemset(self,ips,content_dict):
		ip_itemsets = dict()
		for ip, download_contents in ips.items():
			value = []
			for content in download_contents:
				if content_dict.get(content) is not None:
					value.append(content_dict.get(content))
			ip_itemsets[ip] = frozenset(value)
		return ip_itemsets



	def find_freq_itemsets(self,ip_itemsets,k_1_itemsets,min_support):
		counts = defaultdict(int)
		for ips, contents in ip_itemsets.items():		# loop through the ip_itemsets
			for itemset in k_1_itemsets:		# loop through the k-1 frequent itemsets
				if itemset.issubset(contents):		# if itemset is a subset of the frequent set
					for other_item in contents - itemset:		# loop through the rest of the items
						curr_superset = itemset | frozenset((other_item,))
						counts[curr_superset] +=1
		k_itemsets = dict()
		for superset,freq in counts.items():
			if freq >= min_support:
				k_itemsets[superset] = freq
		return k_itemsets

	def find_all_candidate_rules(self,freq_itemsets):
		candidate_rules = []
		for itemset_length, itemset_counts in freq_itemsets.items():
			for itemset in itemset_counts.keys():
				for conclusion in itemset:
					premise = itemset - set((conclusion,))
					candidate_rules.append((premise,conclusion))
		print("There are {} candidate rules".format(len(candidate_rules)))
		return candidate_rules

	def calculate_confidence(self,ip_itemsets,candidate_rules,**kwargs):
		correct_counts = defaultdict(int)
		incorrect_counts = defaultdict(int)
		for ips, content in ip_itemsets.items():
			for candidate_rule in candidate_rules:
				premise, conclusion = candidate_rule 	#type(candidate_rule) : tuple
				if premise.issubset(content):
					if conclusion in content:
						correct_counts[candidate_rule]+=1
					else:
						incorrect_counts[candidate_rule]+=1

		rule_confidence = dict()
		for candidate_rule in candidate_rules:
			try:
				percentage = correct_counts[candidate_rule]
				/(correct_counts[candidate_rule]
				+incorrect_counts[candidate_rule])
			except ZeroDivisionError:
				percentage = 0
			rule_confidence[candidate_rule] = percentage

		test = kwargs.get('test',False)
		if test is False:
			min_confidence = 0.9
			if kwargs.get('min_confidence') is not None:
				min_confidence = kwargs.get('min_confidence')
			rule_confidence = {rule: confidence for rule, confidence in rule_confidence.items()
											if confidence > min_confidence}

		return rule_confidence

	def show_name(self,premise,conclusion):
		premise_name = ", ".join(self.look_up_dict.get(n) for n in premise)
		conclusion_name = self.look_up_dict.get(conclusion)
		return premise_name,conclusion_name

if __name__ == '__main__':

	"""INITIAL SETUP"""
	rel_path = os.path.dirname("__file__")
	data_folder = 'dataset'
	data_file_name = 'download_records.csv'
	file_path = os.path.join(rel_path,data_folder,data_file_name)

	AA = Apriori(file_path)
	ips, contents = AA.data_filter()
	test_set = AA.test_dict

	min_support = 13

	content_dict = AA.set_up_content_dict(contents)
	ip_itemsets = AA.set_up_ip_itemset(ips,content_dict)
	"""INITIAL SETUP ENDS HERE"""

	freq_itemsets = dict()
	#initial frequent itemset
	freq_itemsets[1] = dict((frozenset((idx,)),content[1])
						for idx,content in enumerate(contents)
						if content[1] > min_support)
	
	for k in range(2,20):
		curr_freq_set = AA.find_freq_itemsets(ip_itemsets,freq_itemsets[k-1],min_support)
		if len(curr_freq_set) == 0:
			print("Did not find any frequent itemsets of length {}".format(k))
			sys.stdout.flush()
			break
		else:
			print("Found {} frequent itemsets of length {}".format(len(curr_freq_set),k))
			sys.stdout.flush()
			freq_itemsets[k] = curr_freq_set
	del freq_itemsets[1]	#delete the frequent itemset with the set length of 1

	candidate_rules = AA.find_all_candidate_rules(freq_itemsets)
	rule_confidence = AA.calculate_confidence(ip_itemsets,candidate_rules, min_confidence = 0.9)
	sorted_confidence = sorted(rule_confidence.items(),key = itemgetter(1),reverse = True)

	"""TEST PART"""
	test_data = AA.set_up_ip_itemset(test_set,content_dict)
	rule_confidence_test = AA.calculate_confidence(test_data,candidate_rules, test = True)
	#sorted_confidence_test = sorted(rule_confidence_test.items(),key = itemgetter(1),reverse = True)
	"""TEST ENDS"""

	for idx in range(10):
		print("Rule #{0}".format(idx+1))
		premise,conclusion = sorted_confidence[idx][0]
		premise_name,conclusion_name = AA.show_name(premise, conclusion)
		print("Rule: if a person downloads {} they will also download {}".format(premise_name,conclusion_name))
		print(" -- Confidence: {0:.3f}".format(rule_confidence.get((premise,conclusion),-1)))
		print(" -- Test confidence: {0:.3f}\n".format(rule_confidence_test.get((premise,conclusion),-1)))



















