# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
# from .models import UserProfile

# User = get_user_model()

# class SignupSerializer(serializers.ModelSerializer):
    
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'name']

#     def create(self, validated_data):
        
#         name = validated_data.pop('name', '')
        
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         user.name = name
#         user.save()
#         return user


from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile
from points.models import PointManager
 
User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'name']

    def create(self, validated_data):
        password = validated_data.pop("password")
        name = validated_data.pop("name")

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            name=name,
        )
        user.set_password(password)
        user.save()
        return user
# class SignupSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'name']

#     def create(self, validated_data):
#         print("==== validated_data ====")
#         print(validated_data)  # ← name が来てるか確認

#         password = validated_data.pop("password", None)
#         name = validated_data.pop("name", None)

#         print(">>>> name popped:", name)

#         user = User(
#             username=validated_data.get("username"),
#             email=validated_data.get("email"),
#             name=name,
#         )

#         print(">>>> user before save:", user.username, user.email, user.name)

#         user.set_password(password)
#         user.save()

#         # 保存後に DB から再取得して確認
#         saved = User.objects.get(id=user.id)
#         print(">>>> DB saved name:", saved.name)

#         return saved


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["image", "role", "is_totp_verified"]


    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    # ★ 追加：point_balance を MeView に含める
    point_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "profile",
            "point_balance", 
        ]

    def get_point_balance(self, obj):
        try:
            pm = PointManager.objects.get(user=obj)
            return pm.point_balance
        except PointManager.DoesNotExist:
            return 0
