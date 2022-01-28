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

base_model_dir = 'C:\\Users\\Chanwit\\Desktop\\project\\Model\\'

weight_list = list(glob.glob(os.path.join(base_model_dir, 
                                        '*40-03*.hdf5'),
                        recursive=True))
weight_list.sort()

print("Loading weights to models")
model_list = list()
for weight_path in weight_list:
        print()
        print(os.path.basename(weight_path))
        model = load_model(weight_path)
        model_list.append(model)

print("Load done.")

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

                def prepare(img_path):
                        img = image.load_img(img_path, target_size=(299,299))
                        x = image.img_to_array(img)
                        x = x/255
                        return np.expand_dims(x, axis=0)

                preds = [model.predict([prepare(path)]) for model in model_list]
                preds = np.array(preds)

                print(preds)

                os.remove(path)

                summed = np.sum(preds, axis=0)
                # result = np.argmax(summed, axis=1)

                ######## Weight avg fold1 - fold5 ########
                # ideal_weights = [0.18, 0.2, 0.02, 0.02, 0.18]

                ideal_weights = [0.4, 0.3, 0.0, 0.0, 0.1]
                ideal_weighted_preds = np.tensordot(preds, ideal_weights, axes=((0),(0)))
                ideal_weighted_ensemble_prediction = np.argmax(ideal_weighted_preds, axis=1)

                print(ideal_weighted_preds)

                result_model = np.around(np.max(preds), decimals=3)
                result_weighted = np.around(ideal_weighted_preds, decimals=3)
                result_avg= np.around(summed/5, decimals=3)

                index_model = np.where(preds == np.max(preds))
                index = index_model[0][0]

                model_list_name = ["InceptionResNetV2", "InceptionV3", "ResNet50V2", "ResNet50", "Xception"]
                model_name = model_list_name[index]

                if(ideal_weighted_ensemble_prediction == 0):
                        result_image = {
                                "name":filename,
                                "result":"Benign",
                                "props":str(result_model) + " of " + str(model_name) + " model",
                                "avg":str(result_avg[0][0]),
                                "wei":str(result_weighted[0][0])
                        }
                else:
                        result_image = {
                                "name":filename,
                                "result":"Malignant",
                                "props":str(result_model) + " of " + str(model_name) + " model",
                                "avg":str(result_avg[0][1]),
                                "wei":str(result_weighted[0][1])
                        }

                return Response(result_image, status=status.HTTP_200_OK)