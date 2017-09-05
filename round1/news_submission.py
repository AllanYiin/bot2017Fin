import os
import json
import codecs
import random
import uuid
import datetime
import time
import warnings
import weakref
import shutil
import numpy as np

class news_submission(list):
	def __init__(self):
		"""
		测试集数据结构
		"""
		super().__init__()
		self.name='testingset'
		self.is_masked=False

	def size(self):
		return len(self)
	def add_item(self,obj):
		"""
		:param  新增对象obj至dict结构:
		:return:无回传值
		"""
		if isinstance(obj, pricedetail):
			self.append(obj)
	def load_items(self, data):
		"""
		批量将pricedetail加入
		:param data :
		:return 批量加入的数量:
		"""
		if isinstance(data, list):
			print('start load pricedetail')
			tot = len(data)
			for i in range(len(data)):
				try:
					if isinstance(data[i], dict):
						item = pricedetail(data[i])
						self.add_item(item)
				except OSError as e:
					print(e)
				if i % 1000 == 0 and i > 0:
					print('{0} 已加载..{1:.3f}%'.format(i, (i / tot) * 100.0))
			print('{0} 已加载完成!'.format(i))
			return i
			
	def load_researches(self, relationdata, sampledata):
		"""
		将投研报告对应至评分时点单位
		:param self:
		:param relationdata: 投研报告关系檔
		:param sampledata: 投研报告明细檔
		:return:是否加载成功
		"""
		try:
			if isinstance(relationdata, list) and isinstance(sampledata, list):
				print('开始加载投研报告明细檔ResearchTrainSample')
				tot = len(sampledata)
				for i in range(len(sampledata)):
					try:
						if isinstance(sampledata[i], dict):
							samplitem=ResearchTrainSample(sampledata[i])
							for k in range(len(relationdata)):
								if relationdata[k]['news_id']==samplitem.news_id:
									relationitem=ResearchRelations(relationdata[k])
									uuid=self._lookup_uuid(relationitem.security_id,relationitem.show_time)
									self.insert_news(samplitem,uuid)
					except OSError as e:
						print(e)
					if i % 1000 == 0 and i > 0:
						print('{0} 已加载...{1:.3f}%'.format(i, (i / tot) * 100.0))
			print('{0} 已加载完成!'.format(str(i)))
			return True
		except OSError as e:
			print(e)
			return False
	def load_annoncements(self, annoncedata, sampledata):
		"""
		将公告对应至评分时点单位
		:param self:
		:param annoncedata: 公告关系檔
		:param sampledata: 公告明细檔
		:return:是否加载成功
		"""
		try:
			if isinstance(annoncedata, list) and isinstance(sampledata, list):
				print('开始加载公告明细檔AnnouncementsTrainSample')
				tot=len(sampledata)
				for i in range(len(sampledata)):
					try:
						if isinstance(sampledata[i], dict):
							samplitem=AnnouncementsTrainSample(sampledata[i])
							for k in range(len(annoncedata)):
								if sampledata[k]['news_id']==samplitem.news_id:
									relationitem=AnnouncementsRelations(annoncedata[k])
									uuid=self._lookup_uuid(relationitem.security_id,relationitem.publish_date)
									self.insert_news(samplitem,uuid)
					except OSError as e:
						print(e)
					if i%1000==0 and i>0:
						print('{0} 已加载...{1:.3f}%'.format(i, (i / tot) * 100.0))
				print('{0} 已加载完成!'.format(str(i)))
			return True
		except OSError as e:
			print(e)
			return False
	def insert_news(self,news_sample,uuid):
		if  isinstance(news_sample, AnnouncementsTrainSample):
			news_sample.notice_date=None
			news_sample.publish_date=None
			if uuid in self:
				self[uuid].announcelist.append(news_sample)
				return True
			return False
		elif isinstance(news_sample, ResearchTrainSample):
			if uuid in self:
				self[uuid].researchlist.append(news_sample)
				return True
		return False
	def _lookup_uuid(self, security_id,data_date):
		if not self.is_masked:
			for (k, v) in self.items():
				if v.security_id==security_id and v.datetime==data_date:
					return k
	def mask_data(self):
		if not self.is_masked:
			for (k, v) in self.items():
				v.mask_data()
	def to_submit_dataset(self):
		"""
		内部生成提交数据结构
		:return :包含dict的清单
		"""
		outputs=[]
		for i in range(len(self)):
			if isinstance(self[i],pricedetail):
				outputs.append(self[i].to_submit_dict())
		return outputs
	
	def consolidateData(self):
		"""
		将各个测试集的具有uuid的json汇入

		"""
		reports=[]
		annos=[]
		prices=[]
		news=[]
		with codecs.open('AnnouncementsTrainSample.json', 'r', 'utf-8') as file1:
			dict_str = file1.readlines()
			jdict = json.loads(dict_str[0],encoding='utf-8')
			annos = jdict
		with codecs.open('ResearchTrainSample.json', 'r', 'utf-8') as file1:
			dict_str = file1.readlines()
			jdict = json.loads(dict_str[0],encoding='utf-8')
			reports = jdict
			
		with codecs.open('NewsTrainSample.json', 'r', 'utf-8') as file1:
			dict_str = file1.readlines()
			jdict = json.loads(dict_str[0],encoding='utf-8')
			news = jdict
			
		with codecs.open('pricedetail.json', 'r', 'utf-8') as file1:
			dict_str = file1.readlines()
			jdict = json.loads(dict_str[0],encoding='utf-8')
			prices = jdict
	
	
		for i in range(len(prices)):
			item=prices[i]
			for k in range(len(reports)):
				if reports[k]['uuid']==item.uuid:
					r = ResearchTrainSample(reports[k])
					item.researchlist.append(r)
			for m in range(len(annos)):
				if annos[m]['uuid'] == item.uuid:
					a = AnnouncementsTrainSample(annos[m])
					item.announcelist.append(a)
			for n in range(len(news)):
				if news[n]['uuid'] == item.uuid:
					nn = NewsTrainSample(news[n])
					item.newslist.append(nn)

			self.add_item(item)
		
	
	
	
