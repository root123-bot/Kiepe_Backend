from django.shortcuts import render
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
import string, hashlib, random, requests
from django.http import JsonResponse
from Kiepe.utils.index import sendNotification
from Kiepe.main.models import *
from Kiepe.main.views import *
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView



# HII UNAPROCESS PAYMENTS ILI UTUPE PUSH KWA MTEJA
@api_view(['POST'])
def process_payment(request):
    if request.method == 'POST':
      
        selected_payment_method = request.data.get('payment_method')
        
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        phone_no = request.data.get('phone_number')
        phone_no = format_mobile_phone_number(phone_no)
        print(user_id, amount, phone_no, selected_payment_method)

        product_name = 'Kiepe Service'
        reference_number = ''
        # //Create reffere numbers ===========
        # existing_reference_number = PaymentReferenceNumber.objects.values_list('reference_no', flat=True).filter(reference_no__contains='AAP').last()
        existing_reference_number = PaymentReferenceNumbers.objects.values_list('reference_number', flat=True)
        existing_reference_number = list(existing_reference_number)

        flag = True
        while flag:
            reference_number = str(random.randint(1000000000000000000, 99999999990000000000))
            if reference_number not in existing_reference_number:
                flag = False 


        # last_used_reference_number = PaymentReferenceNumber.get_last_no(selected_payment_method)
        rnumber = PaymentReferenceNumbers.objects.create(
            reference_number = reference_number,
        )

        rnumber.save()
      
        transaction = TransactionRecords.objects.create(
            payed_by = get_user_model().objects.get(pk=user_id),
            amount = amount,
            reference_number = rnumber,
            status = 'NOT PAID',
        )

        transaction.save()

        message = ''

        if selected_payment_method == '1':  # tigopesa
            message = pay_with_tigopesa(phone_no, amount, reference_number)
            # returned by method, as gateway_feedback
        if selected_payment_method == '2':  # mpesa
            message = pay_with_mpesa(phone_no, amount,reference_number)
        if selected_payment_method == '3':  # Airtel
            message = pay_with_airtelMoney(phone_no, amount,reference_number)
      
        # this will be returned/posted after we call this api
        feedback = {
            'feedback': message,
            'payment_method': selected_payment_method,
            'user_id': user_id,
            'amount': amount,
            'phone_no': phone_no
        }

        return JsonResponse(feedback, safe=False)

from datetime import datetime as dt
def pay_with_mpesa(phone_no, amount,reference_number):
    # has_string = 'mainstream|'.date('d-m-Y')
    today_date = dt.today().strftime('%d-%m-%Y')
    hash_string = "mainstream|"+today_date
    authentication_key = hashlib.md5(hash_string.encode()).hexdigest()

    call_back_url = "https://6964-41-59-195-10.ngrok-free.app/api/paymentcallbackhandler"
    

    json_data = {
        "api_source": "MAINSTREAM MEDIA",
        "api_to": "Mpesa",
        "product": "Service Subscription",
        "amount": amount,
        "callback": call_back_url,
        "hash": authentication_key,
        "user": "mainstream",
        "mobileNo": phone_no,
        "reference": reference_number
    }

    # send post request
    gateway_url = "https://vodaapi.evmak.com/test/"
    headers = {'Content-Type': 'application/json'}
    payment_request = requests.post(gateway_url, headers=headers, json=json_data) 

    gateway_feedback = payment_request.json()

    return gateway_feedback


from datetime import datetime as dt
def pay_with_tigopesa(phone_no, amount,reference_number):
    
    today_date = dt.today().strftime('%d-%m-%Y')
    hash_string = "mainstream|"+today_date
    authentication_key = hashlib.md5(hash_string.encode()).hexdigest()
    # hizi callback_url inabidi tuzibadilishe tuweke api url yetu ambayo tigo ita-icall endapo mtu ameshalipia
    # ndo maana hapa unaona inaanza na "afyatap" coz ndo url ya domain husika
    call_back_url = "https://6964-41-59-195-10.ngrok-free.app/api/paymentcallbackhandler"
    

    json_data = {
        # "api_source": "MAINSTREAM MEDIA",
        "api_source": "MAINSTREAM MEDIA",
        "api_to": "TigoPesa",
        "amount": amount,
        "product": "Service Subscription",
        "callback": call_back_url,
        "hash": authentication_key,
        "user": "mainstream",
        "mobileNo": phone_no,
        "reference": reference_number
    }

    # send post request
    gateway_url = "https://mno.evmak.com/tigo/test/"
    # gateway_url = "https://vodaapi.evmak.com/test/"
    
    headers = {'Content-Type': 'application/json'}
    payment_request = requests.post(gateway_url, headers=headers, json=json_data)
    print("json data ", json_data)
    print('Payment request ', payment_request)

    # hapa ndo inapogomea
    print('dirssssssss ', dir(payment_request))
    gateway_feedback = payment_request.json()
    print("Payment request json ", gateway_feedback)
    # print('FEEDBACK------------- ------> ', gateway_feedback)
    return gateway_feedback


