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
