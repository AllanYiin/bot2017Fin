
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
		array1=None
		array2=None
		if isinstance(representation1,np.ndarray):
			array1=representation1
		elif isinstance(representation1,np.str):
			array1=self[representation1]
			
		if isinstance(representation2,np.ndarray):
			array2=representation2
		elif isinstance(representation2,np.str):
			array2=self[representation2]
			
		if len(array1.shape)==1 and len(array2.shape)==1:
			return np.sum(array1*array2,axis)/(len(array1)*len(array2))
		else:
			print('status3')
			product=array1 * array2
			print(product.shape)
			return np.sum(product, -1 ) / (array1.shape[-1] * array2.shape[-1])
		
	def find_nearest_word(self,represent,  topk:int=10):
		array1=np.empty(200)
		if isinstance(represent,str) and represent in self:
			array1=self[represent]
		elif isinstance(represent,np.ndarray) :
			array1=represent
		result=cosine_similarity(np.reshape(array1,(1,array1.shape[-1])),self._matrix)
		result=np.reshape(result,result.shape[-1])
		result_sort=result.argsort()[-1*topk:][::-1]
		found={}
		for item in  result_sort:
			found[self.idx2word[item]]=result[item]
		print(found)
		return found
	
	def analogy(self,wordA:str, wordB:str,wordC:str, topk:int=10):
		if wordA in self and wordB in self and wordC in self:
			arrayD=self[wordB]-self[wordA]+self[wordC]
			result=self.find_nearest_word(arrayD,topk)
			stopword=[wordA,wordB,wordC]
			tmp= result.copy()
			for k,v in tmp.items():
				if sum([1 if k==item or k in item or item in k else 0 for item in stopword])>0 :
					del result[k]
			return result
		else:
			return None
	#def TopNSimilarWords(self,word):
	








if __name__ == '__main__':
	w2v=word2vec()
	
	answer=w2v.analogy('双子座','花心','处女座')
	print('双子座之于花心，那么处女座则是…'+'、'.join(list(answer.keys())))
	
	
	
	# files=['W2v_1151245.json','W2v_199999.json','W2v_399999.json','W2v_599999.json','W2v_799999.json','W2v_999999.json']
	# for file in  files:
	# 	f= codecs.open(file,'r','utf-8')
	# 	jdict=json.load(f)
	# 	f.close()
	# 	print(file + '  loaded...!')
	# 	if isinstance(jdict,dict):
	# 		for k,v in jdict.items():
	# 			word_embed[k]=np.array(v)
	
	# fil=open('word2vec.pkl', 'rb')
	# word_embed=cPickle.load(fil)
	# fil.close()