from datetime import datetime as dt
def pay_with_airtelMoney(phone_no, amount,reference_number):
    try:
        today_date = dt.today().strftime('%d-%m-%Y')
        hash_string = "mainstream|"+today_date
        authentication_key = hashlib.md5(hash_string.encode()).hexdigest()
        call_back_url = "https://6964-41-59-195-10.ngrok-free.app/api/paymentcallbackhandler"
        

        json_data = {
            "api_source": "MAINSTREAM MEDIA",
            "api_to": "TigoPesa",
            "amount": amount,
            "product": "Service Subscription",
            "callback": call_back_url,
            "hash": authentication_key,
            "user": "mainstream",
            "mobileNo": phone_no,
            "reference": reference_number
        }

        # send post request
        gateway_url = "https://mno.evmak.com/tigo/test/"
        # gateway_url = "https://vodaapi.evmak.com/test/"
        
        headers = {'Content-Type': 'application/json'}
        payment_request = requests.post(gateway_url, headers=headers, json=json_data)
        print("payment request ", payment_request)
        gateway_feedback = payment_request.json()
        # print('FEEDBACK------------- ------> ', gateway_feedback)
        return gateway_feedback

    except Exception as e:
        print('Error ', e)

def format_mobile_phone_number(phone_no):
    formatted_phone_no = ''
    tanzania_code = '255'

    if len(phone_no) >= 9:
        phone_no = phone_no.replace(' ', '')
        phone_no = phone_no[-9:]
        formatted_phone_no = tanzania_code + '' + phone_no

    return formatted_phone_no




