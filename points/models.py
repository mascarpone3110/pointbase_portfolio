# from django.db import models
# from django.conf import settings
# from django.utils.crypto import get_random_string
# from django.utils import timezone


# # ======================================================
# # 商品（自社商品）
# # ======================================================

# def upload_item_image(instance, filename):
#     return f"items/{instance.id}/{filename}"

# def create_item_id():
#     return get_random_string(22)

# class Item(models.Model):
#     id = models.CharField(primary_key=True, default=create_item_id, max_length=22)
#     name = models.CharField(max_length=100)
#     price = models.PositiveIntegerField(default=0)
#     stock = models.PositiveIntegerField(default=0)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to=upload_item_image, blank=True)
#     is_published = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Order(models.Model):
#     STATUS = (("pending", "Pending"), ("success", "Success"), ("failed", "Failed"))

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     total_amount = models.PositiveIntegerField(default=0)  # 使ったポイント
#     status = models.CharField(max_length=20, choices=STATUS, default="pending")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order({self.user.username}, {self.total_amount}pt)"


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)

#     # 自社商品の場合
#     item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)

#     # Amazon 商品の場合
#     asin = models.CharField(max_length=30, blank=True)

#     item_name = models.CharField(max_length=255)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.PositiveIntegerField()  # 1商品のポイント

#     def __str__(self):
#         return f"{self.item_name} x {self.quantity}"


# class PointManager(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     point_balance = models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.user.username}: {self.point_balance}pt"


# class PointTransaction(models.Model):
#     TYPE = (("earn", "Earn"), ("spend", "Spend"))

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     points = models.IntegerField()  # + or -
#     transaction_type = models.CharField(max_length=10, choices=TYPE)
#     description = models.CharField(max_length=255)
#     total_points = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.u
# ser.username}: {self.points}pt ({self.transaction_type})"



from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
import uuid

# ======================================================
# 商品（自社商品）
# ======================================================

def upload_item_image(instance, filename):
    return f"items/{instance.id}/{filename}"

def create_item_id():
    return get_random_string(22)


def generate_order_id():
    """
    PB-XXXXXX のようなプロっぽい注文番号を作成
    衝突を避けるためUUIDの前方を使う方式
    """
    prefix = "PB"
    uid = uuid.uuid4().hex[:10].upper()  # 10桁でほぼ衝突しない
    return f"{prefix}-{uid}"


class Item(models.Model):
    id = models.CharField(primary_key=True, default=create_item_id, max_length=22)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_item_image, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# class Order(models.Model):
#     STATUS = (("pending", "Pending"), ("success", "Success"), ("failed", "Failed"))

#     # ★ ここ！！ランダムな注文番号を主キーにする
#     id = models.CharField(
#         primary_key=True,
#         max_length=20,
#         default=generate_order_id,
#         editable=False
#     )

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     total_amount = models.PositiveIntegerField(default=0)  # 使ったポイント
#     status = models.CharField(max_length=20, choices=STATUS, default="pending")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order({self.id}, {self.user.username}, {self.total_amount}pt)"
    
class Order(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("canceled", "Canceled"),
        ("delivered", "Delivered"),
    )

    # 元のランダムIDを復活
    id = models.CharField(
        primary_key=True,
        max_length=20,
        default=generate_order_id,
        editable=False
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order({self.id}, {self.user.username}, {self.total_amount}pt)"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)

    # 自社商品の場合
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)

    # Amazon 商品の場合
    asin = models.CharField(max_length=30, blank=True)

    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()  # 1商品のポイント

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"


class PointManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    point_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.point_balance}pt"


class PointTransaction(models.Model):
    TYPE = (
        ("earn", "Earn"),        # 購入などによる自動獲得
        ("spend", "Spend"),      # 商品購入
        ("teacher", "Teacher"),  # 先生の付与
        ("admin", "Admin"),      # 管理者調整
    )

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField()  # 付与は +、消費は - で保存
    transaction_type = models.CharField(max_length=10, choices=TYPE)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    balance_after = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.points}pt ({self.transaction_type})"


class ClassMaster(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
