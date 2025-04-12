from django.shortcuts import render
from rest_framework.views import APIView
import random

from Kiepe.main.models import DeviceAuthModel
from .models import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from Kiepe.utils.index import sendOTP
from Kiepe.kibanda.models import *
from Kiepe.customer.models import *
from Kiepe.main.models import *
from Kiepe.customer.serializers import *
from Kiepe.kibanda.serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

def generateOTP():
    OTP = []
    for i in range(4):
        OTP.append(str(random.randint(0, 9)))
    return "".join(OTP)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
    'refresh': str(refresh),
    'access': str(refresh.access_token),
    }

class IsUserExist(APIView):
    def post(self ,request):
        phone = request.data.get("phone")
        User = get_user_model()
        users = User.objects.filter(phone_number=phone)
        if users.count() > 0:
            user = users.last()

            token = get_tokens_for_user(user)
            access_token = token['access']

            return Response({
                "message": "User exist",
                "user_id": user.id,
                "accessToken": access_token,
                "user_group": "customer" if hasattr(user, "customer") else "kibanda",
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_200_OK)
        
is_user_exist = IsUserExist.as_view()

class CheckUserExistByPhone(APIView):
    def get(self, request):
        phone = self.request.GET.get('phone')
        User = get_user_model()
        users = User.objects.filter(phone_number=phone)

        if users.count() > 0:
            user = user.last()
            


class LoginAPIView(APIView):
    def post(self, request):
        try:
            phone = request.data.get("phone")
            password = request.data.get("password")

            User = get_user_model()

            user = authenticate(request, username=phone, password=password)

            if user is not None:
                # generate accessToken for that user.
                token = get_tokens_for_user(user)
                access_token = token['access']
                # then we have the user..
                # i should get the category of that user to save to return his profile serializer...

                if hasattr(user, "customer"):
                    customer = user.customer
                    serialize = CustomerProfileSerializer(customer)
                    
                    return Response({
                        "message": "Login successful",
                        "data": { **serialize.data, 'accessToken': access_token }
                    }, status=status.HTTP_200_OK)

                elif hasattr(user, "kibanda"):
                    kibanda = user.kibanda
                    serialize = KibandaProfileSerializer(kibanda)

                    return Response({
                        "message": "Login successful",
                        "data": { **serialize.data, 'accessToken': access_token }
                    }, status=status.HTTP_200_OK)
            
                else:
                    return Response({
                        "message": "Unrecognized user group"
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
            else:
                return Response({
                    "message": "Invalid credentials"
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            print(e)
            return Response({
                "message": "Login failed"
            }, status=status.HTTP_400_BAD_REQUEST)


login = LoginAPIView.as_view()            

class ValidateOTPAPIView(APIView):
    def post(self, request):
        try:
            phone = request.data.get('phone_number')
            OTP = request.data.get('otp')
            print('OTP ', OTP, phone)
            userOTP = UserOTP.objects.filter(phone=phone, otp=OTP)
            if userOTP.count() > 0:
                userOTP = userOTP.first()
                userOTP.alreadyUsed = True
                userOTP.save()

                # then allow the user to set the new pin where we'll store it in our auth user model and we'll create a new user
                return Response({
                    "message": "OTP validated successfully"
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    "message": "Invalid OTP"
                }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({
                "message": "OTP validation failed"
            }, status=status.HTTP_400_BAD_REQUEST)

validate_otp = ValidateOTPAPIView.as_view()        

class GenerateOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data.get('phone_number')
            OTP = generateOTP()
            # store the OTP and phone number in the database
            # check if there is phone number of that ..
            existingOTP = UserOTP.objects.filter(phone=phone)
            if (existingOTP.count() > 0):
                existingOTP = existingOTP.first()
                existingOTP.otp = OTP
                existingOTP.alreadyUsed = False
                existingOTP.save()
            else:
                userOTP = UserOTP.objects.create(
                    phone=phone,
                    otp=OTP
                )
                
                userOTP.save()
            
            # send this message to the user phone number
            message = f"Nambari ya kuthibitisha, {OTP}"
            # sendOTP(phone, message)
            print('this is otp... ', OTP)

            return Response({
                "message": "OTP sent successfully",
                "OTP": OTP
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("something went wrong ", e)
            return Response({
                "message": "Unable to send OTP"
            }, status=status.HTTP_400_BAD_REQUEST)
        
send_otp = GenerateOTPAPIView.as_view()

class RegisterUserAPIView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        user_group = request.data.get('usergroup')
        pin = request.data.get('pin')
        deviceID = request.data.get('deviceID')
        print(phone, user_group, pin, deviceID)
        try:
            
            if user_group == "customer":
                # kumbuka hapa tume-omit 'email' but we said its required_fields in our Auth Model let's see if this will work..
                user = get_user_model().objects.create_user(
                    phone_number=phone,
                    password = pin,
                    email="notset@gmail.com"
                )
                user.save()
                customer = CustomerProfile.objects.create(
                    user=user
                )
                customer.save()

                # at the end lets save the 'deviceID'
                devices = DeviceAuthModel.objects.filter(modelId=deviceID)
                if devices.count() > 0:
                    device = devices.first()
                    device.pin = pin
                    device.save()
                else:
                    device = DeviceAuthModel.objects.create(
                        modelId=deviceID,
                        pin = pin
                    )
                    device.save()

                token = get_tokens_for_user(user)
                access_token = token['access']

                serialize = CustomerProfileSerializer(customer)
                data = { **serialize.data, 'accessToken': access_token }

                return Response(data , status=status.HTTP_200_OK)



            elif user_group == "kibanda":
                # kumbuka hapa tume-omit 'email' but we said its required_fields in our Auth Model let's see if this will work..
                user = get_user_model().objects.create_user(
                    phone_number=phone,
                    password = pin,
                    email="notset@gmail.com"
                )
                user.save()
                kibanda = KibandaProfile.objects.create(
                    user=user,
                )
                kibanda.save()

                # at the end lets save the 'deviceID'
                devices = DeviceAuthModel.objects.filter(modelId=deviceID)
                if devices.count() > 0:
                    device = devices.first()
                    device.pin = pin
                    device.save()
                else:
                    device = DeviceAuthModel.objects.create(
                        modelId=deviceID,
                        pin = pin
                    )
                    device.save()

                kibanda_status = KibandaStatus.objects.create(
                    kibanda=kibanda
                )
                kibanda_status.save()

                # we should have payment instance of the created kibanda
                payment = KibandaPayments.objects.create(
                    kibanda=kibanda
                )
                
                payment.save()

                token = get_tokens_for_user(user)
                access_token = token['access']

                serialize = KibandaProfileSerializer(kibanda)
                data = { **serialize.data, 'accessToken': access_token }

                return Response(data, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    "message": "Invalid user group"
                }, status=status.HTTP_400_BAD_REQUEST)
            
        
        except Exception as e:
            print(e)
            return Response({
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


register_user = RegisterUserAPIView.as_view()


class GetUserAPIVIew(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user
        print("USER ", user)

        token = get_tokens_for_user(user)
        access_token = token['access']

        if (user.is_superuser):
            return Response({
                "id": user.id,
                "email": user.email,
                "phone": user.phone_number,
                "is_superuser": user.is_superuser,
                "accessToken": access_token,
            }, status=status.HTTP_200_OK)
            
        elif hasattr(user, 'customer'):
            customer = user.customer
            serialize = CustomerProfileSerializer(customer)
            
            return Response({ **serialize.data, 'accessToken': access_token }, status=status.HTTP_200_OK)

        elif hasattr(user, 'kibanda'):
            kibanda = user.kibanda
            serialize = KibandaProfileSerializer(kibanda)

            return Response({**serialize.data, 'accessToken': access_token }, status=status.HTTP_200_OK)
        else:
            pass

get_user = GetUserAPIVIew.as_view()

class SetUserLoginPIN(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        pin = request.data.get('pin')

        user = request.user

        user.password = pin

        user.save()

        token = get_tokens_for_user(user)
        access_token = token['access']
        
        if (user.is_superuser):
            return Response({
                "id": user.id,
                "email": user.email,
                "phone": user.phone_number,
                "is_superuser": user.is_superuser,
                "accessToken": access_token,
            }, status=status.HTTP_200_OK)
            
        elif hasattr(user, 'customer'):
            customer = user.customer
            serialize = CustomerProfileSerializer(customer)
            
            return Response({ **serialize.data, 'accessToken': access_token }, status=status.HTTP_200_OK)

        elif hasattr(user, 'kibanda'):
            kibanda = user.kibanda
            serialize = KibandaProfileSerializer(kibanda)

            return Response({**serialize.data, 'accessToken': access_token }, status=status.HTTP_200_OK)
        else:
            pass

set_user_pin = SetUserLoginPIN.as_view()