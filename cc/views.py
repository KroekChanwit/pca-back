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
import numpy as np
import pandas as pd
from keras.models import Model, load_model
from keras.preprocessing import image
# from sklearn.metrics import accuracy_score

class PCa(generics.RetrieveUpdateDestroyAPIView):

    @api_view(['POST'])
    @permission_classes((AllowAny, ))
    def uploadImage(request):

        file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)

        # base_model_dir = 'C:\\Users\\Chanwit\\Desktop\\project\\Model'

        # weight_list = list(glob.glob(os.path.join(base_model_dir, '*40-05*.hdf5'), recursive=True))
        # weight_list.sort()      

        # print(weight_list)

        # print("Loading weights to models")
        # model_list = list()
        # for weight_path in weight_list:
        #         print()
        #         print(os.path.basename(weight_path))
        #         model = load_model(weight_path)
        #         model_list.append(model)

        # print("Load done.")
        # def prepare(filepath):
        #         IMG_SIZE = 256
        #         img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        #         new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        #         return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

        # img = cv2.imread('C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\002040_002550.jpg')

        model = load_model('C:\\Users\\Chanwit\\Desktop\\project\\Model\\backup_model_train-299-40-01-2classes-new_Xception_132_200ep.hdf5')
        # prediction = model.predict([prepare('002040_002550.jpg')])

        test_image = image.load_img('C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\Benign.png', target_size = (299, 299))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis = 0)
        result = model.predict(test_image)

        print(result)

        if(result[0][0] == 0):
                prediction = 'Benign'
                print(prediction)
        else:
                prediction = 'Malignant'
                print(prediction)
        # print(prediction)
        # model.compile(optimizer='adam',
        #       loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        #       metrics=['accuracy'])
        
        # model_fit = model.fit(img,
        #                         steps_per_epoch = 3,
        #                         epochs = 10)

        # val = model.predict(img)
        # print(val)
        

        # # test_img = img.reshape((1,299))

        # img_class = model.predict_classes(test_img)
        # prediction = img_class[0]
        # classname = img_class[0]
        # print("Class: ",classname)
        # # img = img.reshape((299,299))
        # plt.imshow(img)
        # plt.title(classname)
        # plt.show()

#         window_name = 'image'

#         Using cv2.imshow() method 
#         Displaying the image 
#         cv2.imshow(window_name, img)

        # classes = model.predict_classes(img)

        # print(classes)
        # im = Image.open("C:\\Users\\Chanwit\\Desktop\\pca-project\\pca-back\\media\\" + filename)
        # im.show()

        return Response(status=status.HTTP_200_OK)
        ################################ Database BHH can read only
        ################################ Connect database from BDMS (wifi: BDMS_APP)

        # 'postgres://bhhsepsis:sepsis@bhh@10.141.13.3:5432/imed_bhh'

        # obj = {"databasename":"imed_bhh","ip":"10.141.13.3","port":"5432","username":"bhhsepsis","password":"sepsis@bhh"}

        # try:
        #     connect = connect_db(obj)
        #     con = connect.cursor()
        #     con.execute(f"""
        #     SELECT bhh_cc_json_patient_profile('07-01-021535')
        #     """)
        #     connect.commit()

        #     result = con.fetchall()

        #     con.close()

        #     return Response(result,status=status.HTTP_200_OK)

        # except NameError:
        #     print(NameError)
        #     return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


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
    
