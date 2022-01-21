# serializers -->> reuturn data with json format
import datetime
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
# from django.utils.six import text_type
from django.utils import timezone
# from .models import Lab

import jwt


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','username','is_superuser','first_name', 'last_name')


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password', 'first_name','last_name')



class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())

        return jwt.encode(data, "secret", algorithm="HS256")

def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])


SUPERUSER_LIFETIME = datetime.timedelta(minutes=120)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    # def validate(self, attrs):
    #     data = super().validate(attrs)
    #     refresh = self.get_token(self.user)
    #     data['refresh'] = str(refresh)
    #     data['access'] = str(refresh.access_token)

    #     # Add extra responses here
    #     data['username'] = self.user.username
    #     data['groups'] = self.user.groups.values_list('name', flat=True)
    #     # if api_settings.UPDATE_LAST_LOGIN:
    #     #     update_last_login(None, self.user)
    #     return data

    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        if self.user.is_superuser:
            new_token = refresh.access_token
            new_token.set_exp(lifetime=SUPERUSER_LIFETIME)
            data['access'] = str(new_token)
        else:
            data['access'] = str(refresh.access_token)
        
                # Add extra responses here
        data['username'] = self.user.username
        data['groups'] = self.user.groups.values_list('name', flat=True)

        update_last_login(None, self.user)

        return data