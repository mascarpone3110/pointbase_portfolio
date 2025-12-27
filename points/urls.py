from django.urls import path

from .views import (
    # ----- 商品 -----
    ItemListView, ItemCreateView, ItemDetailAPI, ItemUpdateView, ItemDeleteView,
    ItemAdminDetailView,
    # ----- 注文 -----
    OrderListAPI, CreateOrderAPI, OrderDetailAPI,
    CancelOrderAPI, MarkOrderDeliveredAPI,

    # ----- ポイント -----
    TeacherStudentsView, TeacherAddPointsView,
    StudentPointHistoryView, AllPointsHistoryView,

    # ----- クラス管理 -----
    ClassListView,        # GET一覧 / POST作成
    AdminClassDetailView, # クラス詳細
    AdminChangeStudentClassView, # 生徒のクラス変更
    StudentsByClassView,  # /api/classes/all /none /1 など
    UpdateStudentClassView,
    ClassDeleteView,
    ClassStudentsView,

)

urlpatterns = [
    # -------------------------
    # 商品
    # -------------------------
    path("items/", ItemListView.as_view()),
    path("items/create/", ItemCreateView.as_view()),
    path("items/<str:id>/", ItemDetailAPI.as_view()),
    path("items/<str:id>/admin/", ItemAdminDetailView.as_view()),
    path("items/<str:id>/update/", ItemUpdateView.as_view()),
    path("items/<str:id>/delete/", ItemDeleteView.as_view()),

    # -------------------------
    # 注文
    # -------------------------
    path("orders/", OrderListAPI.as_view()),
    path("orders/create/", CreateOrderAPI.as_view()),
    path("orders/<str:order_id>/cancel/", CancelOrderAPI.as_view()),
    path("orders/<str:order_id>/delivered/", MarkOrderDeliveredAPI.as_view()),
    path("orders/<str:pk>/", OrderDetailAPI.as_view()),

    # -------------------------
    # ポイント
    # -------------------------
    path("teacher/students/", TeacherStudentsView.as_view()),
    path("teacher/points/add/", TeacherAddPointsView.as_view()),
    path("points/history/", AllPointsHistoryView.as_view()),
    path("points/history/<uuid:user_id>/", StudentPointHistoryView.as_view()),

    # -------------------------
    # クラス管理（teacher/admin 共通）
    # -------------------------
    path("classes/change/", UpdateStudentClassView.as_view(), name="class_change"),
    path("classes/", ClassListView.as_view()),                     # 一覧 & 作成
    path("classes/all/", StudentsByClassView.as_view(), {"mode": "all"}),
    path("classes/none/", StudentsByClassView.as_view(), {"mode": "none"}),
    # path("classes/change/", UpdateStudentClassView.as_view(), name="class_change"),
    path("classes/<int:class_id>/", StudentsByClassView.as_view(), {"mode": "by_class"}),
    path("classes/<int:pk>/delete/", ClassDeleteView.as_view(), name="class_delete"),
    path("classes/<str:pk>/students/", ClassStudentsView.as_view()),

    path("admin/classes/<int:class_id>/", AdminClassDetailView.as_view()),
    path("admin/students/<uuid:user_id>/change_class/", AdminChangeStudentClassView.as_view()),

]
