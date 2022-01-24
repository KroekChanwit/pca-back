from os import name
from pyexpat import model
# from django.shortcuts import render
from rest_framework import generics, serializers
from rest_framework import permissions, status
# from rest_framework import response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated ,AllowAny
# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.views import TokenViewBase
# from .serializers import UserSerializer, UserSerializerWithToken ,MyTokenObtainPairSerializer,TokenRefreshLifetimeSerializer
# from .db import connect_db
import json
import pandas as pd
import requests
from PIL import Image
from django.core.files.storage import FileSystemStorage

# Create your views here.
# class UserList(APIView):
#     """
#     Create a new user. It's called 'UserList' because normally we'd have a get
#     method here too, for retrieving a list of all User objects.
#     """
#     permission_classes = (permissions.AllowAny,)
#     def post(self,request):
#         user = request.data.get('user')
#         if not user:
#             return Response({'response' : 'error', 'message' : 'No data found'})
#         serializer = UserSerializerWithToken(data = user)
#         if serializer.is_valid():
#             saved_user = serializer.save()
#         else:
#             return Response({"response" : "error", "message" : serializer.errors})
#         return Response({"response" : "success", "message" : "user created succesfully"})

# class CreateUserView(APIView):
#     permission_classes = (permissions.AllowAny,)
#     def post(self, request, format=None):
#         print(request.data)
#         serializer = UserSerializerWithToken(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer

# class TokenRefreshView(TokenViewBase):
#     """
#         Renew tokens (access and refresh) with new expire time based on specific user's access token.
#     """
#     serializer_class = TokenRefreshLifetimeSerializer


# config database
# obj = {"databasename":"cross-care","ip":"cross-care-do-user-10292029-0.b.db.ondigitalocean.com","port":"25060","username":"cc","password":"lPIn23IZwnY978G6"}
import tensorflow as tf
from tensorflow import keras
import os, sys
import time
import cv2
import datetime
import glob
import itertools
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.models import Model, load_model
from keras.preprocessing import image
# from sklearn.metrics import accuracy_score
from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input

base_model_dir = 'C:\\Users\\Chanwit\\Desktop\\project\\Model\\'
        # base_model_dir = 'C:\\Users\\User\\Desktop\\Model\\'

model1 = load_model(base_model_dir + 'backup_model_train-299-40-04-2classes-new_InceptionResNetV2_780_200ep.hdf5')
model2 = load_model(base_model_dir + 'backup_model_train-299-40-04-2classes-new_InceptionV3_311_200ep.hdf5')
model3 = load_model(base_model_dir + 'backup_model_train-299-40-04-2classes-new_ResNet50_175_200ep.hdf5')
model4 = load_model(base_model_dir + 'backup_model_train-299-40-04-2classes-new_ResNet50V2_190_200ep.hdf5')
model5 = load_model(base_model_dir + 'backup_model_train-299-40-04-2classes-new_Xception_132_200ep.hdf5')
    

class PCa(generics.RetrieveUpdateDestroyAPIView):

    @api_view(['POST'])
    @permission_classes((AllowAny, ))
    def uploadImage(request):
        
        ########## receive image from frontend ##########

        file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)

        path_media = 'C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\'
        # path_media = 'C:\\Users\\User\\Desktop\\pca-project\\pca-back\\media\\'

        path = os.path.join(path_media, filename)       

        # print(model2.summary())
        def prepare(img_path):
                img = image.load_img(img_path, target_size=(299,299))
                x = image.img_to_array(img)
                x = x/255
                return np.expand_dims(x, axis=0)

        models = [model1, model2, model3, model4, model5]
        # models = [model2, model3, model4, model5]
        
        # result2 = [model.predict([prepare(path)]) for model in models]
        # x=np.argmax(result2,axis=1)
        # print(x)

        preds = [model.predict([prepare(path)]) for model in models]
        os.remove(path)

        preds = np.array(preds)
        
        # print(preds)

        sum_benign = 0
        sum_malignant = 0
        
        for x in preds:
                for y in x:
                        sum_benign = sum_benign + y[0]
                        sum_malignant = sum_malignant + y[1]

        result_benign = np.around((sum_benign/5)*100, decimals=2)
        result_malignant = np.around((sum_malignant/5)*100, decimals=2)

        result_image = []

        if(result_benign > result_malignant):
                result_image.append("Benign : ")
                result_image.append(str(result_benign) + " %")
        else:
                result_image.append("Malignant : ")
                result_image.append(str(result_malignant) + " %")

        # model = load_model('C:\\Users\\Chanwit\\Desktop\\project\\Model\\backup_model_train-299-40-01-2classes-new_ResNet50_175_200ep.hdf5')
        # model = load_model('C:\\Users\\User\\Desktop\\Model\\backup_model_train-299-40-01-2classes-new_ResNet50_175_200ep.hdf5')
        # model.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])
        
        # def prepare(img_path):
        #         img = image.load_img(img_path, target_size=(299,299))
        #         x = image.img_to_array(img)
        #         x = x/255
        #         return np.expand_dims(x, axis=0)

        # res = model.predict([prepare(path)])
        # results = [[i,r] for i,r in enumerate(res)]
        # results.sort(key=lambda x: x[1], reverse=True)
        # for r in results:
        #         print(str(r[1]))

        return Response(result_image, status=status.HTTP_200_OK)

# def insert_api(request, status):

#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]

#     else:
#         ip = request.META.get('REMOTE_ADDR')

#     connect = connect_db(obj)
#     con = connect.cursor()

#     con.execute(f"""
                
#     INSERT INTO public.api_transaction
#     (ip_address, api, browser, response_status, "method", uid)
#     VALUES('{ip}', '{request.META.get('PATH_INFO')}', '{request.META.get('TERM_PROGRAM')}', '{status}', '{request.META.get('REQUEST_METHOD')}','2');

#     """)
#     connect.commit()

#     con.close()

# def provide_token_login(profile):
#     url = "http://localhost:8080/api/token/"
#     payload = json.dumps({
#         "username": f"{profile['username']}",
#         "password": f"med{profile['password']}"
#     })
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     data = json.loads(response.text)
#     return data

# def test_api_imed():
#     url = "http://10.141.10.17:8091/api/imed/login"
    