class predict_point(object):
	warnings.warn("Predict_point相关内容即将弃用，建议使用较单纯的list of dict替代", DeprecationWarning, stacklevel=2)
	def __init__(self,_uuid=None,value1=None,value2=None,value3=None):
		"""
		测试集的基础单位，所有的新闻都会放在这个类中
		:param _uuid:
		:param value1:
		:param value2:
		:param value3:
		"""
		
		if _uuid is None:
			self.uuid=str(uuid.uuid4())  #解决json序列化问题
		else:
			self.uuid=str(_uuid)
		self.security_id=''
		self.datetime=None
		self.d0_wd =1
		self.d1_wd = 1
		self.d2_wd = 1
		self.d3_wd = 1
		self.value1=value1
		self.value2= value2
		self.value3= value3
		self.announcelist=[]
		self.researchlist = []
	def mask_data(self):
		"""
		抹去证券编号与日期信息(测试集不提供此类信息)
		"""
		self.security_id=None
		self.datetime=None
		if len(self.announcelist)>0:
			for m in range(len(self.announcelist)):
				self.announcelist[m].publish_date=None
				self.announcelist[m].notice_date = None
	

class pricedetail(object):
	"""
	初赛数据集pricedetail
	"""
	def __init__(self, jsondict=None):
		if isinstance(jsondict, dict):
			if jsondict is not None:
				self.tag = jsondict['tag']
				self.security_id =jsondict['security_id']
				self.data_date=time.strptime(jsondict['data_date'],"%Y-%m-%d")
				self.d0_wd =jsondict['d0_wd']
				self.d0_open =jsondict['d0_open']
				self.d1_wd = jsondict['d1_wd']
				self.d1_open = jsondict['d1_open']
				self.d2_wd = jsondict['d2_wd']
				self.d2_open = jsondict['d2_open']
				self.d3_wd = jsondict['d3_wd']
				self.d3_open = jsondict['d3_open']

				self.uuid=None
				self.announcelist = []
				self.researchlist = []
				self.newslist = []
				
	def mask_data(self):
		"""
		抹去证券编号与日期信息(测试集不提供此类信息)
		"""
		self.security_id=None
		self.data_date=None
	
				
	def to_predicpoint(self,v1=None,v2=None,v3=None):
		warnings.warn("Predict_point相关内容即将弃用，建议使用较单纯的list of dict替代", DeprecationWarning,stacklevel=2)
		item = predict_point()
		item.uuid = self.uuid
		item.security_id = self.security_id
		item.datetime = self.data_date
		item.d0_wd = int(self.d0_wd)
		item.d1_wd = int(self.d1_wd)
		item.d2_wd = int(self.d2_wd)
		item.d3_wd = int(self.d3_wd)
		if v1 is None:
			item.value1 =  (float(self.d1_open) / float(self.d0_open)) - 1
		else:
			item.value1=v1
		if v2 is None:
			item.value2 = (float(self.d2_open) / float(self.d1_open)) - 1
		else:
			item.value2=v2
		if v3 is None:
			item.value3 = (float(self.d3_open) / float(self.d2_open)) - 1
		else:
			item.value3=v3
		return item
	
	def to_submit_dict(self, uuid=None):
		"""
		在一般情况下是不需要自行指定数值，应该都是根据数据计算得出来的。仅在内部测试阶段会自行指定值
		:param uuid:
		:return:
		"""
		item = {}
		if uuid:
			item['uuid'] = uuid
		elif len(self.uuid)==36:
			item['uuid'] = self.uuid
		#测试集数据会自带uuid，训练集则可以自行设定，以供自行测试使用
		# item['security_id'] = self.security_id
		# item['data_date'] = self.data_date
		item['value1'] = (float(self.d1_open) / float(self.d0_open)) - 1
		item['value2'] = (float(self.d2_open) / float(self.d1_open)) - 1
		item['value3'] =  (float(self.d3_open) / float(self.d2_open)) - 1
		return item


