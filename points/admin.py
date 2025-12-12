from django.contrib import admin
from .models import Item, Order, OrderItem, PointManager, PointTransaction

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PointManager)
admin.site.register(PointTransaction)
