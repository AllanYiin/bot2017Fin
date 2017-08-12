
import json
import codecs
import pandas as pd
import uuid
import sys
import datetime
import time
import pickle
import csv
import numpy as np
from transform import *
import _pickle as cPickle
import gzip
import numpy as np
import scipy.sparse as sp
from scipy.spatial.distance import squareform, pdist
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity





class word2vec(dict):
	def __init__(self,filename='word2vec.pklz'):
		"""
		Py Word2vec结构
		"""
		super().__init__()
		self.name='word2vec'
		self.load(filename)
		self.vocab_cnt=len(self)
		self.dims=self[list(self.keys())[0]].shape[0]
		
		print('詞彙數:' + str(self.vocab_cnt))
		print('維度數:' + str(self.dims))
		
		self.word2idx= {w: i for i, w in enumerate(self.keys())}
		self.idx2word= {i: w for i, w in enumerate(self.keys())}
		self._matrix =np.array(list(self.values()))
		print(self._matrix.shape)
	
	def save(self, filename='word2vec.pklz'):
		"""
		:param filename:存储位置
		"""
		fil = gzip.open(filename, 'wb')
		cPickle.dump(self, fil, protocol=pickle.HIGHEST_PROTOCOL)
		fil.close()
	
	
	def load(self,filename='word2vec.pklz'):
		fil = gzip.open(filename, 'rb')
		while True:
			try:
				tmp=cPickle.load(fil)
				self.update(tmp)
			except EOFError as e:
				print(e)
				break
		fil.close()
	
	def cosine_distance(self,representation1,representation2,axis=-1):
		"""
		計算兩個表徵間的cosine距離
		:param representation1:
		:param representation2:
		:param axis:
		:return:
		"""
		array1=None
		array2=None
		if isinstance(representation1,np.ndarray):
			array1=representation1
		elif isinstance(representation1,np.str):
			array1=self[representation1]
		else:
			raise NotImplementedError
			
		if isinstance(representation2,np.ndarray):
			array2=representation2
		elif isinstance(representation2,np.str):
			array2=self[representation2]
		else:
			raise NotImplementedError
			
		if len(array1.shape)==1 and len(array2.shape)==1:
			return np.sum(array1*array2,axis)/(len(array1)*len(array2))
		else:
			print('status3')
			product=array1 * array2
			print(product.shape)
			return np.sum(product, -1 ) / (array1.shape[-1] * array2.shape[-1])
	
	def find_nearest_word(self,represent,  topk:int=10,stopwords:list=[]):
		"""
		根據表徵(可以是字，可以是詞向量)取得最接近的詞
		:param stopwords: 停用詞，將此類詞排除於答案
		:param represent:
		:param topk:
		:return:
		"""
		array1=np.empty(200)
		if isinstance(represent,str) and represent in self:
			array1=self[represent]
			stopwords.append(represent)
		elif isinstance(represent,np.ndarray) :
			array1=represent
		else:
			raise NotImplementedError
		result_cos=cosine_similarity(np.reshape(array1,(1,array1.shape[-1])),self._matrix)
		result_cos=np.reshape(result_cos,result_cos.shape[-1])
		result_sort=result_cos.argsort()[-1*topk:][::-1]
		# [[self.idx2word[idx],result_cos[idx]] for idx in result_sort]
		# found={}
		# for item in  result_sort:
		# 	found[self.idx2word[item]]=result[item]
		# sortlist=sorted(found.items(), key=lambda d: d[1],reverse=True)
		#print(found)
		return [[self.idx2word[idx],result_cos[idx]] for idx in result_sort if self.idx2word[idx] not in stopwords and sum([ 1 if stop.startswith(self.idx2word[idx]) else 0 for stop in  stopwords])==0 ] #[item for item in sortlist if sum([len(item[0].replace(stop,''))>=2 for stop in stopwords]) ==0]
		
	
	def analogy(self,wordA:str, wordB:str,wordC:str, topk:int=10):
		"""
		語意類比關係  A:B=C:D
		:param wordA:
		:param wordB:
		:param wordC:
		:param topk: 取前K個
		:return:
		"""
		if wordA in self and wordB in self and wordC in self:
			arrayD=self[wordB]-self[wordA]+self[wordC]
			return self.find_nearest_word(arrayD,topk,stopwords= [wordA, wordB, wordC])
		else:
			return None
	#def TopNSimilarWords(self,word):
	
	def get_antonyms(self,wordA:str, topk:int=10,ispositive:bool=True):
		seed=[['美丽','丑陋'],['安全','危险'],['成功','失败'],['富有','贫穷'],['快乐','悲伤']]
		proposal={}
		for pair in seed:
			if ispositive:
				result=self.analogy(pair[0],pair[1],wordA,topk)
				print(w2v.find_nearest_word((self[pair[0]] + self[pair[1]]) / 2, 3))
			else:
				result = self.analogy(pair[1], pair[0], wordA, topk)
				print(w2v.find_nearest_word((self[pair[0]] + self[pair[1]]) / 2, 3))
				
			for item in result:
				term_products = np.argwhere(self[wordA] * self[item[0]] < 0)
				#print(item[0] + ':' +wordA + str(term_products))
				#print(item[0] + ':' +wordA+'('+str(pair)+')  '+ str(len(term_products)))
				if len(term_products)>=self.dims/4:
					if item[0] not in proposal:
						proposal[item[0]] = item[1]
					elif item[1]> proposal[item[0]]:
						proposal[item[0]] +=item[1]
		for k,v in  proposal.items():
			proposal[k]=v/len(seed)
		sortitems=sorted(proposal.items(), key=lambda d: d[1],reverse=True)
		return  [sortitems[i] for i in range(min(topk,len(sortitems)))]

	def print_word_statistics(self,result_list:list,is_print:bool=True):
		if is_print:
			print('、'.join(['{:s}:({:.{prec}f}%)'.format(item[0],item[1]*100.0, prec=3) for item in result_list]))
		else:
			return '、'.join(['{:s}:({:.{prec}f}%)'.format(item[0],item[1]*100.0, prec=3) for item in result_list])












if __name__ == '__main__':
	w2v=word2vec()
	
	anto=w2v.get_antonyms('尊敬')
	print(''.join([item[0]+str(w2v.cosine_distance('尊敬',item[0])) for item  in anto]))
	w2v.print_word_statistics(anto)
	
	similarWords=w2v.find_nearest_word('似乎',10)
	w2v.print_word_statistics(similarWords)
	
	answer = w2v.analogy('张惠妹', '阿妹', '周杰伦')
	print('张惠妹之于阿妹，那么周杰伦则是…' +w2v.print_word_statistics(answer,False))
	
	answer=w2v.analogy('双子座','花心','处女座')
	print('双子座之于花心，那么处女座则是…'+w2v.print_word_statistics(answer,False))
	
	
	
	
