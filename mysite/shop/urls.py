from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', home_screen_view, name='home'),
    path('index/', home_screen_view, name='index'),
    path('cart/', cart_view, name='cart'),
    path('wishlist/', wishlist_view, name='wishlist'),

    # Списки товарів
    path('product_list/', product_list_view, name='product_list'),
    path('product_list_perf/', product_list_perf_view, name='product_list_perf'),
    path('product_list_cand/', product_list_cand_view, name='product_list_cand'),
    path('scent_of_month/', scent_of_month_view, name='scent_of_month'),
    path('perfume_filtered_list/<str:filter_type>/<str:filter_value>/', filtered_perfume_list_view, name='filtered_perfumes'),
    path('candle_filtered_list/<str:filter_type>/<str:filter_value>/', filtered_candle_list_view, name='filtered_candles'),
    path('darkfem_collection/', darkfem_collection_view, name='darkfem_collection'),
    path('loveme_collection/', loveme_collection_view, name='loveme_collection'),
    path('<str:model_name>/<int:product_id>/', product_card_view, name='product_card'),


    # Кошик
    path('cart/add/<str:model_name>/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    
    # Вішліст
    path('wishlist/add/<str:model_name>/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<int:item_id>/', move_to_cart, name='move_to_cart'),
    path('wishlist/toggle/', views.wishlist_toggle, name='wishlist_toggle'),

    #Пошук
    path('search/', SearchProductsView.as_view(), name='search'),
    path('ajax/search-suggestions/', search_suggestions, name='search_suggestions'),
    path('ajax/search-products/', ajax_search_products, name='ajax_search_products'),

    #Оформлення замовлення
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    #Інше
    path('about_us/', about_us_view, name='about_us'),
    path('partnership/', partnership_view, name='partnership'),
    path('delivery_info/', delivery_info_view, name='delivery_info'),
    path('contacts/', contacts_view, name='contacts'),

]
