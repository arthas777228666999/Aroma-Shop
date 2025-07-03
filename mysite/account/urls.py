from django.urls import path
from .views import registration_view, logout_view, login_view, account_view, reset_password_view, account_change_view

urlpatterns = [                 
    path('register/', registration_view, name="register"),
    path('logout/', logout_view, name="logout"),
    path('login/', login_view, name="login"),  
    path('account/', account_view, name="account"), 
    path('reset_password/', reset_password_view, name="reset_password"),
    path('account/change/', account_change_view, name="account_change"),

]
