from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ItemSerializer, OrderSerializer, OrderDetailSerializer,PointTransactionSerializer
from .models import Item, Order, OrderItem, PointManager, PointTransaction
from rest_framework.views import APIView
from accounts.models import UserProfile, User
from .permissions import IsTeacherOrAdmin
from django.shortcuts import get_object_or_404
from .models import ClassMaster
from rest_framework.parsers import MultiPartParser, FormParser
import os
import shutil
try:
    import boto3
except ImportError:
    boto3 = None
from django.utils.timezone import now

# Item 

# class ItemCreateView(APIView):
#     permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

#     def post(self, request):
#         serializer = ItemSerializer(data=request.data)
    
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Item created", "item": serializer.data})

#         return Response(serializer.errors, status=400)
class ItemCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request):
        item = Item.objects.create(
            name=request.data.get("name"),
            price=request.data.get("price"),
            stock=request.data.get("stock"),
            description=request.data.get("description"),
            is_published=str_to_bool(request.data.get("is_published")),  # ★ここ
            image=request.FILES.get("image"),
        )

        return Response(
            {
                "message": "Item created",
                "item": ItemSerializer(item, context={"request": request}).data,
            },
            status=201,
        )


class ItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.all().order_by("-created_at")
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class ItemDetailAPI(generics.RetrieveAPIView):
    queryset = Item.objects.filter(is_published=True)
    serializer_class = ItemSerializer
    lookup_field = "id"

    def get_serializer_context(self):
        return {"request": self.request}

class ItemAdminDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    queryset = Item.objects.all()   # ← is_published を見ない
    serializer_class = ItemSerializer
    lookup_field = "id"

def str_to_bool(val):
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return val.lower() in ["true", "1", "yes", "on"]

class ItemUpdateView(APIView):
    def patch(self, request, id, *args, **kwargs):
        try:
            item = Item.objects.get(id=id)
        except Item.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        item.name = request.data.get("name", item.name)
        item.price = request.data.get("price", item.price)
        item.stock = request.data.get("stock", item.stock)
        item.description = request.data.get("description", item.description)

        # ★ ここが重要：文字列を bool に変換して代入
        if "is_published" in request.data:
            item.is_published = str_to_bool(request.data.get("is_published"))

        # 画像があれば更新
        if "image" in request.FILES:
            item.image = request.FILES["image"]

        item.save()
        return Response({"message": "updated"})
    



class ItemDeleteView(APIView):
    """
    商品削除（画像ファイルを含む）
    ・ローカル: media/items/<id>/ フォルダごと削除
    ・S3: items/<id>/ 配下のオブジェクトを全削除
    """

    def delete(self, request, id, *args, **kwargs):
        try:
            item = Item.objects.get(id=id)
        except Item.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        # -----------------------------
        # 1) S3 Storage かどうか判定
        # -----------------------------
        storage = item.image.storage

        # -----------------------------
        # ★ S3 の場合
        # -----------------------------
        if hasattr(storage, "bucket_name"):  # boto3 storage の場合この属性がある
            bucket_name = storage.bucket_name
            s3 = boto3.resource("s3")
            bucket = s3.Bucket(bucket_name)

            prefix = f"items/{id}/"

            # prefix 以下を全部削除
            bucket.objects.filter(Prefix=prefix).delete()

            # DBだけ削除
            item.delete()

            return Response({"message": "deleted (S3)"}, status=200)

        # -----------------------------
        # ★ ローカル FileSystemStorage の場合
        # -----------------------------
        else:
            # image.path が存在すればフォルダを削除
            if item.image:
                folder_path = os.path.dirname(item.image.path)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path, ignore_errors=True)

            item.delete()
            return Response({"message": "deleted (local)"}, status=200)


# Order

class CreateOrderAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        items = request.data.get("items", [])
        fee = int(request.data.get("fee", 0)) 

        if not items:
            return Response({"error": "No items in order."}, status=400)

        # ユーザーのポイント残高
        point_manager = PointManager.objects.get(user=user)

        # 合計計算（商品分）
        total_points = sum(i["price"] * i["quantity"] for i in items)

        # 🔥 ここで手数料を含める
        grand_total = total_points + fee

        # ポイント不足チェック
        if point_manager.point_balance < grand_total:
            return Response({"error": "ポイントが足りません"}, status=400)

        # 注文オブジェクト作成（合計ポイント反映）
        order = Order.objects.create(
            user=user,
            total_amount=grand_total, 
            status="pending",
            fee=fee
        )

        # 注文アイテム保存
        for data in items:
            is_amazon = data.get("is_amazon", False)
            item_id = data["id"]

            OrderItem.objects.create(
                order=order,
                item=None if is_amazon else Item.objects.get(id=item_id),
                asin=item_id.replace("A-", "") if is_amazon else "",
                item_name=data["name"],
                quantity=data["quantity"],
                price=data["price"],
                fee=fee
            )

        # ポイント減算（手数料込み）
        point_manager.point_balance -= grand_total
        point_manager.save()

        # トランザクション履歴
        PointTransaction.objects.create(
            user=user,
            points=-grand_total,
            transaction_type="spend",
            description=f"注文 ID {order.id}",
            balance_after=point_manager.point_balance
        )

        # 注文を success に更新
        order.status = "success"
        order.save()

        # レスポンス
        return Response({
            "message": "Order created",
            "order_id": order.id,
            "total": point_manager.point_balance
        }, status=200)

class CancelOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user
        profile = UserProfile.objects.get(user=user)

        # teacher/admin → 全注文操作可能
        if profile.role in ["teacher", "admin"]:
            order = get_object_or_404(Order, id=order_id)
        else:
            # 生徒は自分の注文だけ
            order = get_object_or_404(Order, id=order_id, user=user)

        # delivered はキャンセル禁止
        if order.status == "delivered":
            return Response({"error": "受け取り済みの注文はキャンセルできません"}, status=400)

        if order.status == "canceled":
            return Response({"message": "すでにキャンセル済みです"}, status=200)

        # ポイント返金（注文者に返す）
        point_manager = PointManager.objects.get(user=order.user)
        point_manager.point_balance += order.total_amount
        point_manager.save()

        # トランザクション
        PointTransaction.objects.create(
            user=order.user,
            points=order.total_amount,
            transaction_type="refund",
            description=f"注文キャンセル ID {order.id}",
            balance_after=point_manager.point_balance,
        )

        order.status = "canceled"
        order.canceled_at = now()
        order.save()

        return Response({
            "message": "注文をキャンセルしました",
            "order_id": order.id,
            "new_balance": point_manager.point_balance
        })



class MarkOrderDeliveredAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.status == "delivered":
            return Response({"message": "すでに受け取り済みです"}, status=200)

        if order.status == "canceled":
            return Response({"error": "キャンセル済みの注文は受け取りできません"}, status=400)

        # delivered に変更
        order.status = "delivered"
        order.delivered_at = now()
        order.save()

        return Response({
            "message": "商品を受け取ったことを記録しました",
            "delivered_at": order.delivered_at
        })

class OrderListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", "student")

        # Teacher/Admin → 全注文
        if role in ["teacher", "admin"]:
            return Order.objects.select_related("user").order_by("-created_at")

        # Student → 自分の注文
        return Order.objects.filter(user=user).order_by("-created_at")



class OrderDetailAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import IsTeacherOrAdmin
from .serializers import StudentSerializer, TeacherPointAddSerializer
from accounts.models import User, UserProfile
from .models import PointManager, PointTransaction


class TeacherStudentsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        students = UserProfile.objects.filter(role="student").select_related("user")
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class TeacherAddPointsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request):
        serializer = TeacherPointAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data["user_ids"]
        amount = serializer.validated_data["amount"]
        description = serializer.validated_data["description"]

        for uid in user_ids:
            try:
                target = User.objects.get(id=uid)
            except User.DoesNotExist:
                continue

            pm = PointManager.objects.get(user=target)
            pm.point_balance += amount
            pm.save()

            PointTransaction.objects.create(
                user=target,
                points=amount,
                transaction_type="teacher",
                description=description,
                balance_after=pm.point_balance
            )

        return Response({"success": True})


# ============================
# 　Check
# ============================
def can_view_history(request_user, target_user_id):
    """本人 or teacher or adminならTrue"""
    # プロフィールがない可能性も考慮
    role = getattr(request_user.profile, "role", "student")

    # 管理者・先生ならOK
    if role in ["teacher", "admin"]:
        return True

    # 本人ならOK
    return str(request_user.id) == str(target_user_id)


