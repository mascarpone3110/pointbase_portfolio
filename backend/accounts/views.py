from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from .serializers import SignupSerializer, UserSerializer
from .models import User, UserProfile, DeletedUserLog
from points.permissions import IsTeacherOrAdmin

User = get_user_model()

# =======================================
# Login
# =======================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        # ❗退会済みはログイン禁止
        if hasattr(user, "profile") and user.profile.role == "student":
            if not user.profile.is_active_student:
                return Response({"error": "退会済みの生徒です"}, status=403)

        refresh = RefreshToken.for_user(user)

        response = Response({"message": "Login successful"})
        response.set_cookie("access_token", str(refresh.access_token), httponly=True, secure=False, samesite="Lax")
        response.set_cookie("refresh_token", str(refresh), httponly=True, secure=False, samesite="Lax")

        return response
    
class ClearTokenView(APIView):
    authentication_classes = []  # 認証スキップ
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"message": "All cookies cleared"})

        # サーバー側で保持している全Cookieキーを削除
        for key in request.COOKIES.keys():
            response.delete_cookie(
                key,
                path="/",         
                samesite="Lax",   
                domain=None,      
            )
        return response


# =======================================
# Logout
# =======================================
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"}, status=200)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


# =======================================
# Me
# =======================================
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


# =======================================
# Signup
# =======================================
class SignupView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer



# =======================================
# CSRFCookie
# =======================================
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFCookieView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


# =======================================
# User Profile Me
# =======================================
class UserProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile

        return Response({
            "name": user.name or user.username,
            "comment": profile.comment,
            "image": profile.image.url if profile.image else None,
        })

    def patch(self, request):
        user = request.user
        profile = user.profile

        if "name" in request.data:
            user.name = request.data["name"]
            user.save()

        if "comment" in request.data:
            profile.comment = request.data["comment"]

        if "image" in request.FILES:
            profile.image = request.FILES["image"]

        profile.save()

        return Response({"message": "Profile updated"})


# =======================================
# Register (Public)
# =======================================
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name")
        role = request.data.get("role", "student")

        # --- 🔥 追加：username & email の重複チェック ---
        if User.objects.filter(username=username).exists():
            return Response({"error": "ユーザー名は既に使われています"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "このメールアドレスは既に登録されています"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            name=name,
        )

        profile = user.profile
        profile.role = role
        profile.save()

        return Response({"message": "登録完了", "role": role}, status=201)


# =======================================
# Teacher/Admin → Student Registration
# =======================================
class RegisterStudentByTeacherView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request):

        username = request.data.get("username")
        email = request.data.get("email")
        name = request.data.get("name", "")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "username, email, password は必須です"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "この username は既に存在します"}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"error": "この email は既に登録済みです"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            name=name,
        )

        profile = user.profile
        profile.role = "student"
        profile.save()

        return Response({
            "message": "生徒アカウントを作成しました",
            "user_id": str(user.id),
        }, status=201)


# =======================================
# 退会（deactivate）
# =======================================
class DeactivateAccountsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request, user_id):
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが存在しません"}, status=404)

        if target.profile.role != "student":
            return Response({"error": "教師/管理者は退会にできません"}, status=403)

        if not target.profile.is_active_student:
            return Response({"message": "すでに退会状態です"}, status=200)

        target.profile.is_active_student = False
        target.profile.save()

        return Response({"message": "退会処理が完了しました"}, status=200)


# =======================================
# 再開（reactivate）
# =======================================
class ReactivateAccountsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request, user_id):
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが存在しません"}, status=404)

        if target.profile.role != "student":
            return Response({"error": "教師/管理者は対象外です"}, status=403)

        target.profile.is_active_student = True
        target.profile.save()

        return Response({"message": "在籍状態を再開しました"}, status=200)



# =======================================
# 削除ログ一覧
# =======================================
class DeleteAccountsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def delete(self, request, user_id):
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが存在しません"}, status=404)

        if target.profile.role != "student":
            return Response({"error": "教師/管理者は削除できません"}, status=403)

        if target.profile.is_active_student:
            return Response({"error": "退会状態にしてから削除してください"}, status=400)

        # 🔥 ログ保存（モデル名に合わせて修正済み）
        DeletedUserLog.objects.create(
            user_id=target.id,          # ← ここ重要
            username=target.username,
            email=target.email,
            name=target.name,
            deleted_by=request.user
        )

        # Profile → User を削除
        target.profile.delete()
        target.delete()

        return Response({"message": "完全削除しました"}, status=200)

class DeletedAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = DeletedUserLog.objects.order_by("-deleted_at")
        data = [
            {
                "user_id": log.user_id,
                "username": log.username,
                "email": log.email,
                "name": log.name,
                "deleted_at": log.deleted_at,
                "deleted_by": log.deleted_by.username if log.deleted_by else None,
            }
            for log in logs
        ]

        return Response(data)


# =======================================
# アカウント一覧
# =======================================
class AccountsListView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        users = User.objects.all().order_by("username")

        data = []
        for u in users:
            p = getattr(u, "profile", None)

            data.append({
                "user": str(u.id),
                "username": u.username,
                "name": u.name,
                "profile": {
                    "is_active_student": p.is_active_student if p else True
                }
            })

        return Response(data)


# =======================================
# アカウント詳細
# =======================================
class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが存在しません"}, status=404)

        profile = user.profile

        return Response({
            "id": str(user.id),
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "profile": {
                "role": profile.role,
                "comment": profile.comment,
                "image": profile.image.url if profile.image else None,
                "is_active_student": profile.is_active_student,
                "is_totp_verified": profile.is_totp_verified,
                "created_at": user.created_at,
            }
        })