class AnnouncementsRelations(object):
	"""
	初赛数据集AnnouncementsRelations
	"""
	def __init__(self, jsondict):
		if isinstance(jsondict, dict):
			self.news_id=jsondict['news_id']
			self.security_id=jsondict['security_id']
			self.publish_date=jsondict['publish_date']
			self.uuid = None

			
class AnnouncementsTrainSample(object):
	"""
	初赛数据集AnnouncementsTrainSample
	"""
	def __init__(self, jsondict):
		if isinstance(jsondict, dict):
			if 'news_id' in jsondict:
				self.news_id=jsondict['news_id']
			elif 'AnnonceCode' in jsondict:
				self.news_id = jsondict['AnnonceCode']
			if 'annonce_type' in jsondict:
				self.annonce_type=jsondict['annonce_type']
			elif 'AnnonceType' in jsondict:
				self.annonce_type = jsondict['AnnonceType']
					
			if 'annonce_title' in jsondict:
				self.annonce_title=jsondict['annonce_title']
			elif 'AnnonceTitle' in jsondict:
				self.annonce_title = jsondict['AnnonceTitle']
				
			#在新闻内容档案中将不会再有日期类字段(请查询关联檔)
			# if 'publish_date' in jsondict:
			# 	self.publish_date=jsondict['publish_date']
			# if 'notice_date' in jsondict:
			# 	self.notice_date=jsondict['notice_date']
			if 'content' in jsondict:
				self.content=jsondict['content']
			elif 'Content' in jsondict:
				self.content = jsondict['Content']
			self.uuid = None
			
		
class ResearchRelations(object):
	"""
	初赛数据集ResearchRelations
	"""
	def __init__(self, jsondict):
		if isinstance(jsondict, dict):
			self.news_id = jsondict['news_id']
			#self.title= jsondict['title'] #关联檔将不再放置新闻内容之信息
			if 'security_id' in jsondict:
				self.security_id = jsondict['security_id']
			else:
				self.security_id = jsondict['security_code']  #bug fix
			self.publish_date = jsondict['show_time'].replace('T00:00:00','')
			self.uuid=None
	

class ResearchTrainSample(object):
	"""
	初赛数据集ResearchTrainSample
	"""
	def __init__(self, jsondict):
		if isinstance(jsondict, dict):
			self.news_id = jsondict['news_id']
			self.title = jsondict['title']
			self.column_type = jsondict['column_type']
			if 'content' in jsondict:
				self.content=jsondict['content']
			elif 'Content' in jsondict:
				self.content = jsondict['Content']
			self.uuid = None


class NewsRelations(object):
	"""
	初赛数据集NewsRelations(追加之新闻信息)
	"""
	def __init__(self, jsondict):
		if isinstance(jsondict, dict):
			self.news_id=jsondict['news_id']
			self.security_id=jsondict['security_id']
			self.publish_date=jsondict['publish_date']
			self.uuid = None

class NewsTrainSample(object):
	"""
	初赛数据集NewsTrainSample(追加之新闻信息)
	"""
	def __init__(self, jsondict):
		if isinstance(jsondict, dict):
			self.news_id = jsondict['news_id']
			self.title = jsondict['title']
			if 'content' in jsondict:
				self.content=jsondict['content']
			elif 'Content' in jsondict:
				self.annonce_type = jsondict['Content']
			self.uuid = None
