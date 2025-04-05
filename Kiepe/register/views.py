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
def generateOTP():
    OTP = []
    for i in range(4):
        OTP.append(str(random.randint(0, 9)))
    return "".join(OTP)

class IsUserExist(APIView):
    def post(self ,request):
        phone = request.data.get("phone")
        User = get_user_model()
        user = User.objects.filter(phone_number=phone)
        if user.count() > 0:
            return Response({
                "message": "User exist",
                "user_id": user.last().id,
                "user_group": "customer" if hasattr(user.last(), "customer") else "kibanda",
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_200_OK)
        
is_user_exist = IsUserExist.as_view()


class LoginAPIView(APIView):
    def post(self, request):
        try:
            phone = request.data.get("phone")
            password = request.data.get("password")


            User = get_user_model()

            user = authenticate(request, username=phone, password=password)
            if user is not None:
                # then we have the user..
                # i should get the category of that user to save to return his profile serializer...
                if hasattr(user, "customer"):
                    customer = user.customer
                    serialize = CustomerProfileSerializer(customer)

                    return Response({
                        "message": "Login successful",
                        "data": serialize.data
                    }, status=status.HTTP_200_OK)

                elif hasattr(user, "kibanda"):
                    kibanda = user.kibanda
                    serialize = KibandaProfileSerializer(kibanda)
                    return Response({
                        "message": "Login successful",
                        "data": serialize.data
                    }, status=status.HTTP_200_OK)
            
                else:
                    return Response({
                        "message": "Unrecognized user group"
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
            else:
                return Response({
                    "message": "Invalid credentials"
                }, status=status.HTTP_200_OK)
        
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
            sendOTP(phone, message)
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

                serialize = CustomerProfileSerializer(customer)
                return Response(serialize.data , status=status.HTTP_200_OK)



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

                serialize = KibandaProfileSerializer(kibanda)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
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





