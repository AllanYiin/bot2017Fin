# ==============================================================================
# Copyright (c) Deepbelief.ai. All rights reserved.
# ==============================================================================

'''
提交格式转换程序，将训练集数据转换为提交阶段选手们将收到的数据格式
	Step1. 产生计算单位guid
	Step2. 将公报、研究报告归整至guid
	Step3. 处理日期weekday问题
	Step4. 处理答案

'''

import json
import codecs
import pandas as pd
import uuid
import sys
import datetime
import time
import pickle
import csv


from news_submission import *

files=['pricedetail.json','AnnouncementsTrainSample.json','ResearchTrainSample.json']

#files=['pricedetail.json','AnnouncementsRelations.json','AnnouncementsTrainSample.json','ResearchRelation.json','ResearchTrainSample.json']
data={}
def handel_utf8bom():
	"""
	處理文件中有u'\ufeff'的問題(utf-8 BOM)
	:return:
	"""
	for file in files:
		s = codecs.open(file, mode='r', encoding='utf-8-sig').read()
		codecs.open(file, mode='w', encoding='utf-8').write(s)
		print(file+'   UTF8无BOM格式转换完成!!')


def preload_data():
	"""
	将初赛提供之json数据根据files的定义读入内存，并且统一透过名为data的dict统一存放，以便日后叫用
	"""
	global files,data
	#handel_utf8bom()
	for file in files:
		with codecs.open(file, 'r', 'utf-8') as file1:
			dict_str = file1.readlines()  # 读出来的是一个list
			jdict = json.loads(dict_str[0],encoding='utf-8')
			data[file] = jdict
			print(file+'  loaded...!')
			
			
class CJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime("%Y-%m-%d")
		elif isinstance(obj, uuid.UUID):
			return str(obj)
		elif isinstance(obj, float):
			return str(obj)
		else:
			return json.JSONEncoder.default(self, str(obj))
		
		
def gen_base():
	"""
	产生固化的测试集数据以及提交数据格式(由训练集数据格式转换)
	:return  newssub:测试集数据
	"""
	newssub=news_submission()
	newssub.load_items(data['pricedetail.json'])
	newssub.load_researches(data['ResearchRelation.json'], data['ResearchTrainSample.json'])
	newssub.load_annoncements(data['AnnouncementsRelations.json'],data['AnnouncementsTrainSample.json'])

	try:
		with open('testingset.pkl', 'wb') as handle:
			pickle.dump(newssub, handle, protocol=pickle.HIGHEST_PROTOCOL)
	except Exception as err:
		print(err)
	newssub.mask_data()
	return newssub

def gen_submit(submit_type,newssub):
	"""
	可以生成三种数据格式
	'json' : 0,
    'pickle' :1,
    'txt' : 2
	:param submit_type: 数据格式
	:return:
	"""
	SUBMIT_TYPE = {
		'json': 0,
		'pickle': 1,
		'txt': 2}
	try:
		if isinstance(newssub,news_submission):
			submit = newssub.to_submit_dataset()
			if submit_type in SUBMIT_TYPE:
				if SUBMIT_TYPE[submit_type] == 0:
					save_dict_json(submit, 'submit_dataset.json')
				elif SUBMIT_TYPE[submit_type] == 1:
					with open('submit_dataset.pkl', 'wb') as handle:
						pickle.dump(submit, handle, protocol=pickle.HIGHEST_PROTOCOL)
				
				elif SUBMIT_TYPE[submit_type] == 2:
					fieldnames = ['uuid', 'value1', 'value2','value3']
					test_file =open('submit_dataset.txt', 'w') #请勿改为wb，有坑
					writer = csv.DictWriter(test_file, delimiter='\t', fieldnames=fieldnames)
					writer.writeheader()
					for row in submit:
						writer.writerow(row)
					test_file.close()
					
	except Exception as err:
		print(err)





def save_dict_json(dict, dict_file_name):
	"""将dict进行json序列化,并以json形式保存
    :param dict: 字典结构数据
    :param dict_file_name: json文件名"""
	dict_str = json.dumps(dict, ensure_ascii=False)  # 写入中文问题
	file = codecs.open(dict_file_name, 'w', encoding="utf-8")
	file.write(dict_str)  # 写入
	file.close()
	
def porocessTestData():
	"""
	用于处理测试集数据
	
	"""
	subm=news_submission()
	subm.consolidateData()
	#
	with open('submit_dataset.pkl', 'wb') as handle:
		pickle.dump(subm, handle, protocol=pickle.HIGHEST_PROTOCOL)
		
		
		
		
def listofdict2txt(listofdict,save_path):
	text = ''
	for m in range(len(listofdict)):
		item = listofdict[m]
		if isinstance(item, dict):
			values=[str(v) for  k,v in item.items()]
			text +='\t'.join(values) + '\r\n'
	file = codecs.open(save_path, 'w', encoding="utf-8")
	file.write(text)
def json2txt(json_file,save_path):
	with codecs.open(json_file, 'r', 'utf-8') as file1:
		dict_str = file1.readlines()
		jsondict = json.loads(dict_str[0], encoding='utf-8')
		return listofdict2txt(jsondict,save_path)

if __name__ == '__main__':
	porocessTestData()
	
	with open('submit_dataset.pkl', 'rb') as handle:
		news = pickle.load(handle)
	
	
	
	#print('preload json start!')
	#handel_utf8bom()  #如果是linux平台请自行解除注解执行一次即可
	# preload_data()
	# news=[]
	# try:
	# 	with open('testingset.pkl', 'rb') as handle:
	# 		news = pickle.load(handle)
	# except IOError as e:
	# 		news = gen_base()
	# gen_submit('json', news)
	# gen_submit('pickle', news)
	# gen_submit('txt', news)
	
	#
	
	print('finish')