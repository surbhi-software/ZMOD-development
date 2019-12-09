import json,  os, skimage
from trainModel.mrcnn import model as modellib
from trainModel.mrcnn import visualize
import numpy as np
from trainModel.mrcnn import utils, config
import os,json,ast
from random import choice
from string import ascii_uppercase
logFolder='./logs/'

from trainModel import kerasUtilities
from multiprocessing import Lock, Process
from trainModel.kerasUtilities import PMMLMODELSTORAGE
kerasUtilities = kerasUtilities.KerasUtilities()

selDev="/device:CPU:0"
def gpuCPUSelect(selDev):
	return selDev

class CustomDataset(utils.Dataset):
    
    def get_polygons(self, annotation):
        polygons=[]
        for ann in annotation:
            polyg = {'all_points_x':[],'all_points_y':[]}
            for seg in ann['segmentation']:
                polyg['all_points_x'].append(seg['x'])
                polyg['all_points_y'].append(seg['y'])
            polygons.append(polyg)
        return polygons

    def get_classes(self, annotation):
        class_ = set()
        for ann in annotation:
            for an in ann['annotation']:
                class_.add(an['label'])
        return class_
    
    def get_class_ids(self,annotation):
        classids = []
        for a in annotation:
            for inf in self.class_info:
                if inf['name'] == a['label']:
                    classids.append(inf['id'])
        return classids
    
    def load_dataset(self, datasetDir, subset):
        """Load a subset of the Balloon dataset.
        dataset_dir: Root directory of the dataset.
        subset: Subset to load: train or val
        """        

        # Train or validation dataset?
        assert subset in ["train", "validation"]
        parentFolder=datasetDir
        dataset_dir = os.path.join(parentFolder, subset)
        annotations = os.listdir(dataset_dir)
        annotations = [json.load(open(os.path.join(dataset_dir,ann),'r')) for ann in annotations if ann.endswith('.json')]
        classes = self.get_classes(annotations)
        for idx,cl in enumerate(classes):
            self.add_class("customWork",idx+1,cl)
            
        # Add images
        for a in annotations:
            # Get the x, y coordinaets of points of the polygons that make up
            # the outline of each object instance. These are stores in the
            # shape_attributes (see json format above)
            # The if condition is needed to support VIA versions 1.x and 2.x.
            polygons = self.get_polygons(a['annotation'])
            classIds = self.get_class_ids(a['annotation'])
            # load_mask() needs the image size to convert polygons to masks.
            # Unfortunate1ly, VIA doesn't include it in JSON, so we must read
            # the image. This is only managable since the dataset is tiny.
            image_path = os.path.join(dataset_dir, a['imagePath'])
            height = a['imageHeight']
            width = a['imageWidth']

            self.add_image(
                "customWork",
                image_id=a['imagePath'],  # use file name as a unique image id
                path=image_path,
                width=width, height=height,
                polygons=polygons,classids=classIds)

    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a balloon dataset image, delegate to parent class.
        image_info = self.image_info[image_id]
        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
            mask[rr, cc, i] = 1
        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID only, we return an array of 1s
        return mask.astype(np.bool), np.array(info['classids'],dtype=np.uint8)

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "customWork":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)


class ObjectDetetctionModels():

	def __init__(self):
		# self.pathOfData = None
		# self.logFolder = './logs/'
		self.statusFile = None
		self.modelPathName=None
		self.dataFolder=None
		self.idforData=None
		# self.trainFolder = None
		# self.validationFolder = None
		# self.pmmlObj = None
		# self.hdExtDet = None
		# self.pmmlfileObj = None
		self.lockForStatus = Lock()

	def upDateStatus(self):
		self.lockForStatus.acquire()
		sFile=open(self.statusFile,'r')
		sFileText=sFile.read()
		data_details=json.loads(sFileText)
		sFile.close()
		self.lockForStatus.release()

		return data_details


	def train(modelPathName,dataFolder,statusfileLocation,idforData):
		self.statusFile=statusfileLocation
		dataset_train = CustomDataset()
		dataset_train.load_dataset(dataFolder, "train")
		dataset_train.prepare()

		dataset_val = CustomDataset()
		dataset_val.load_dataset(dataFolder, "validation")
		dataset_val.prepare()

		kerasUtilities.updateStatusOfTraining(statusfileLocation,'Data Loaded')

		MODEL_DIR='./logs/'+idforData+'_mrcnnModel'+'/'
		kerasUtilities.checkCreatePath(MODEL_DIR)

		class CustomConfig(config.Config):
		    NAME = "customWork"
		    IMAGES_PER_GPU = 1
		    NUM_CLASSES = len(dataset_train.class_names)
		    STEPS_PER_EPOCH = 10
		    DETECTION_MIN_CONFIDENCE = 0.9


		configure = CustomConfig()
		# configure.NUM_CLASSES=len(dataset_train.class_names)

		model = modellib.MaskRCNN(mode="training", config=configure,
		                          model_dir=MODEL_DIR)
		kerasUtilities.updateStatusOfTraining(statusfileLocation,'Model Object Created')
		model.load_weights(model.get_imagenet_weights(), by_name=True)

		kerasUtilities.updateStatusOfTraining(statusfileLocation,'Training Started')

		try:
			import tensorflow as tf
			with tf.device(gpuCPUSelect(selDev)):
				model.train(dataset_train, dataset_val, learning_rate=configure.LEARNING_RATE, epochs=2, layers='heads')
				kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Completed')
				# model.fit_generator(tGen,steps_per_epoch=stepsPerEpoch,validation_steps=10,epochs=epoch,validation_data=vGen,callbacks=[tensor_board])
		except Exception as e:
			data_details=self.upDateStatus()
			data_details['status']='Training Failed'
			data_details['errorMessage']='Please check the error >> '+ str(e)
			data_details['errorTraceback']=traceback.format_exc()
			with open(self.statusFile,'w') as filetosave:
				json.dump(data_details, filetosave)
			# sys.exit()
			return

		

		from nyokaBase.mrcnn import maskrcnn_to_pmml
		pmmlObj=maskrcnn_to_pmml.MaskrcnnToPMML(model,classes=dataset_train.class_names)
		pmmlObj.export(modelPathName)
		kerasUtilities.updateStatusOfTraining(statusfileLocation,'PMML file Successfully Saved')
		return ('Done')
