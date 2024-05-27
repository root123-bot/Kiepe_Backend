from django.db import models
from Kiepe.kibanda.models import *
from Kiepe.customer.models import *
from Kiepe.administrator.models import *
from django.contrib.auth import get_user_model

# Create your models here.
'''
    Tulisema kibanda pia anaweza aka-act as mteja akaagiza chipsi, so what u did here is wrong
    we track Customer profile in ordered_by instead of the "User" since the user can be of both 
    the "Kibanda" or "Customer".. assigned_to ndo lazima iwe "KibandaProfile"
'''

ADS_CATEGORIES = (
    ("RATING", "RATING"), # this is big ad that will be showing to tap somewhere to rate sth with image check in screenshots of your phone, this does not need to redirect user to any screen
    ("ARTICLE", "ARTICLE"), # this is article that for now will show image and title and shorted description and then user can tap to read more, the user can like the article and comment on it
    ("ARTICLE VOTING", "ARTICLE VOTING"), # This is article with title and simple few lines of description and the image in this article the user can vote for something, i called it article since it will have post when user click go to another screen
)

ADS_HOME_TAB = (
    ("All", "All"), # this will show ads in "all" tab of home screen in restaurant list
    ("Nearby", "Nearby"), # this will show ads in "nearby" tab of home screen in restaurant list
    ("Opened", "Opened"), # this will show ads in "popular" tab of home screen in restaurant list
    ("Rating", "Rating"), # this will show ads in "rating" tab of home screen in restaurant list
)

class Order(models.Model):
    order_id = models.CharField(max_length=255, blank=True, null=True)
    order_status = models.CharField(max_length=255) # pending, accepted, rejected, cancelled, completed
    order_date = models.DateTimeField(auto_now_add=True)
    order_updated = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(KibandaProfile, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    namba_ya_mteja = models.CharField(max_length=255, blank=True, null=True)
    mark_as_deleted = models.BooleanField(default=False)
    kibanda_mark_order_deleted = models.BooleanField(default=False)

    @property
    def get_assigned_to(self):
        return {
            "id": self.assigned_to.id,
            "user_id": self.assigned_to.user.id,
            "cover": self.assigned_to.cover_photo.url,
            "brand": self.assigned_to.brand_name,
            "phone": self.assigned_to.phone_number
        }
    
    # kama hii field inakataa just stick to look for "order_status" since it serve the same thing
    @property
    def is_order_cancelled(self):
        if self.cancelledorder:
            return True
        return False
    
    @property
    def get_ordered_by(self):
        return {
            "id": self.ordered_by.customer.id if hasattr(self.ordered_by, "customer") else self.ordered_by.kibanda.id,
            "user_id": self.ordered_by.id,
            "phone": self.ordered_by.phone_number
        }
    
    @property
    def get_order_items(self):
        items = []
        for item in self.order_items.all():
            items.append({
                "id": item.id,
                "menu_id": item.menu.id,
                "menu_name": item.menu.name,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
            })

        return items
    
    # @property
    # def get_order_items(self):
    #     # this is how to get all order items for a specific order, so you can put the serializer here and return the data
    #     # its like saying >>> serializer = OrderItemSerializer(self.order_items, many=True)
    #     # then return the data >>> return serializer.data
    #     return OrderItemSerializer(self.order_items, many=True).data

# all notification i sent is from "Kiepe App"/System as a sender
class Notification(models.Model):
    target = models.CharField(max_length=255) # either to customer, kibanda
    heading = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_associted_with_order = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    sent_to = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="notifications")


    @property
    def get_order(self):
        order = None
        if self.order:
            return {
                "id": self.order.id,
                "order_id": self.order.order_id,
                "order_status": self.order.order_status,
                "order_date": self.order.order_date,
                "order_updated": self.order.order_updated,
                "assigned_to": self.order.assigned_to.id,
                "ordered_by": self.order.ordered_by.id,
                "total": self.order.total,
            }
        return order
    
    @property
    def get_sent_to(self):
        return {
            "id": self.sent_to.id,
            "user_id": self.sent_to.id,
            "phone": self.sent_to.phone_number
        }
            

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=255, default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_order_id(self):
        return self.order.id
    

# kuna order anaweza aka-cancel customer au kibanda.. ko hii nimeona ni muhimu ili kuweza ku-send notification kwa kibanda kuwa customer
# ca-cancel order and also kwa customer kuwa kibanda ka-cancel order yake.. nimeona ni vizuri hizi model zote zikae hapa...
# coz hapa ndo kuna model ya order ... order anaweza aka-cancel custumer but tulishasema kuwa customer anaweza akawa
# kibanda au customer so lets here in CAncelOrdersByCustomer in cancelled_by use the get_user_model()
class CancelledOrdersByCustomer(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="cancelledorder")
    cancelled_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now_add=True)
    cancelled_reason = models.TextField(blank=True, null=True)
    cancelled_updated = models.DateTimeField(auto_now=True)

# ni orders anazo-reject nimeziita cancelledordrers
class CancelledOrdersByKibanda(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="rejectedorder")
    cancelled_by = models.ForeignKey(KibandaProfile, on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now_add=True)
    cancelled_reason = models.TextField(blank=True, null=True)
    cancelled_updated = models.DateTimeField(auto_now=True)

