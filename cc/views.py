from os import name
from django.shortcuts import render
from rest_framework import generics, serializers
from rest_framework import permissions, status
from rest_framework import response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenViewBase
from .serializers import UserSerializer, UserSerializerWithToken ,MyTokenObtainPairSerializer,TokenRefreshLifetimeSerializer
from .db import connect_db
import json
import pandas as pd
import requests
from PIL import Image
from django.core.files.storage import FileSystemStorage

# Create your views here.
class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """
    permission_classes = (permissions.AllowAny,)
    def post(self,request):
        user = request.data.get('user')
        if not user:
            return Response({'response' : 'error', 'message' : 'No data found'})
        serializer = UserSerializerWithToken(data = user)
        if serializer.is_valid():
            saved_user = serializer.save()
        else:
            return Response({"response" : "error", "message" : serializer.errors})
        return Response({"response" : "success", "message" : "user created succesfully"})

class CreateUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, format=None):
        print(request.data)
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class TokenRefreshView(TokenViewBase):
    """
        Renew tokens (access and refresh) with new expire time based on specific user's access token.
    """
    serializer_class = TokenRefreshLifetimeSerializer


# config database
obj = {"databasename":"cross-care","ip":"cross-care-do-user-10292029-0.b.db.ondigitalocean.com","port":"25060","username":"cc","password":"lPIn23IZwnY978G6"}

class PCa(generics.RetrieveUpdateDestroyAPIView):

    @api_view(['POST'])
    @permission_classes((AllowAny, ))
    def uploadImage(request):

        file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)

        im = Image.open("C:\\Users\\User\\Desktop\\project\\cc-back\\media\\" + filename)
        im.show()

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


def insert_api(request, status):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]

    else:
        ip = request.META.get('REMOTE_ADDR')

    connect = connect_db(obj)
    con = connect.cursor()

    con.execute(f"""
                
    INSERT INTO public.api_transaction
    (ip_address, api, browser, response_status, "method", uid)
    VALUES('{ip}', '{request.META.get('PATH_INFO')}', '{request.META.get('TERM_PROGRAM')}', '{status}', '{request.META.get('REQUEST_METHOD')}','2');

    """)
    connect.commit()

    con.close()

def provide_token_login(profile):
    url = "http://localhost:8080/api/token/"
    payload = json.dumps({
        "username": f"{profile['username']}",
        "password": f"med{profile['password']}"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    return data

def test_api_imed():
    url = "http://10.141.10.17:8091/api/imed/login"
    
