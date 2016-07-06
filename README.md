# Affinity Analysis algorithm #

*This algorithm is written for recommending similar contents to download for iLibrary users.*


*No extra modules needed*


Usage Example:
```python
file_path = "xxx/xxx.csv"
AA = Apriori(file_path) # load in the data from the csv file

#ips is a python dictionary object (key = user id, value = contents the user downloaded)
#contents is a list of tuples (a content, download frequency of the content)
ips, contents = AA.data_filter() 

test_set = AA.test_dict  #test data, python dictionary object

 # hash the contents into numbers for easy analysis
content_dict = AA.set_up_content_dict(contents)

# python dictionary {ip:(contents the ip downloaded in numbers)}
ip_itemsets = AA.set_up_ip_itemset(ips,content_dict) 

min_support = 13 #set up for the minimum support 

#set up the length 1 frequent itemsets 
freq_itemsets = dict()
freq_itemsets[1] = dict((frozenset((idx,)),content[1])
					    for idx,content in enumerate(contents)
					    if content[1] > min_support)

#use the find_freq_itemsets to find superset 
curr_freq_set = AA.find_freq_itemsets(ip_itemsets,freq_itemsets[k-1],min_support)

#use find_all_candidate_rules to find all candidate rules
candidate_rules = AA.find_all_candidate_rules(freq_itemsets)

#use calculate_confidence to calculate the confidence of the rule
#optional argument, min_confidence & test
#default: min_confidence = 0.9, test = false
rule_confidence = AA.calculate_confidence(ip_itemsets,candidate_rules, min_confidence = 0.9)

#sort the result by confidence
sorted_confidence = sorted(rule_confidence.items(),key = itemgetter(1),reverse = True)
```
-
Sample data format

User ID  | Download Content
-------- | --------
001      | Content A
002      | Content B
003      | Content C
004      | Content A
005      | Content C 
...      | ...