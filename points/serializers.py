from rest_framework import serializers
from .models import Item,  Order, OrderItem
from rest_framework import serializers
from accounts.models import UserProfile, User
from .models import PointManager, PointTransaction


# class ItemSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField()
#     created_at = serializers.DateTimeField(read_only=True)

#     class Meta:
#         model = Item
#         fields = [
#             "id",
#             "name",
#             "price",
#             "stock",
#             "description",
#             "image",
#             "created_at",
#             "is_published"
#         ]
#         read_only_fields = ["id", "price", "created_at"]

#     def get_image(self, obj):
#         request = self.context.get("request")
#         if not obj.image:
#             return None
#         if request:
#             return request.build_absolute_uri(obj.image.url)
#         return obj.image.url  # fallback


# class ItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Item
#         fields = "__all__"
#         read_only_fields = ["id", "created_at"]

class ItemSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "price",
            "stock",
            "description",
            # "image",      
            "image_url", 
            "created_at",
            "is_published",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url





class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "item", "item_name", "quantity", "price", "image"]

    def get_image(self, obj):
        # Itemモデルの image をそのまま返す（URL or ImageField）
        if obj.item and obj.item.image:
            try:
                return obj.item.image.url  # ImageField の場合
            except:
                return obj.item.image      # URL文字列の場合
        return None


class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    name = serializers.CharField(source="user.name", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "user_id",
            "username",
            "name",
            "status",
            "created_at",
            "delivered_at",
            "canceled_at",
            "items",
        ]



class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "total_amount", "fee", "status", "created_at", "delivered_at" ,"items"]


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.id")
    username = serializers.CharField(source="user.username")
    name = serializers.CharField(source="user.name")
    balance = serializers.SerializerMethodField()
    class_ref = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = UserProfile
        fields = ["user", "username", "name", "balance", "class_ref"]

    def get_balance(self, obj):
        pm = PointManager.objects.get(user=obj.user)
        return pm.point_balance


class TeacherPointAddSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.UUIDField())
    amount = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("Amount cannot be zero.")
        return value


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = [
            "id",
            "points",
            "transaction_type",
            "description",
            "created_at",
            "balance_after", 
        ]