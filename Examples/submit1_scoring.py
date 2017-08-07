from scoring import *
from news_submission import *
from transform import *


abs_path   =os.path.dirname(__file__)


if __name__ == '__main__':

	
	answer=submitfile2listofdict(os.path.join(abs_path,'answer.txt'))
	submit_test =submitfile2listofdict(os.path.join(abs_path, 'submit_test.txt'))
	result=scoring(submit_test,answer)
	