class PaidCallback(APIView):
    def post(self, request, *args, **kwargs):
        status = request.data.get("ResultType")
        reference = request.data.get('ThirdPartyReference')
        if status == True or status == "Completed":
            # we should get the transaction record with that reference number 
            transaction = TransactionRecords.objects.filter(reference_number__reference_number = reference).first()  # there is no way for the reference number to be duplicated so return the first one

            if transaction is not None:
                transaction.status = 'PAID'
                transaction.save()

                # angalia hiyo transaction ilikuwa sh ngap
                amount = transaction.amount
                # 1 per day, 200 per week, 1000 per month
                if amount == 1000:
                    # give 1 day subscription
                    record = PaymentRecords.objects.create(
                        kibanda = transaction.payed_by.kibanda,
                        amount = transaction.amount,
                        start_date = datetime.now(),
                        end_date = datetime.now() + timedelta(days=1),
                    )
                    record.save()

                    # make kibanda active..
                    kibanda = transaction.payed_by.kibanda
                    kibanda.is_active = True
                    kibanda.save()

                    # send notification to user
                    token = DeviceNotificationToken.objects.filter(user=transaction.payed_by)
                    print("Token ", token)
                    if token.exists():
                        token = token.first().deviceNotificationToken
                        print("token ", token) 
                        sendNotification(
                            "Subscription Activated",
                            "Your account 1 day subscription tier has been activated after that tier expires you will be charged",
                            token,
                        )

                    notification = Notification.objects.create(
                        heading="Subscription Activated",
                        body="Your account 1 day subscription tier has been activated after that tier expires you will be charged",
                        target="kibanda",
                        is_associted_with_order = False,
                        sent_to = kibanda.user,
                    )

                    notification.save()

                elif amount == 2000:
                    # give 1 week subscription
                    record = PaymentRecords.objects.create(
                        kibanda = transaction.payed_by.kibanda,
                        amount = transaction.amount,
                        start_date = datetime.now(),
                        end_date = datetime.now() + timedelta(days=7),
                    )
                    record.save()

                    # make kibanda active..
                    kibanda = transaction.payed_by.kibanda
                    kibanda.is_active = True
                    kibanda.save()

                    # send notification to user
                    token = DeviceNotificationToken.objects.filter(user=transaction.payed_by)
                    print("Token ", token)
                    if token.exists():
                        token = token.first().deviceNotificationToken
                        print("token ", token) 
                        sendNotification(
                            "Subscription Activated",
                            "Your account 7 day subscription tier has been activated after that tier expires you will be charged",
                            token,
                        )

                    notification = Notification.objects.create(
                        heading="Subscription Activated",
                        body="Your account 1 week subscription tier has been activated after that tier expires you will be charged",
                        target="kibanda",
                        is_associted_with_order = False,
                        sent_to = kibanda.user,
                    )

                    notification.save()

                elif amount == 10000:
                    # give 1 month subscription
                    record = PaymentRecords.objects.create(
                        kibanda = transaction.payed_by.kibanda,
                        amount = transaction.amount,
                        start_date = datetime.now(),
                        end_date = datetime.now() + timedelta(days=30),
                    )
                    record.save()

                    # make kibanda active..
                    kibanda = transaction.payed_by.kibanda
                    kibanda.is_active = True
                    kibanda.save()

                    # send notification to user
                    token = DeviceNotificationToken.objects.filter(user=transaction.payed_by)
                    print("Token ", token)
                    if token.exists():
                        token = token.first().deviceNotificationToken
                        print("token ", token) 
                        sendNotification(
                            "Subscription Activated",
                            "Your account 1 month subscription tier has been activated after that tier expires you will be charged",
                            token,
                        )

                    notification = Notification.objects.create(
                        heading="Subscription Activated",
                        body="Your account 1 month subscription tier has been activated after that tier expires you will be charged",
                        target="kibanda",
                        is_associted_with_order = False,
                        sent_to = kibanda.user,
                    )

                    notification.save()

                else:
                    pass

                return Response({"status": "success"}, status=status.HTTP_200_OK)
            
            else:
                return Response({"status": "failed", "message": "Transaction has no reference number"}, status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({"status": "failed", "message": "Transaction was not successful"}, status=status.HTTP_404_NOT_FOUND)


payment_callback_handler = PaidCallback.as_view()







#HII UNAPROCESS WHEN USER PAID
@api_view(['POST'])
def evmalCallback(request):
    if request.method =='POST':
        feedback = {
            'status': ''
        }
        pharmacy_name = ''
        status = request.data.get('ResultType')
        reference = request.data.get('ThirdPartyReference')
        if status == True:
            payment = Payment.objects.filter(reference_no=reference).first()
            if payment is not None: 
                payment.status='PAID'
                payment.save()

                if payment.prescription_id is not None:
                    prescription = PrescriptionDeliveryRequest.objects.filter(id=payment.prescription_id).first()
                    pharmacy = Phamacy.objects.filter(id=prescription.phamacy_id).first()
                    pharmacy_name = pharmacy.name
                    if prescription is not None:   
                        prescription.status = 'processing'
                        prescription.save()
                        feedback['status'] = "Sucess" 
                    else:
                        feedback['status'] = "failed"
                elif payment.zana_id is not None:
                    zana = ZanaDeliveryRequest.objects.filter(id=payment.zana_id).first()
                    if zana is not None:   
                        zana.status = 'waiting for delivery'
                        zana.save()
                        feedback['status'] = "Sucess"
                        boda_name = ''
                        boda_phone = ''
                        boda = Boda.objects.filter(id=zana.boda_id).first()
                        patient = Patient.objects.filter(user_id=zana.requested_by_id).first()
                        if boda is not None:
                            boda_name = boda.first_name + " " + boda.last_name
                            boda_phone = boda.phone_no
                            msg = "AFYA TAP: Malipo ya ZANA toka kwa "+patient.first_name+" "+patient.last_name+" namba "+patient.phone_no+" yamekalimika, Soma oda kisha peleka"
                            send_general_sma(boda.phone_no , msg) 
                                    # ============SEND SMS TO CUSTOMER ==================
                        msg = "AFYA TAP: Thank you for your payment. Rider  "+boda_name +" with Mobile "+boda_phone+" will deliver your ZANA"
                        send_general_sma(patient.phone_no , msg) 
                    else:
                        feedback['status'] = "failed"
                else:
                    appointment = AppointmentBookingRequest.objects.filter(id=payment.appointment_id).first()
                    if appointment is not None: 
                        appointment.status = 'On Progress'
                        appointment.save()
                        feedback['status'] = "Sucess" 
                    else:
                        feedback['status'] = "failed"          
            else:
                feedback['status'] = "failed"
            
            if feedback['status']=="Sucess":
                patient = Patient.objects.filter(id=payment.patient_id).first()
                msg = "Your medicine payment to "+ pharmacy_name +"completed successful."
                send_general_sma(patient.phone_no , sms)
            return JsonResponse(feedback, safe=False)   