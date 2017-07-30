import numpy as np
import pickle
from itertools import groupby
from operator import itemgetter
from news_submission import *


def rmse(predictions,answer):
	"""
	評分程序
	:param predictions:
	:param answer:
	:return:
	"""
	if isinstance(predictions, np.ndarray):
		return np.sum(np.sqrt(np.mean((predictions-answer)**2)))
	
	
def generate_scoring_array(predictions_list,answer_list):
	"""
	
	:param predictions_list: 選手提交結果
	:param answer_list: 答案
	:return: 提交結果與答案 n[.array
	"""
	preddict={}
	answer=[]
	pred=[]
	if isinstance(predictions_list, list):
		for i in range(len(predictions_list)):
			preddict[predictions_list[i].uuid]=predictions_list[i]
			
	if isinstance(answer_list,list):
		for i in range(len(answer_list)):
			item=answer_list[i]
			_item=preddict[item.uuid]
			if isinstance(answer_list[i],predict_point):
				answer.append(np.asarray([item.value1,item.value2,item.value3]))
				pred.append(np.asarray([_item.value1,_item.value2,_item.value3]))
	return 	np.asarray(pred),np.asarray(answer)


def scoring(predictions_list,answer_list):
	"""
	評分流程作業
	:param predictions_list:
	:param answer_list:
	:return:
	"""
	pred,answer=generate_scoring_array(predictions_list,answer_list)
	print(pred)
	print(answer)
	return rmse(pred,answer)


def validate_submit(file_path,news_submit=None):
	"""
	验证提交数据集格式是否正确
	:param file_path:提交数据集路径
	param news_submit:测试数据集的类
	:return:是否格式正确
	"""
	if os.path.exists(file_path):
		try:
			submit=[]
			if os.path.splitext(os.path.basename(file_path))[1].lower()==".json":
				with codecs.open(file_path, 'r', 'utf-8') as file1:
					dict_str = file1.readlines()
					submit = json.loads(dict_str[0], encoding='utf-8')
	
			elif os.path.splitext(os.path.basename(file_path))[1].lower()==".pkl":
				with open(file_path, 'rb') as handle:
					submit = pickle.load(handle)
			
			elif os.path.splitext(os.path.basename(file_path))[1].lower() == ".txt":
				with codecs.open(file_path, 'r', 'utf-8') as file1:
					submit = {k: map(str.strip, g) for k, g in groupby(file1, key=itemgetter(0))}
			else:
				return False
			
			#step1 确认字段数与变量名称正确
			right=0
			wrong=0
			for k in range(len(submit)):
				dictlist=list(submit[k])
				if len(dictlist)==4 and 'uuid' in submit[k] and  'value1' in submit[k] and  'value2' in submit[k] and  'value3' in submit[k]:
					right+=1
				else:
					wrong += 1
					s = '案例{0}错误 :'.format(str(k))
					if len(dictlist) != 4:
						s += '字段数不正确!'
					if 'uuid' not in submit[k]:
						s += '缺少必要字段uuid!'
					if 'value1' not in submit[k]:
						s += '缺少必要字段value1!'
					if 'value2' not in submit[k]:
						s += '缺少必要字段value2!'
					if 'value3' not in submit[k]:
						s += '缺少必要字段value3!'
					print(s)
			print('共计{0}正确，{1}错误'.format(right, wrong))
			if wrong>0:
				return False
			else:
				# step2 是否提交正确的uuid
				right = 0
				wrong = 0
				if news_submit is not None and isinstance(news_submit,news_submission):
					for k in range(submit):
						if submit[k]['uuid'] in news_submission:
							right += 1
						else:
							wrong += 1
							s = 'uuid{0}不存在 :'.format(submit[k]['uuid'])
							print(s)
					print('共计{0}正确，{1}错误'.format(right, wrong))
					if wrong > 0:
						return False
					else:
						return True
				else:
					print('仅检查字段结构正确性')
					return True
		except OSError as e:
			print(e.strerror)
			return False
		
	else:
		return False

if __name__ == '__main__':
	
	result=validate_submit('submit_dataset.json')
	predictions_list=[]
	answer_list=[]
	
	p1= predict_point(uuid.uuid4(),0.5,0.2,-0.1)
	p2 =predict_point(uuid.uuid4(),1.5,-3.2,1.0)
	p3 =predict_point(uuid.uuid4(),-4.4,-3.2,0.01)
	predictions_list=[p1,p2,p3]
	
	a1 =  predict_point(p1.uuid,0.3,0.1,-0.2)
	a2 =  predict_point(p2.uuid,1.7,-2.2,1.2)
	a3 =  predict_point(p3.uuid,-4.3,-2.2,0.1)
	answer_list=[a1,a2,a3]
	
	scoring=scoring(predictions_list,answer_list)
	print(scoring)