# ============================
# 🔵 StudentPointHistoryView
# ============================
class StudentPointHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):

        # --- 対象ユーザー取得 ---
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # --- 認可チェック ---
        if not can_view_history(request.user, user_id):
            return Response(
                {"detail": "You do not have permission to view this history."},
                status=403
            )

        # --- 履歴取得 ---
        history = PointTransaction.objects.filter(user=target).order_by("-created_at")

        # --- レスポンス整形 ---
        data = [{
            "id": h.id,
            "points": h.points,
            "transaction_type": h.transaction_type,
            "description": h.description,
            "created_at": h.created_at,
            "balance_after": h.balance_after,  # ← 取引後残高
        } for h in history]

        return Response(data)



class AllPointsHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        # 全ての履歴を新しい順に並べる
        history = PointTransaction.objects.select_related("user").order_by("-created_at")

        data = []

        for h in history:
            data.append({
                "id": h.id,
                "points": h.points,
                "transaction_type": h.transaction_type,
                "description": h.description,
                "created_at": h.created_at,
                "user_name": h.user.name,
                "username": h.user.username,
                "user_id": str(h.user.id),
                # "balance_after": h.balance_after,
            })

        return Response(data)



#classes管理
class UpdateStudentClassView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request):
        user_id = request.data.get("user_id")
        class_id = request.data.get("class_id")  

        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        profile.class_ref_id = class_id
        profile.save()

        return Response({"message": "Class updated"})




from django.db.models import Q


class ClassStudentsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request, pk):
        students = UserProfile.objects.filter(role="student", class_ref_id=pk).select_related("user")

        data = [
            {
                "user_id": str(s.user.id),
                "username": s.user.username,
                "name": s.user.name,
                "balance": PointManager.objects.get(user=s.user).point_balance,
                "class_id": s.class_ref_id
            }
            for s in students
        ]

        return Response(data)




class ClassDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        ClassMaster.objects.filter(id=pk).delete()
        return Response({"message": "deleted"})




class ClassChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_ids = request.data.get("user_ids", [])
        class_id = request.data.get("class_id")

        UserProfile.objects.filter(user_id__in=user_ids).update(class_ref_id=class_id)

        return Response({"message": "updated"})


class ClassRankingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        students = UserProfile.objects.filter(class_ref_id=pk).order_by("-balance")
        data = [
            {"name": s.user.first_name, "balance": s.balance}
            for s in students
        ]
        return Response(data)

class AdminChangeStudentClassView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request, user_id):
        class_id = request.data.get("class_id")

        try:
            profile = UserProfile.objects.get(user__id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "user not found"}, status=404)

        if class_id in ("", None):
            profile.class_ref = None
        else:
            try:
                cls = ClassMaster.objects.get(id=class_id)
            except ClassMaster.DoesNotExist:
                return Response({"error": "class not found"}, status=404)
            profile.class_ref = cls

        profile.save()
        return Response({"message": "updated"})



class AdminClassDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request, class_id):
        try:
            cls = ClassMaster.objects.get(id=class_id)
        except ClassMaster.DoesNotExist:
            return Response({"error": "class not found"}, status=404)

        students = UserProfile.objects.filter(
            role="student",
            class_ref_id=class_id
        ).select_related("user")

        data = {
            "id": cls.id,
            "name": cls.name,
            "students": [
                {
                    "user": str(s.user.id),
                    "username": s.user.username,
                    "name": s.user.name,
                    "balance": PointManager.objects.get(user=s.user).point_balance,
                    "class_id": s.class_ref_id,
                }
                for s in students
            ],
        }

        return Response(data)






class ClassListView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        classes = ClassMaster.objects.all().values("id", "name")
        return Response(list(classes))

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"error": "name is required"}, status=400)

        ClassMaster.objects.create(name=name)
        return Response({"message": "created"})




class StudentsByClassView(APIView):
    """
    クラス別生徒一覧:
    /api/classes/all/
    /api/classes/none/
    /api/classes/<id>/
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request, mode, class_id=None):
        qs = UserProfile.objects.filter(role="student").select_related("user", "class_ref")

        if mode == "all":
            pass

        elif mode == "none":
            qs = qs.filter(class_ref__isnull=True)

        elif mode == "by_class":
            if class_id is None:
                return Response({"detail": "class_id required"}, status=400)
            qs = qs.filter(class_ref_id=class_id)

        else:
            return Response({"detail": "invalid mode"}, status=400)

        serializer = StudentSerializer(qs, many=True)
        return Response(serializer.data)
