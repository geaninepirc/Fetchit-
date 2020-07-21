from django.urls import path
from . import views

urlpatterns = [
    path('product-sets/', views.ProductSetView.as_view()),
    path('products/', views.ProductView.as_view()),
    path('reference-image/', views.RefImageView.as_view()),
    path('create-pure-reference-image/', views.PureCreateRefImageView.as_view()),
    path('reference-image/<int:ref_img_id>/', views.RefImageView.as_view()),
]