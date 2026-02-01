# from rest_framework_simplejwt.authentication import JWTAuthentication

# class CookieJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         #Authorizationヘッダー確認
#         header_auth = super().authenticate(request)
#         if header_auth is not None:
#             return header_auth
        
#         #なければ　Cookie から access_token 探す
#         raw_token = request.COOKIES.get('access_token')
#         if raw_token is None:
#             return None
#         validated_token = self.get_validated_token(raw_token)
#         return self.get_user(validated_token), validated_token
# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 1) Authorizationヘッダ優先（Bearer対応）
        header_auth = super().authenticate(request)
        if header_auth is not None:
            return header_auth

        # 2) Cookieのaccess_tokenをチェック
        raw_token = request.COOKIES.get('access_token')
        if not raw_token:
            return None  # 認証情報なし → 他の認証 or Anonymous

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            # ★ここで500を出さず401にする（Cookieはここで消さない）
            raise AuthenticationFailed("Invalid or expired token")
