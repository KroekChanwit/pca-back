from os import name
from pyexpat import model
from rest_framework import generics, serializers
from rest_framework import permissions, status
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
import pandas as pd
from PIL import Image
from django.core.files.storage import FileSystemStorage

import openslide
import py_wsi
from datetime import datetime
from patchify import patchify
from tqdm import tqdm

import tensorflow as tf
from tensorflow import keras
import os, sys
import cv2
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.models import Model, load_model
from keras.preprocessing import image
from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input

# base_model_dir = 'C:\\Users\\Chanwit\\Desktop\\project\\Model\\'

# weight_list = list(glob.glob(os.path.join(base_model_dir, 
#                                         '*40-03*.hdf5'),
#                         recursive=True))
# weight_list.sort()

# print("Loading weights to models")
# model_list = list()
# for weight_path in weight_list:
#         print()
#         print(os.path.basename(weight_path))
#         model = load_model(weight_path)
#         model_list.append(model)

# print("Load done.")

class PCa(generics.RetrieveUpdateDestroyAPIView):

        @api_view(['POST'])
        @permission_classes((AllowAny, ))
        def uploadImage(request):
                
                ########## receive image from frontend ##########

                file = request.FILES['image']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)

                path_media = 'C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\'
                path = os.path.join(path_media, filename)   

                # import py_wsi.imagepy_toolkit as tk
                
                file_dir = "C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\"
                db_location = "C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\"
                xml_dir = file_dir
                patch_size = 256
                level = 10
                db_name = "patch_db"
                overlap = 0
                
                label_map = {'BG':0,
                                'FG': 1,
                                'N': 2,
                                'P3': 3,
                                'P4': 4,
                                'P5': 5,
                                }
                
                turtle = py_wsi.Turtle(file_dir, db_location, db_name, 
                                        xml_dir=xml_dir, label_map=label_map, 
                                        )
                
                
                level_count, level_tiles, level_dims = turtle.retrieve_tile_dimensions(filename, patch_size=256)
                print("Level count:         " + str(level_count))
                print("Level tiles:         " + str(level_tiles))
                print("Level dimensions:    " + str(level_dims))
                
                patch_size = level_dims[-2]
                level = level_count-2
                overlap = 0
                if patch_size[0]>patch_size[1]:
                        selected_size = patch_size[0]
                else:
                        selected_size = patch_size[1]

                start1 = datetime.now()
                print("\nExtracting WSI at 20x...")
                
                slide_data = turtle.retrieve_sample_patch(filename, 
                                                selected_size, #select greater than one
                                                level, 
                                                overlap=0)
                # bar()
                
                # large_image = np.asarray(slide_data, dtype='uint8')
                # print(large_image.shape)
                
                stop1 = datetime.now() - start1
                print("stop1: ", stop1)

                TILE_SIZE = 256
                large_image = np.array(slide_data)

                print("Extracting patches of image and mask")
                start1 = datetime.now()
                patches = patchify(large_image, (TILE_SIZE, TILE_SIZE, 3), 
                                step=TILE_SIZE)  #Step=256 for 256 patches means no overlap
                patches = np.array(patches, dtype='uint8')
                patches = np.squeeze(patches)
                print(patches.shape)
                stop1 = datetime.now() - start1
                print("stop1: ", stop1)

                def detect_bg(patch, prob=False):
                        # image = cv2.imread('test24.png')
                        # image = np.array(patch * 255, dtype='uint8')
                        
                        h, w, _ = patch.shape
                        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
                        
                        thresh = cv2.adaptiveThreshold(gray, 255,
                                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY_INV, 11, 2)
                        
                        pixels = cv2.countNonZero(thresh)
                        pixel_ratio = (pixels/(h * w)) * 100
                        title = 'Pixel ratio: {:.2f}%'.format(pixel_ratio)
                        
                        if prob:
                                print(title)
                                plt.figure()  
                                plt.subplot(1,2,1)
                                plt.title("Original Patch")
                                plt.imshow(patch)
                                plt.subplot(1,2,2)
                                plt.title(title)
                                plt.imshow(thresh)
                        
                        return pixel_ratio

                time1 = datetime.now()
                print('\nSaving pathes...')
                cnt=0
                path_patches = 'C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\patches\\'
                patch_dir = os.path.join(path_patches, file.name + '-image20x')
                if not os.path.exists(patch_dir):
                        print("[INFO] 'creating {}' directory".format(patch_dir))
                        os.makedirs(patch_dir)
                
                patch_pass = list()
                for i in tqdm(range(patches.shape[0])):
                        for j in range(patches.shape[1]):
                        # print(i,j)
                                single_patch = patches[i,j]
                                
                                pixel_ratio = detect_bg(single_patch, prob=False)
                                if pixel_ratio > 20:
                                        # print(i, j, pixel_ratio)
                                        patch_pass.append((i,j))
                                        # plt.figure()
                                        # plt.imshow(single_patch)
                                                
                                        filename = str(i) + '_' + str(j) + '.png'
                                        filepath = os.path.join(patch_dir, filename)
                                        Image.fromarray(single_patch).save(filepath)
                                
                print('\npatches passed pixel ratios: ', len(patch_pass) )   
                time2 = datetime.now() - time1
                print(f"{time2}")

                # def prepare(img_path):
                #         img = image.load_img(img_path, target_size=(299,299))
                #         x = image.img_to_array(img)
                #         x = x/255
                #         return np.expand_dims(x, axis=0)

                # preds = [model.predict([prepare(path)]) for model in model_list]
                # preds = np.array(preds)

                # print(preds)

                # os.remove(path)

                # summed = np.sum(preds, axis=0)

                # # result = np.argmax(summed, axis=1)

                # ######## Weight avg fold1 - fold5 ########
                # # ideal_weights = [0.18, 0.2, 0.02, 0.02, 0.18]

                # ideal_weights = [0.4, 0.3, 0.0, 0.0, 0.1]
                # ideal_weighted_preds = np.tensordot(preds, ideal_weights, axes=((0),(0)))
                # ideal_weighted_ensemble_prediction = np.argmax(ideal_weighted_preds, axis=1)

                # print(ideal_weighted_preds)

                # result_model = np.around(np.max(preds), decimals=3)
                # result_weighted = np.around(ideal_weighted_preds, decimals=3)
                # result_avg= np.around(summed/5, decimals=3)

                # index_model = np.where(preds == np.max(preds))
                # index = index_model[0][0]

                # model_list_name = ["InceptionResNetV2", "InceptionV3", "ResNet50V2", "ResNet50", "Xception"]
                # model_name = model_list_name[index]

                # if(ideal_weighted_ensemble_prediction == 0):
                #         result_image = {
                #                 "name":filename,
                #                 "result":"Benign",
                #                 "props":str(result_model) + " of " + str(model_name) + " model",
                #                 "avg":str(result_avg[0][0]),
                #                 "wei":str(result_weighted[0][0])
                #         }
                # else:
                #         result_image = {
                #                 "name":filename,
                #                 "result":"Malignant",
                #                 "props":str(result_model) + " of " + str(model_name) + " model",
                #                 "avg":str(result_avg[0][1]),
                #                 "wei":str(result_weighted[0][1])
                #         }

                # return Response(result_image, status=status.HTTP_200_OK)
                return Response(status=status.HTTP_200_OK)
