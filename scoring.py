import numpy as np
from news_submission import *


def rmse(predictions,answer):
	if isinstance(predictions, np.ndarray):
		return np.sum(np.sqrt(np.mean((predictions-answer)**2)))
	
	
def generate_scoring_array(predictions_list,answer_list):
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
	pred,answer=generate_scoring_array(predictions_list,answer_list)
	print(pred)
	print(answer)
	return rmse(pred,answer)


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