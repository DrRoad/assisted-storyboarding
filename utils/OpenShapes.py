import os
import cv2
import numpy as np
from utils.experiments.opt import Options
from utils.experiments.context import Context
from utils.experiments.shapes import Shapes
import time
import pdb

def main(query_path, dump_path):
	opt = Options().parse(['--INPUT_MAP', query_path, '--INSTANCE_MAP', query_path, '--DUMP_DATA_PATH', dump_path])
	#pdb.set_trace()
	query_list = sorted(os.listdir(opt.QUERY_LABEL_PATH))
	context = Context(opt)
	shapes = Shapes(opt)

	
	for i in range(0, len(query_list)):
		img = cv2.cvtColor(cv2.imread(os.path.join(opt.QUERY_LABEL_PATH, query_list[i])), cv2.COLOR_BGR2RGB)
		if i==0:
			CONTEXT_MAP = img
		else:
			img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
			_ , mask = cv2.threshold(img_gray, 2, 255, cv2.THRESH_BINARY_INV)
			CONTEXT_MAP_masked = cv2.bitwise_and(CONTEXT_MAP, CONTEXT_MAP, mask=mask)

			mask_inv = cv2.bitwise_not(mask)
			img_masked = cv2.bitwise_and(img, img, mask= mask_inv)
			
			CONTEXT_MAP = cv2.add(CONTEXT_MAP_masked, img_masked)
 	

	CONTEXT_MAP = np.array(CONTEXT_MAP, dtype=np.uint32)	
	LABEL_CONTEXT_MAP = np.uint8(shapes.convert_colors_to_labels(CONTEXT_MAP))
	
	# GET THE EXEMPLAR MATCHES -- 
	EXEMPLAR_MATCHES = context.get_exemplars(LABEL_CONTEXT_MAP)
	
	for i in range(0,len(query_list)):
		# READ THE IMAGE -- 
		#print('FILE NAME: ' + query_list[i])
		
		ith_DUMP_DATA_PATH = os.path.join(dump_path, (query_list[i]).replace('.png', '/'))
		if not os.path.exists(ith_DUMP_DATA_PATH):
	                        os.makedirs(ith_DUMP_DATA_PATH)
		
	        # Convert to numpy arrays
#		input_map = np.array(cv2.imread(os.path.join(opt.QUERY_LABEL_PATH, query_list[i])), dtype=np.uint32)
#		input_map_img = cv2.cvtColor(cv2.imread(os.path.join(opt.QUERY_LABEL_PATH, query_list[i])), cv2.COLOR_BGR2RGB)
#		input_map_img_gray = cv2.cvtColor(input_map_img, cv2.COLOR_RGB2GRAY)
		#_, mask = cv2.threshold(input_map_img_gray, 2, 255, cv2.THRESH_BINARY_INV)
#		rect = cv2.boundingRect(cv2.findNonZero(input_map_img_gray))
		
#		cropped_image = input_map_img[rect[1]:rect[3]+rect[1], rect[0]:rect[2]+rect[0]]
#		

		input_map = np.array(cv2.cvtColor(cv2.imread(os.path.join(opt.QUERY_LABEL_PATH, query_list[i])), cv2.COLOR_BGR2RGB), dtype=np.uint32)
		
#		input_map = np.array(cropped_image, dtype=np.uint32)
		instance_map = np.array(cv2.imread(os.path.join(opt.QUERY_INST_PATH,  query_list[i])), dtype=np.uint32)

		

		#pdb.set_trace()	
		LABEL_MAP = np.uint8(shapes.convert_colors_to_labels(input_map))
	# 	LABEL_MAP = cv2.imread(query_path + query_list[i])
		#pdb.set_trace()
		#LABEL_MAP = LABEL_MAP[:,:,0]
		INST_MAP = np.int32(instance_map)
	# 	INST_MAP = np.int32(cv2.imread(query_path + query_list[i]))    
		# GET THE EXEMPLAR MATCHES -- 
		#EXEMPLAR_MATCHES = context.get_exemplars(LABEL_MAP)
	
		# GET THE IMAGE OUTPUTS -- 
		image_outputs = shapes.get_outputs(LABEL_MAP, INST_MAP, EXEMPLAR_MATCHES)
		
		fin_outputs = shapes.finalize_images(image_outputs)
		#pdb.set_trace()	
		for ni in range(0,len(image_outputs)):
			cv2.imwrite(os.path.join(ith_DUMP_DATA_PATH, str(ni) + '.png'), fin_outputs[ni]['im'])
	