# you can rate also leave the rating comment, rated by customer, but rememmber customer can be anyone
# so use the get_user_model() to get the user
class KibandaRating(models.Model):
    rated_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    rating = models.IntegerField(null=True, blank=True)
    rated_at = models.DateTimeField(auto_now_add=True)
    rated_updated = models.DateTimeField(auto_now=True)
    rating_comment = models.TextField(blank=True, null=True)
    kibanda = models.ForeignKey(KibandaProfile, blank=True, null=True, on_delete=models.CASCADE, related_name="kibandaratings")
    # hichi "kibanda" lazima mtu apost 

class CustomerRating(models.Model):
    rated_by = models.ForeignKey(KibandaProfile, on_delete=models.CASCADE)
    rating = models.IntegerField()
    rated_at = models.DateTimeField(auto_now_add=True)
    rated_updated = models.DateTimeField(auto_now=True)
    rating_comment = models.TextField(blank=True, null=True)
    customer = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, related_name="customerratings")
    # hichi "customer" lazima mtu apost 



# all devices login in our system will be stored here, we will use this model to authenticate devices
# if the device is in this model then it is authenticated to use our system through the pin provided
# if the device is not here then allow the user to enter his number send the otp and then allow him 
# to set the pin and then store the device in this model. If he forgets the pin then he can reset the pin
# by entering the number and then the otp will be sent to him and then he will be allowed to set the pin again
class DeviceAuthModel(models.Model):
    modelId = models.CharField(max_length=255)
    pin = models.CharField(max_length=255)


class DeviceNotificationToken(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="notificationToken")
    deviceNotificationToken = models.CharField(max_length=255)

# when a kibanda create account/verified account we need to create the payment records for him 
# and this should be created "automatically" like we did with Profile, so whenever the kibanda 
# create account we should also create the payment record(one) and you know what every kibanda
# should have one record that's onetoone relationship and should be unique,  this "free" payment 
# should be activated a time admin verify the profile of the kibanda, and we said its one month 
# free just remember this JUST REMEMBER THIS AND YOU KNOW WHAT WE SHOULD TAKE THE TIME FIELD 
# WHICH ADDED MANUALLY BE US, this should be overriden everytime user update his payment record
class KibandaPayments(models.Model):
    kibanda = models.OneToOneField(KibandaProfile, on_delete=models.CASCADE, related_name="paymentrecord", unique=True)
    payed_at = models.DateTimeField(blank=True, null=True)
    amount = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    expire_date = models.DateTimeField(blank=True, null=True)
    isExpired = models.BooleanField(default=False)
    # by default we have "status" in kibanda which can be "FREE" which we can change to "NON-FREE" to tell
    # django that user is no longer in 1month free tier

    @property
    def get_kibanda(self):
        return {
            "id": self.kibanda.id
        }


# this will be created first time user select the payment method to initiate the payment so before initiating just save the 
# phone number put by user in relation to thsi reference_number
class PaymentReferenceNumbers(models.Model):
    phone = models.CharField(max_length=255, blank=True, null=True)
    reference_number = models.CharField(max_length=255, blank=True, null=True)

# this can be manytomanyjust used to keep records all all payment made
class TransactionRecords(models.Model):
    payment_method = models.CharField(max_length=255, blank=True, null=True)
    reference_number = models.OneToOneField(PaymentReferenceNumbers, on_delete=models.CASCADE)  # this we generate ourself and we should send to tigopesa when we call their api, they execute the user transaction and then give back our response and we need to check if it existed in our db for us to verify if the transaction was generated by us
    external_transaction_number = models.CharField(max_length=255, blank=True, null=True) # this is from tigopesa, come from them 
    payed_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="whopaid")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default="NOT PAID") # this can be pending, success, failed, cancelled, expired, refund

# this can be created when user open the app for the first time and then we can use this to track the user who is not logged in
class SessionIds(models.Model):
    session_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# user can vote ad either by using the session_id or by using the user_id
class AdVotes(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    ad = models.ForeignKey("Ads", on_delete=models.CASCADE)
    vote = models.BooleanField(default=False)
    voted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey(SessionIds, blank=True, null=True) # we'll generate this session_id here on the server instead on the client side like on zeromoja app


class AdRating(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    ad = models.ForeignKey("Ads", on_delete=models.CASCADE)
    rating = models.IntegerField()
    rated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey(SessionIds, blank=True, null=True) # we'll generate this session_id here on the server instead on the client side like on zeromoja app

class AdComments(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    ad = models.ForeignKey("Ads", on_delete=models.CASCADE)
    comment = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey(SessionIds, blank=True, null=True) # we'll generate this session_id here on the server instead on the client side like on zeromoja app

class CommentReplies(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(AdComments, on_delete=models.CASCADE)
    reply = models.TextField()
    replied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey(SessionIds, blank=True, null=True) # we'll generate this session_id here on the server instead on the client side like on zeromoja app

class CommentLikes(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(AdComments, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey(SessionIds, blank=True, null=True) # we'll generate this session_id here on the server instead on the client side like on zeromoja app

# for now lets not focus on reply replies, we can add them later if we need them
class ReplyLikes(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    reply = models.ForeignKey(CommentReplies, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey(SessionIds, blank=True, null=True) # we'll generate this session_id here on the server instead on the client side like on zeromoja app    

class Ads(models.Model):
    category = models.CharField(max_length=255, choices=ADS_CATEGORIES)
    image = models.ImageField(upload_to="ads_images/", blank=True, null=True)
    screen = models.CharField(max_length=255, choices=ADS_HOME_TAB)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(blank=True, null=True) # add can live for a week or month
    end_date = models.DateTimeField(blank=True, null=True)
    ad_title = models.CharField(max_length=255, blank=True, null=True)
    ad_description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False) # some ads like a tap to rate can't be shown again after user rate it
