from os import name
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
from keras.models import load_model
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

class PCa(generics.RetrieveUpdateDestroyAPIView):

    @api_view(['POST'])
    @permission_classes((AllowAny, ))
    def uploadImage(request):
        
        ########## receive image from frontend ##########

        # file = request.FILES['image']
        # fs = FileSystemStorage()
        # filename = fs.save(file.name, file)

        # im = Image.open("C:\\Users\\User\\Desktop\\pca-project\\pca-back\\media\\" + filename)
        # im.show()

        ########## Pre-Processing test data same as train data. ##########

        #img_width=256
        #img_height=256

        base_model_dir = 'C:\\Users\\User\\Desktop\\model\\'
        path = 'C:\\Users\\user\\Desktop\\pca-project\\pca-back\\media\\Malignant.png'

        weight_list = list(glob.glob(os.path.join(base_model_dir, '*40-01*.hdf5'), recursive=True))
        weight_list.sort()

        print("Loading weights to models")
        model_list = list()
        for weight_path in weight_list:
                print()
                print(os.path.basename(weight_path))
                model = load_model(weight_path)
                model_list.append(model)

        print("Load done.")

        # model = load_model('C:\\Users\\User\\Desktop\\Model\\backup_model_train-299-40-01-2classes-new_ResNet50_175_200ep.hdf5')
        model.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])
        
        def prepare(img_path):
                img = image.load_img(img_path, target_size=(299,299))
                x = image.img_to_array(img)
                x = x/255
                return np.expand_dims(x, axis=0)

        result = model.predict([prepare(path)])
        d=image.load_img(path)
        plt.imshow(d)
        x=np.argmax(result,axis=1)
        print(x)

        res = model.predict([prepare(path)])
        results = [[i,r] for i,r in enumerate(res)]
        results.sort(key=lambda x: x[1], reverse=True)
        for r in results:
                print(str(r[1]))

        return Response(status=status.HTTP_200_OK)

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
    
