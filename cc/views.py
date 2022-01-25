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
                                        '*40-04*.hdf5'),
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
                os.remove(path)

                print(preds)

                preds = np.array(preds)
                summed = np.sum(preds, axis=0)
                result = np.argmax(summed, axis=1)
                
                print(result)
       
                ideal_weights = [0.2, 0.4, 0.0, 0.0, 0.4]  ######## ปรับใหม่ * ไปรันโค้ด evaluate ใหม่ ของโมเดล Fold 4 เอา weight มาใส่ ########

                ideal_weighted_preds = np.tensordot(preds, ideal_weights, axes=((0),(0)))
                # ideal_weighted_ensemble_prediction = np.argmax(ideal_weighted_preds, axis=1)

                print(ideal_weighted_preds)

                sum_benign = 0
                sum_malignant = 0
                
                for x in preds:
                        for y in x:
                                sum_benign = sum_benign + y[0]
                                sum_malignant = sum_malignant + y[1]

                result_benign = np.around((sum_benign/5)*100, decimals=2)
                result_malignant = np.around((sum_malignant/5)*100, decimals=2)

                result_image = []

                if(result == 0):
                        result_image.append("Benign : ")
                        result_image.append(str(result_benign) + " %")
                else:
                        result_image.append("Malignant : ")
                        result_image.append(str(result_malignant) + " %")


                return Response(result_image, status=status.HTTP_200_OK)
                # return Response(status=status.HTTP_200_OK)
