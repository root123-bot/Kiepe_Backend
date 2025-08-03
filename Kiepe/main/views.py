from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from Kiepe.customer.serializers import *
from Kiepe.kibanda.serializers import *
from Kiepe.utils.index import sendNotification
from .models import *
from .serializers import *
from Kiepe.kibanda.models import *
import string, random
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
import datetime
from Kiepe.utils.index import sendOTP
from django.db.models import Q
from Kiepe.administrator.serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class UserDetalsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        
        user_id = request.data.get('user_id')

        try:
            user = get_user_model().objects.get(id=int(user_id))
            if hasattr(user, 'kibanda'):
                kibanda = user.kibanda
                serialize = KibandaProfileSerializer(kibanda)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
            if hasattr(user, 'customer'):
                customer = user.customer
                serialize = CustomerProfileSerializer(customer)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
            return Response({"details": "Unrecognized user group"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
user_details = UserDetalsAPIView.as_view()

class DeleteUserAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        try:
            user = get_user_model().objects.get(id=int(user_id))
            user.delete()
            return Response({"details": "User deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

delete_user = DeleteUserAPIView.as_view()

class SaveDeviceNotificationToken(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        print('user id ', user_id, ' token ', token)
        try:
            user = get_user_model().objects.get(id=int(user_id))
            notificationToken = DeviceNotificationToken.objects.filter(user=user)

            if notificationToken.exists():
                notificationToken = notificationToken.first()
                notificationToken.deviceNotificationToken = token
                notificationToken.save()
                return Response({"details": "Token updated successfully"}, status=status.HTTP_200_OK)

            else:
                notificationToken = DeviceNotificationToken.objects.create(user=user, deviceNotificationToken=token)
                notificationToken.save()
                return Response({"details": "Token added successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
save_device_notification_token = SaveDeviceNotificationToken.as_view()

# any user can order so lets use "user" model instead of biased "customer" model
class FetchCustomerOrders(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        print("Posted user id ", user_id)
        try:
            user = get_user_model().objects.get(id=int(user_id))
            # we look for the "ordered by model - CustomerProfile" then "id" field
            orders = Order.objects.filter(ordered_by__id = user.id, mark_as_deleted = False)

            serializer = OrderSerializer(reversed(orders), many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
customer_orders = FetchCustomerOrders.as_view()

class CreateOrder(APIView):
    def post(self, request):
        
        user_id = request.data.get('user_id')
        order_metadata = request.data.get('order_metadata')
        simu_ya_mteja = request.data.get('phone')
        print('data sent ', user_id, order_metadata, simu_ya_mteja)
        try:
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = KibandaProfile.objects.get(id=int(order_metadata['kibandaId']))
            existingOrderIds = Order.objects.values_list('order_id', flat=True)
            order_ids = list(existingOrderIds)
            orderId = ""
            flag = True
            while flag:
                orderId = "".join(random.choices(string.ascii_uppercase + string.digits, k=25))
                if orderId not in order_ids:
                    flag = False


            
            order = Order.objects.create(order_id = orderId, ordered_by=user, assigned_to=kibanda, order_status='pending', total = 0, namba_ya_mteja = simu_ya_mteja)
            order.save()
            for item in order_metadata['metadata']:
                oitem = OrderItem.objects.create(
                    order=order,
                    menu = Menu.objects.get(id=item['id']),
                    quantity = item['quantity'],
                    subtotal = item['totalPrice']
                )
                oitem.save()
                subtotal = oitem.subtotal if oitem.subtotal != None else 0
                order.total = int(order.total) + int(subtotal)

            order.save()
            # send notification to kibanda
            token = DeviceNotificationToken.objects.filter(user=kibanda.user)
            if token.exists():
                token = token.first().deviceNotificationToken
                sendNotification("New Order", "You have a new order", token)
            else:
                print("No token for kibanda")

            # do also need to send notification to customer
            token = DeviceNotificationToken.objects.filter(user=user)
            if token.exists():
                token = token.first().deviceNotificationToken
                sendNotification("Order Placed", "Your order has been placed", token)
            else:
                print("No token for customer")
                

            # lets also create the notifications for both kibanda and customer
            notification = Notification.objects.create(
                target="customer",
                sent_to = user,
                heading = "Order Placed Successful",
                is_associted_with_order=True,
                body = "You have successfully placed an order",
                order = order
            )

            notification.save()

            # have the notification for kibanda..
            notification2 = Notification.objects.create(
                target="kibanda",
                sent_to = kibanda.user,
                is_associted_with_order=True,
                heading = "New Order",
                body = "You received a new order, please check it out",
                order = order
            )



            notification2.save()
                
            message = f"Kuna order mpya imeingia, namba ya mteja ni {user.phone_number}, kwa maelezo zaidi ingia Kihepe app"

            sendOTP(kibanda.user.phone_number, message)

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e: 
            print('this is our error ', str(e))
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
create_order = CreateOrder.as_view()

class CustomerCancelOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def patch(self, request, *args, **kwargs):
        user = request.user
        order_id = kwargs.get('order_id')

        try:
            order = Order.objects.get(id=int(order_id))

            order.order_status = "cancelled"
            
            cancelled_order = CancelledOrdersByCustomer.objects.create(
                order = order,
                cancelled_by = user,
            )

            order.save()
            cancelled_order.save()
            ordered_to = order.assigned_to
            msg_receiver = ordered_to.user
            token = DeviceNotificationToken.objects.filter(user = msg_receiver)
            if token.exists():
                token = token.first().deviceNotificationToken
                sendNotification("Order cancelled", "Customer have cancelled the order made", token)
            else:
                print("no token for kibanda")

            # let's create notification... customer notifications
            notification1 = Notification.objects.create(
                target = "customer",
                heading = "Order cancelled",
                body = "Please check the order details for more information.".format(order.id),
                is_associted_with_order = True,
                order = order,
                sent_to = msg_receiver,
            )

            # kibanda notifications
            notification2= Notification.objects.create(
                target = "kibanda",
                heading = "Order cancelled",
                body = "The order have this id {} have been cancelled by customer. Please check the order details for more information. ".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = order.assigned_to.user,
            )

            notification1.save()
            notification2.save()
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print('error ', str(err))
            return Response({"details": str(err)}, status=status.HTTP_400_BAD_REQUEST)

customer_cancel_order = CustomerCancelOrderAPIView.as_view()

# in my case nimeweka mtu aki-delete order ambayo ni pending basi ame-cancel 
# order... hivyo...
# i think if also the kibanda delete the "Pending" order then he cancelled the 
# order so customer should receive the notification...
# BUT I THINK THIS CAPABILITY OF DELETE THE PEDING ORDER SHOULD NOT BE HERE SINCE 
# IT HAVE THE HARSH CONSEQUENCES, SO SOMEONE SHOULD FIRST "REJECT" OR CANCEL THE 
# ORDER THEN DELETE IT IF HE WANT..
class MarkDeletedOrderAPIView(APIView):
    def post(self, request):
        order_id = request.data.get("order_id")
        
        try:
            
            order = Order.objects.get(id=int(order_id))
            order.mark_as_deleted = True
            order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print('error ', str(err))
            return Response({"details": str(err)}, status=status.HTTP_400_BAD_REQUEST)

mark_as_deleted = MarkDeletedOrderAPIView.as_view()


class FetchKibandaOrders(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        
        try:
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            # we look for the "ordered by model - CustomerProfile" then "id" field
            # kibanda can look for orders deleted by customer and we don't care for 
            # the orders deleted by kibanda itself
            orders = Order.objects.filter(assigned_to__id = kibanda.id, kibanda_mark_order_deleted = False)

            serializer = OrderSerializer(reversed(orders), many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
kibanda_orders = FetchKibandaOrders.as_view()

class MarkOrderRejected(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        order_id = request.data.get("order_id")

        try:
            user = get_user_model().objects.get(id=int(user_id))
            order = Order.objects.get(id=int(order_id))

            # we call "Rejected" if kibanda cancel the order
            order.order_status = "rejected"

            cancelled_order = CancelledOrdersByKibanda.objects.create(
                order = order,
                cancelled_by = user.kibanda,
            )

            

            ordered_by = order.ordered_by
            assigned_to = order.assigned_to

            customer = user
            kibanda = assigned_to.user

            # KUMBUKA HIZI MESSAGES ZIMEKUWA HARD-CODED ILI KUJUA-REDIRECT SO IN OUR FRONTEND.. SO DON'T CHANGE THEM
            token = DeviceNotificationToken.objects.filter(user = customer)
            if token.exists():
                token  = token.first().deviceNotificationToken
                sendNotification("Order Rejected", "Your order has been rejected", token)
            else:
                print("no token for customer")

            token = DeviceNotificationToken.objects.filter(user = kibanda)
            if token.exists():
                token  = token.first().deviceNotificationToken
                sendNotification("Sucessful Rejected", "You have successful rejected the order", token)
            else:
                print("no token for kibanda")

            # let's create notification... customer notifications
            notification1 = Notification.objects.create(
                target = "customer",
                heading = "Order rejected",
                body = "Your order of this id {} has been rejected by the kibanda,please check the order details for more information.".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = customer,
            )

            # kibanda notifications
            notification2= Notification.objects.create(
                target = "kibanda",
                heading = "Order rejected",
                body = "You have successful rejected the order of this id {}. Please check the order details for more information.".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = kibanda,
            )

            notification1.save()
            notification2.save()
            
            order.save()
            cancelled_order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


mark_order_rejected = MarkOrderRejected.as_view()


class KibandaMarkOrderDeleted(APIView):
    def post(self, request):
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=int(order_id))

            order.kibanda_mark_order_deleted = True

            order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

kibanda_mark_order_deleted = KibandaMarkOrderDeleted.as_view()


class FetchNotificationOfUser(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        user = get_user_model().objects.get(id=int(user_id))
        notifications = Notification.objects.filter(sent_to=user, is_deleted=False)
        notifications = reversed(notifications)
        serialize = NotificationSerializer(notifications, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)

fetch_notification_of_user = FetchNotificationOfUser.as_view()

class MyNotifications(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user

        limit = request.GET.get('limit')
        status = request.GET.get('status')
        page = request.GET.get('page')

        take = limit if limit else 10
        pageParam = page if page else 1
        skip = (int(pageParam) - 1) * int(take)

        qs = Notification.objects.filter(sent_to=user, is_deleted=False)

        total_notifications = qs.count()

        notifications = qs[int(skip):int(int(skip) + int(take))]

        serializer = NotificationSerializer(notifications, many=True)

        return Response({
            'notifications': serializer.data,
            'total': total_notifications,
            'page': page,
            'take': take
        })

user_notifications = MyNotifications.as_view()

class MarkNotificationDeleted(APIView):
    def post(self, request):
        notification_id = request.data.get("notification_id")
        try:
            notification = Notification.objects.get(id=int(notification_id))
            notification.is_deleted = True
            notification.is_read = True
            notification.save()
            serialize = NotificationSerializer(notification)
            return Response(serialize.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
mark_notification_deleted = MarkNotificationDeleted.as_view()

class ClearAllNotificationOfUser(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        try:
            user = get_user_model().objects.get(id=int(user_id))
            notifications = Notification.objects.filter(sent_to=user, is_deleted=False)
            for notification in notifications:
                notification.is_deleted = True
                notification.is_read = True
                notification.save()
            return Response({"details": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
clear_all_notification_of_user = ClearAllNotificationOfUser.as_view()


class MarkOrderAccepted(APIView):
    def post(self, request):
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=int(order_id))

            # we call "Rejected" if kibanda cancel the order
            order.order_status = "accepted"

            customer = order.ordered_by
            kibanda_user = order.assigned_to.user

            token = DeviceNotificationToken.objects.filter(user = customer)
            # we hardcoded the notification message here so we should not change it coz it used in our app for redirect for example you notice the "view you" instead of "view your" but leave it alone
            if token.exists():
                token  = token.first().deviceNotificationToken
                sendNotification("Order Accepted", "Your order has been accepted, for more information view you order", token)
            else:
                print("no token for customer")
            
            token = DeviceNotificationToken.objects.filter(user = kibanda_user)
            if token.exists():
                token  = token.first().deviceNotificationToken
                sendNotification("Order Accepted", "Order marked accepted succesful, you should communicate with your customer to discuss further processing", token)
            else:
                print("no token for kibanda")
            
            # lets create notification for customer
            notification1 = Notification.objects.create(
                target = "customer",
                heading = "Order Accepted",
                body = "Your order of this id {} has been accepted, if not delivered you should communicate with restaurant for delivery process".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = customer,
            )

            # lets create notification for kibanda
            notification2 = Notification.objects.create(
                target = "kibanda",
                heading = "You have successful accepted the order",
                body = "Order of id {} marked accepted succesful, you should communicate with your customer to discuss for further processing".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = kibanda_user,
            )

            order.save()
            notification1.save()
            notification2.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

mark_order_accepted = MarkOrderAccepted.as_view()

# we only give ability to kibanda to mark order completed
class MarkOrderCompleted(APIView):
    def post(self, request):
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=int(order_id))

            # we call "Rejected" if kibanda cancel the order
            order.order_status = "completed"

            customer = order.ordered_by
            kibanda_user = order.assigned_to.user

            token = DeviceNotificationToken.objects.filter(user = customer)
            if token.exists():
                token  = token.first().deviceNotificationToken
                sendNotification("Order Completed", "Your order has been completed, if not delivered you should communicate with restaurant for delivery process", token)
            else:
                print("no token for customer")
            
            token = DeviceNotificationToken.objects.filter(user = kibanda_user)
            if token.exists():
                token  = token.first().deviceNotificationToken
                sendNotification("Order Completed", "Order marked completed succesful, you should communicate with your customer to discuss the delivery process", token)
            else:
                print("no token for kibanda")
            
            # lets create notification for customer
            notification1 = Notification.objects.create(
                target = "customer",
                heading = "Order Completed",
                body = "Your order of this id {} has been completed, if not delivered you should communicate with restaurant for delivery process".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = customer,
            )

            # lets create notification for kibanda
            notification2 = Notification.objects.create(
                target = "kibanda",
                heading = "You have successful completed the order",
                body = "Order of id {} marked completed succesful, you should communicate with your customer to discuss the delivery process".format(order.order_id),
                is_associted_with_order = True,
                order = order,
                sent_to = kibanda_user,
            )

            order.save()
            notification1.save()
            notification2.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("error ", e)
            return Response({ "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


mark_order_completed = MarkOrderCompleted.as_view()



class ChangePasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['user_id']
            user = get_user_model().objects.get(id=int(user_id))
            old_password = request.data['old_password']
            new_password = request.data['new_password']
            confirm_password = request.data['confirm_password']

            if new_password != confirm_password:
                return Response(
                    {"details": "New password and confirm password does not match"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not user.check_password(old_password):
                return Response(
                    {"details": "Old password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"success": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as err:
            print("Error ", err)
            return Response(
                {"details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
change_password = ChangePasswordAPIView.as_view()


class AddKibandaRating(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user_id', None)
            kibanda_id = request.data.get('kibanda_id')
            rating = request.data.get('rating', None)
            comment = request.data.get('comment', None)
            print(" this is data sent ", user_id, kibanda_id, rating, comment)
            # here "rating" can be none in case mtu anasubmit bila kutoa rating
            # here "comment" can be none in case mtu anasubmit bila kutoa comment
            # both of them can't be none at the same time but can have value both at the same time
            # remember customer can be anyone either kibanda or customer
            kibandaRating = KibandaRating.objects.create(
                rated_by = get_user_model().objects.get(id=int(user_id)) if user_id else None,
                rating = rating if rating else None,
                rating_comment = comment if comment else None,
                kibanda = KibandaProfile.objects.get(id=int(kibanda_id)),
            )

            kibandaRating.save()

            return Response(
                {"success": "Rating submitted successfully"},
                status=status.HTTP_200_OK
            )
        
        except Exception as err:
            print("Error ", err)
            return Response(
                {"details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

add_kibanda_rating = AddKibandaRating.as_view()

class FetchKibandaReview(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id', None)
        print('this is entry point ', user_id)
        try:
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda

            kibandaRatings = KibandaRating.objects.filter(kibanda=kibanda, rating_comment__isnull=False, rating__isnull=False)
            print("kibanda ratings ", kibandaRatings)
            serializer = KibandaRatingSerializer(kibandaRatings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as err:
            print("Error ", err)
            return Response(
                {"details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

kibanda_reviews = FetchKibandaReview.as_view()


class KibandaRatings(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id', None)
        print('this is entry point ', user_id)
        try:
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda

            kibandaRatings = KibandaRating.objects.filter(kibanda=kibanda, rating__isnull=False)
            print("kibanda ratings ", kibandaRatings)
            serializer = KibandaRatingSerializer(kibandaRatings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as err:
            print("Error ", err)
            return Response(
                {"details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

kibanda_ratings = FetchKibandaReview.as_view()

class MarkNotificationAsRead(APIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('notification_id')

        try: 
            notification = Notification.objects.get(id=int(id))

            notification.is_read  = True
            notification.save()
            return Response({
                "message": "Successful",
            }, status=status.HTTP_200_OK)
        
        except Exception as err:
            print("Error ", err)
            return Response(
                {"details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
mark_notification_as_read = MarkNotificationAsRead.as_view()

class UpdateUserProfilePicture(APIView):
    def post(self, request, *args, **kwargs):
        photo = request.data.get('photo')
        user_id = request.data.get('user_id')
        print('IM GET CALLED BY LUPE FIASCO', photo, user_id)
        try: 
            user = get_user_model().objects.get(id=int(user_id))

            if hasattr(user, "customer"):
                # we're dealing with customer...
                if user.customer:
                    customer = user.customer
                    customer.image = photo
                    customer.save()
                    return Response({
                        "message": "Successful",
                    }, status=status.HTTP_200_OK)
                
                else:
                    print("Print who are you every user has given profile initially")
            elif hasattr(user, "kibanda"):
                if user.kibanda:
                    kibanda = user.kibanda
                    kibanda.image = photo
                    kibanda.save()
                    return Response({
                        "message": "Successful",
                    }, status=status.HTTP_200_OK)

                else:
                    print("Print who are you every user has given profile initially")

            else:
                return Response({
                    "message": "User is neither customer nor kibanda",
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as err:
            print("Error ", err)
            return Response(
                {"details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )
                
update_user_profile_picture = UpdateUserProfilePicture.as_view()

class ValidateRestaurants(View):
    template_name = "validateVibanda.html"
    def get(self, request):
        restaurants = reversed(KibandaProfile.objects.filter(profile_is_completed = True))
        print('restaurants ', restaurants)
        return render(request, self.template_name, { "vibanda": restaurants })

validate_restaurants = ValidateRestaurants.as_view()


class RestaurantsInfo(View):
    template_name = "kibandaInfo.html"
    def get(self, request, *args, **kwargs):
        kibanda_id = kwargs.get('kid')
        base_url = "http://kihepe.mainfm.co.tz"
        kibanda = KibandaProfile.objects.get(id=int(kibanda_id))
        return render(request, self.template_name, { "kibanda": kibanda, "profile": kibanda.image.url, "cover": kibanda.cover_photo.url, "BASE_URL": base_url })

restaurants_info = RestaurantsInfo.as_view()

class ReverseUserStatus(View):
    # template_name = "kibandaInfo.html"
    def get(self, request, *args, **kwargs):
        kibanda_id = kwargs.get('kid')
        print("kibanda id ", kibanda_id)
        kibanda = KibandaProfile.objects.get(id=int(kibanda_id))

        if kibanda.is_active:
            kibanda.is_active = False

            # send push notification to that user
            user = kibanda.user
            token = DeviceNotificationToken.objects.filter(user=user)
            print('Token ', token)
            if token.exists():
                token = token.first().deviceNotificationToken
                print("token ", token)
                sendNotification(
                    "Account Deactivated",
                    "Your account has been deactivated by the admin. Please contact us for more information",
                    token,
                )
                

            else:
                print("No device token for this us")

            notification = Notification.objects.create(
                heading="Account Deactivated",
                body="Your account has been deactivated by the admin. Please contact us for more information",
                target="kibanda",
                is_associted_with_order = False,
                sent_to = kibanda.user,
            )

            kibanda.save()
            notification.save()

            return HttpResponseRedirect(reverse("validateVibanda"))
        else:
            kibanda.is_active = True
            kibanda.save()

            # send push notification to that user
            user = kibanda.user
            token = DeviceNotificationToken.objects.filter(user=user)
            print("Token ", token)
            if token.exists():
                token = token.first().deviceNotificationToken
                print("token ", token) 
                sendNotification(
                    "Account Activated",
                    "Your account has been activated by the admin. Please visit your profile for more information",
                    token,
                )
                

            else:
                print("No device token for this us")

            # if accounts is activated we should also start the free tier of the user..
            record = KibandaPayments.objects.filter(kibanda=kibanda)
            if record.exists():
                record = record.first()
                record.amount = 0
                record.start_date = datetime.datetime.now()
                record.expire_date = datetime.datetime.now() + datetime.timedelta(days=30)

                record.save()

            else:
                if kibanda.status == "FREE":
                    record = KibandaPayments.objects.create(
                        kibanda=kibanda,
                        amount=0,
                        start_date=datetime.datetime.now(),
                        expire_date=datetime.datetime.now() + datetime.timedelta(days=30)
                    )
                    record.save()

                    # send push notification to that user
                    token = DeviceNotificationToken.objects.filter(user=user)
                    print("Token ", token)
                    if token.exists():
                        token = token.first().deviceNotificationToken
                        print("token ", token) 
                        sendNotification(
                            "Free Tier Activated",
                            "Your account 1 month free tier has been activated after that tier expires you will be charged",
                            token,
                        )

                    notification = Notification.objects.create(
                        heading="Free Tier Activated",
                        body="Your account 1 month free tier has been activated after that tier expires you will be charged",
                        target="kibanda",
                        is_associted_with_order = False,
                        sent_to = kibanda.user,
                    )

                    notification.save()

                    kibanda.status = "NOT-FREE"
                    kibanda.save()

            notification = Notification.objects.create(
                heading="Account Activated",
                body="Your account has been activated by the admin. Please visit your profile for more information",
                target="kibanda",
                is_associted_with_order = False,
                sent_to = kibanda.user,
            )

            notification.save()
            
        return HttpResponseRedirect(reverse("validateVibanda"))

reverse_user_status = ReverseUserStatus.as_view()

class GetSearchSuggestions(APIView):
    def get(self, request):
        query = self.request.GET.get('query') # the query can be restaurant food or place
        # save searched query
        
        # retrieve suggestions, 
        # we only care about eithe rrestaurants or food
        qs = KibandaProfile.objects.filter(
            Q(brand_name__icontains=query)
        )[:10]

        vibanda = KibandaSearchSuggestionSerializer(qs, many=True)

        vibanda = list(vibanda.data)
        misosi = Menu.objects.filter(type="menu")
        qs2 = misosi.filter(
            Q(name__icontains=query) 
        )[:5]


        menus = MenuSearchSuggestionSerializer(qs2, many=True)

        menus = list(menus.data)

        vibanda.extend(menus)

        suggestions = vibanda
        random.shuffle(suggestions)

        return Response({
            "suggestions": suggestions
        })

search_suggestions = GetSearchSuggestions.as_view()

def menu_restaurant_infinite_filter(request):
    limit = request.GET.get('limit') # this always remain 10, what change is page
    page = request.GET.get('page')
    id = request.GET.get('menuId')

    take = limit if limit else 10
    pageParam = page if page else 1
    skip = (int(pageParam) - 1) * int(take)

    msosi = Menu.objects.get(id=id)

    # shortly the "menu" of menuyaleo is "MenuItem" which then linked to actual "menu" thats why
    # we have "__menu__menu", as because the user search for given menu on restaurant its crital
    # to consider only if that menus is currently available on the restaurant that's why i took 
    # the "menuyaleo", after fetched the one which have the menuyaleo with that searched food from 
    # it i serializer them and remember in serializing them we're supplied with all available menuitem
    # of that restaurant
    qs = KibandaProfile.objects.filter(
        menuyaleo__menu__menu = msosi,
        is_active = True
    )

    data = SearchedMenuRestaurantSerializer(qs, many=True)

    data = list(data.data)

    list_dict = [] 

    for item in data:
        dict_item = dict(item)
        list_dict.append(dict_item)
    
    sorted_data = sorted(list_dict, key=lambda x: (x['average_ratings'] if x['average_ratings'] is not None else float('-inf')), reverse=True)

    total = len(sorted_data)

    data = sorted_data[int(skip):int(int(skip) + int(take))]

    return {"data": data, "total": total, "take": take, "page": pageParam}


class GetSearchedFoodRestaurants(APIView):
    def get(self, request):
        output = menu_restaurant_infinite_filter(self.request)

        data = output.get('data')
        total = output.get('total')
        take = output.get('take')
        page = output.get('page')
        return Response({
            "data": data,
            "total": total,
            "take": take,
            "page": page,
        })

searched_menu_restaurants = GetSearchedFoodRestaurants.as_view()


class GetSystemSettings(APIView):
    def get(self, request):
        return Response({
            "engineer_contact": "+255623317196",
        }, status=status.HTTP_200_OK)

get_settings = GetSystemSettings.as_view()

class MyCustomerOrdersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user

        limit = request.GET.get('limit')
        status = request.GET.get('status')
        page = request.GET.get('page')

        take = limit if limit else 10
        pageParam = page if page else 1
        skip = (int(pageParam) - 1) * int(take)

        qs = Order.objects.filter(ordered_by__id = user.id, mark_as_deleted = False)

        valid_statuses = ['accepted', 'pending', 'cancelled', 'completed', 'rejected']

        if status and status in valid_statuses:
            if status == "cancelled":
                cancelled_order_ids = CancelledOrdersByCustomer.objects.filter(cancelled_by__id = user.id, order__mark_as_deleted = False).values_list('id', flat=True)
                qs = Order.objects.filter(id__in=cancelled_order_ids, order_status = "cancelled", mark_as_deleted = False)
            else:
                qs = qs.filter(order_status=status)

        total_orders = qs.count()

        orders = qs[int(skip):int(int(skip) + int(take))]

        serializer = OrderSerializer(reversed(orders), many=True)

        return Response({
            'orders': serializer.data,
            'total': total_orders,
            'page': page,
            'take': take
        })

customer_my_orders = MyCustomerOrdersView.as_view()


class MyRestaurantOrdersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user

        kibanda = user.kibanda

        limit = request.GET.get('limit')
        status = request.GET.get('status')
        page = request.GET.get('page')

        take = limit if limit else 10
        pageParam = page if page else 1
        skip = (int(pageParam) - 1) * int(take)

        qs = Order.objects.filter(assigned_to__id = kibanda.id, kibanda_mark_order_deleted = False)

        valid_statuses = ['accepted', 'pending', 'cancelled', 'completed', 'rejected']

        if status and status in valid_statuses:
            qs = qs.filter(order_status=status)

        total_orders = qs.count()

        orders = qs[int(skip):int(int(skip) + int(take))]

        serializer = OrderSerializer(reversed(orders), many=True)

        return Response({
            'orders': serializer.data,
            'total': total_orders,
            'page': page,
            'take': take
        })

restaurant_my_orders = MyRestaurantOrdersView.as_view()


class CustomerMarkOrderDeleteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        order_id = kwargs.get('order_id')

        try:
            order = Order.objects.get(id=int(order_id))
            order.mark_as_deleted = True

            order.save()
            return Response({ "details": "Order deleted successfully "}, status=status.HTTP_200_OK)
        except Exception as err:
            print('error ', str(err))
            return Response({"details": str(err)}, status=status.HTTP_400_BAD_REQUEST)


customer_mark_order_deleted = CustomerMarkOrderDeleteAPIView.as_view()