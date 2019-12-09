# runall.py
import os
try:
	os.makedirs('./testUseCase/expandable/')
except:
	pass
from subprocess import call

# print ('TestArchitectures.py >>>>>>>>>>>>>> ')
# call(["python", "./testUseCase/TestArchitectures.py"])

print (' TestAutoML.py >>>>>>>>>>>>>> ')
call(["python", "./testUseCase/TestAutoML.py"])


print (' TestDNN.py>>>>>>>>>>>>>> ')
call(["python", "./testUseCase/TestDNN.py"])


print ('TestEditorForCNN.py >>>>>>>>>>>>>> ')
call(["python", "./testUseCase/TestEditorForCNN.py"])

print ('TestScoring.py >>>>>>>>>>>>>> ')
call(["python", "./testUseCase/TestScoring.py"])

print ('TrainDNN.py >>>>>>>>>>>>>> ')
call(["python", "./testUseCase/TrainDNN.py"])


fileList = os.listdir('./testUseCase/expandable/')
print (fileList)
for f in fileList:
	print (f)
	os.remove('./testUseCase/expandable/'+f)
