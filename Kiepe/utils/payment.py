# HII UNAPROCESS PAYMENTS ILI UTUPE PUSH KWA MTEJA

@api_view(['POST'])
def process_payment(request):
    if request.method == 'POST':
        prescription_id = request.data.get('prescription_id')
        appoinment_id = request.data.get('appoinment_id')
        zana_id = request.data.get('zana_id')
        doctor_id = request.data.get('doctor_id')

        if doctor_id is not None:
            deadline_days = request.data.get('package_size')
            today = datetime.today()
            consultation_deadline = today + timedelta(days=deadline_days)
        if prescription_id is None:
            prescription_id = ''
        if appoinment_id is None:
            appoinment_id = ''
        if zana_id is None:
            zana_id = ''
        selected_payment_method = request.data.get('payment_method')
        payment_for_item = request.data.get('payment_for_item')
        payment_for_item_id = request.data.get('payment_for_item_id')
        user_id = request.data.get('patient_id')
        amount = request.data.get('amount')
        phone_no = request.data.get('phone_no')
        phone_no = format_mobile_phone_number(phone_no)
        product_name = 'AfyaTap Service'
        reference_number = ''
        # //Create reffere numbers ===========
        last_used_reference_number = PaymentReferenceNumber.get_last_no(selected_payment_method)
        
        if(selected_payment_method == '1'):
            reference_number = "AAP" + last_used_reference_number
            # increment and save last number
            PaymentReferenceNumber.increment_last_no('1', last_used_reference_number)
        if(selected_payment_method =='2'):
            reference_number = "AAP" + last_used_reference_number
            # increment and save last number
            PaymentReferenceNumber.increment_last_no('2', last_used_reference_number)
        if(selected_payment_method =='3'):
            reference_number = "AAP" + last_used_reference_number
            # increment and save last number
            PaymentReferenceNumber.increment_last_no('3', last_used_reference_number)

            
        patient= Patient.objects.filter(user_id=user_id).first()
        pay = Payment()
        pay.amount = amount
        if doctor_id is not None:
            pay.doctor_id=doctor_id
            pay.consultation_deadline = consultation_deadline
        pay.reference_no=reference_number
        pay.description = payment_for_item
        pay.patient_id = patient.id
        pay.payment_method_id = selected_payment_method
        pay.service_id = payment_for_item_id
        pay.prescription_id = prescription_id
        pay.appoinment_id = appoinment_id
        pay.zana_id = zana_id
        pay.status = "NOT PAID"
        pay.save()
        

        # user = User.objects.get(pk=user_id)
        user = User.objects.get(pk=user_id)

        if payment_for_item == 'service':
            service1 = Service.objects.get(pk=payment_for_item_id)
            product_name = service1.name + ' Service'
            product_name = string.capwords(product_name)
            service_price1 = ServicePrice.objects.filter(service=service1).last()
            amount = service_price1.price

        print('product name ------------------------------ ')
        print(product_name)

        message = ''

        if selected_payment_method == '1':  # tigopesa
            message = pay_with_tigopesa(phone_no, product_name, amount,reference_number)
        if selected_payment_method == '2':  # mpesa
            message = pay_with_mpesa(phone_no, product_name, amount,reference_number)
        if selected_payment_method == '3':  # Airtel
            message = pay_with_airtelMoney(phone_no, product_name, amount,reference_number)
      
        feedback = {
            'feedback': message,
            'payment_method': selected_payment_method,
            'payment_for_item': payment_for_item,
            'payment_for_item_id': payment_for_item_id,
            'user_id': user_id,
            'amount': amount,
            'phone_no': phone_no
        }

        return JsonResponse(feedback, safe=False)


def pay_with_mpesa(phone_no, product_name, amount,reference_number):
    # has_string = 'mainstream|'.date('d-m-Y')
    today_date = datetime.today().strftime('%d-%m-%Y')
    hash_string = "mainstream|"+today_date
    authentication_key = hashlib.md5(hash_string.encode()).hexdigest()

    call_back_url = "https://afyatap-6z6g9.ondigitalocean.app/api/evmalCallback"
    

    json_data = {
        "api_source": "MAINSTREAM MEDIA",
        "api_to": "Mpesa",
        "amount": amount,
        "product": product_name,
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


def pay_with_tigopesa(phone_no, product_name, amount,reference_number):
 
    today_date = datetime.today().strftime('%d-%m-%Y')
    hash_string = "mainstream|"+today_date
    authentication_key = hashlib.md5(hash_string.encode()).hexdigest()
    call_back_url = "https://afyatap-6z6g9.ondigitalocean.app/api/evmalCallback"
    

    json_data = {
        # "api_source": "MAINSTREAM MEDIA",
        "api_source": "MAINSTREAM MEDIA",
        "api_to": "TigoPesa",
        "amount": amount,
        "product": product_name,
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

    gateway_feedback = payment_request.json()
    # print('FEEDBACK------------- ------> ', gateway_feedback)
    return gateway_feedback

def pay_with_airtelMoney(phone_no, product_name, amount,reference_number):
 
    today_date = datetime.today().strftime('%d-%m-%Y')
    hash_string = "mainstream|"+today_date
    authentication_key = hashlib.md5(hash_string.encode()).hexdigest()
    call_back_url = "https://afyatap-6z6g9.ondigitalocean.app/api/evmalCallback"
    

    json_data = {
        "api_source": "MAINSTREAM MEDIA",
        "api_to": "TigoPesa",
        "amount": amount,
        "product": product_name,
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

    gateway_feedback = payment_request.json()
    # print('FEEDBACK------------- ------> ', gateway_feedback)
    return gateway_feedback


def format_mobile_phone_number(phone_no):
    formatted_phone_no = ''
    tanzania_code = '255'

    if len(phone_no) >= 9:
        phone_no = phone_no.replace(' ', '')
        phone_no = phone_no[-9:]
        formatted_phone_no = tanzania_code + '' + phone_no

    return formatted_phone_no






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