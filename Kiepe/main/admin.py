from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CancelledOrdersByCustomer)
admin.site.register(CancelledOrdersByKibanda)
admin.site.register(KibandaRating)
admin.site.register(CustomerRating)
admin.site.register(DeviceAuthModel)
admin.site.register(DeviceNotificationToken)
admin.site.register(Notification)
admin.site.register(KibandaPayments)
admin.site.register(PaymentReferenceNumbers)
admin.site.register(TransactionRecords)
admin.site.register(SessionIds)
admin.site.register(AdVotes)
admin.site.register(AdRating)
admin.site.register(AdComments)
admin.site.register(CommentLikes)
admin.site.register(CommentReplies)
admin.site.register(Ads)
admin.site.register(ReplyLikes)
