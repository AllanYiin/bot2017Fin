import numpy as np
import pickle
import re
import warnings
import numbers
import string
import  pandas
from itertools import groupby
from operator import itemgetter
from news_submission import *



def rmse(predictions:np.ndarray,answer:np.ndarray):
	"""
	評分程序
	:param predictions:
	:param answer:
	:return:
	"""
	warnings.warn("此计分方法已弃用", DeprecationWarning, stacklevel=2)
	return np.sum(np.sqrt(np.mean(np.square(np.subtract(answer, predictions)),0)))

def expect_margin(predictions:np.ndarray,answer:np.ndarray):
	predict_sign=np.sign(predictions)
	answer_sign = np.sign(answer)

	margin_array=[]
	for m in range(answer.shape[0]):
		row=[]
		for n in range(answer.shape[1]):
			a=answer[m,n]
			p = predictions[m,n]
			p_s=predict_sign[m,n]
			a_s=answer_sign[m,n]
			if p_s==a_s :
				row.append(min(abs(a),abs(p)))
			# elif p_s!=a_s or p==0:
			# 	row.append(-1*(abs(a)+abs(p)))
			else:
				#row.append(-1*abs(a))
				row.append(-1 * (abs(a) + abs(p)))
		margin_array.append(row)
	margin_array=np.array(margin_array)
	return np.sum(margin_array,0)

def price_trend_hit(predictions:np.ndarray,answer:np.ndarray):
	predict_sign=np.sign(predictions)
	answer_sign = np.sign(answer)
	hit=np.equal(answer_sign,predict_sign)
	return np.mean(hit,0)

def generate_scoring_array(predictions_list,answer_list):
	"""
	
	:param predictions_list: 選手提交結果
	:param answer_list: 答案
	:return: 提交結果與答案 n[.array
	"""
	preddict={}
	answer=[]
	pred=[]
	missing=0
	if isinstance(predictions_list, list):
		for i in range(len(predictions_list)):
			if isinstance(predictions_list[i],dict) and 'uuid' in predictions_list[i]:
				preddict[predictions_list[i]['uuid']]=predictions_list[i]
			elif isinstance(predictions_list[i],predict_point):
				preddict[predictions_list[i].uuid] = predictions_list[i]
	if isinstance(answer_list,list):
		for i in range(len(answer_list)):
			item=answer_list[i]
			temp_uuid=None
			if isinstance(item,dict) and 'uuid' in item:
				answer.append(np.asarray([float(item['value1']), float(item['value2']), float(item['value3'])],dtype=np.float64))
				if item['uuid'] in preddict:
					temp_uuid=item['uuid']
			elif isinstance(item, predict_point):
				answer.append(np.asarray([float(item.value1), float(item.value2), float(item.value3)],dtype=np.float64))
				if item.uuid in preddict:
					temp_uuid=item.uuid
			if temp_uuid is not None:
				if isinstance(preddict[temp_uuid], dict)  :
					pred.append(np.asarray([float(preddict[temp_uuid]['value1']), float(preddict[temp_uuid]['value2']),
					                       float(preddict[temp_uuid]['value3'])],dtype=np.float64))
				elif isinstance(preddict[temp_uuid], predict_point):
					pred.append(np.asarray([float(preddict[temp_uuid].value1), float(preddict[temp_uuid].value2),
					                                                                float(preddict[temp_uuid].value3)],dtype=np.float64))
			else:
				pred.append(np.asarray([00,0.0,0.0]))
				missing += 1
	return 	np.array(pred),np.array(answer),missing



def scoring(predictions_list,answer_list):
	"""
	評分流程作業
	为了彻底解决原有计分模式可以透过全部写零或是基于零的随机数来获取高分之不公平状况。因此重新修正评分机制，改以预期收益率作为计分基础
		(1)	以选手答案作为交易决策基准，若是选手预测涨，则买入，选手预测跌，则放空，假设所有股票面额一样，计分时不考虑个别股票支票价值差异(因为选手在评测阶段不会知道对应之股票编号)
		(2)	如果选手预测涨跌幅(涨、不变、跌)与实际一致，则会产生获利，获利金额应该等于选手预测涨跌幅绝对值与实际涨跌幅绝对值取其小者。
		(3)	如果选手预测涨跌幅(涨、不变、跌)与实际不一致，则会产生损失，损失金额应该等于选手预测涨跌幅绝对值与实际涨跌幅绝对值加总。
		(4)	如果选手预测不变(涨跌幅为零)，除非答案也是不变，不然将会遭受未执行交易策略的期望收益损失或跌价风险。金额会等于实际涨跌幅绝对值
		(5)	将[涨跌幅一致收益(2)	]-[涨跌幅不一致损失(3)]-[预测不变损失(4)]即可得到该预测的收益
		(6)	计算三日个别之收益加总，除以完美预测状况下之最佳收益，即可获得预期收益率
	:param predictions_list:
	:param answer_list:
	:return:
	"""
	pred,answer,missing=generate_scoring_array(predictions_list,answer_list)
	# print(pred)
	# print(answer)
	margin1=expect_margin(pred,answer) #选手预测的三日预期收益
	margin2= expect_margin(answer, answer) #完美预测的三日预期收益
	price_hit = price_trend_hit(pred, answer)  # 选手预测的三日预期收益
	
	margin_rate=np.divide(margin1,margin2)
	score=np.sum(margin_rate)
	return score ,margin_rate, price_hit,missing



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
					sep = '\t'
					submit=[]
					lines=file1.readlines()
					keys=lines[0].replace('\r','').replace('\n','').split(sep)
					for i in range(1,len(lines)-1):
						dictitem={}
						values=lines[i].replace('\r','').replace('\n','').split(sep)
						for m in range(len(keys)):
							if len(values[0])>0:
								if re.match("^[+-]?\d(>?\.\d+)?$", values[m]) :
									dictitem[keys[m]]=float(values[m])
								else:
									dictitem[keys[m]] =values[m]
						submit.append(dictitem)
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


def submitfile2listofdict(file_path):
	''''
		将各种提交格式加载
	'''
	if os.path.exists(file_path):
		try:
			submit = []
			if os.path.splitext(os.path.basename(file_path))[1].lower() == ".json":
				with codecs.open(file_path, 'r', 'utf-8-sig') as file1:
					dict_str = file1.readlines()
					jsonstr=''.join(dict_str).replace('\t','')
					submit = json.loads(jsonstr)
					return submit
			elif os.path.splitext(os.path.basename(file_path))[1].lower() == ".pkl":
				with open(file_path, 'rb') as handle:
					submit = pickle.load(handle)
					return submit
			elif os.path.splitext(os.path.basename(file_path))[1].lower() in [".txt", ".csv","tsv", ".dat"]:
				with codecs.open(file_path, 'r') as file1:
					sep = '\t'
					submit = []
					lines = file1.readlines()
					if len(lines)>0:
						keys = lines[0].replace('\r', '').replace('\n', '').replace(',', '\t').replace('锘縱alue','value').replace('锘縰uid','uuid').split(sep)
						for i in range(1, len(lines)):
							dictitem = {}
							values = lines[i].replace('\r', '').replace('\n', '').replace(',', '\t').split(sep)
							for m in range(len(keys)):
								if len(values[0]) > 0 and m<len(values):
									if re.match("^[+-]?\d(>?\.\d+)?$", values[m].strip()):
										dictitem[keys[m]] = float(values[m].strip())
									else:
										dictitem[keys[m]] = values[m].strip()
							submit.append(dictitem)
					return submit
		except OSError as e:
			return None
	return None


if __name__ == '__main__':
	
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
