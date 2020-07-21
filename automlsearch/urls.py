from django.urls import path
from . import views

urlpatterns = [
    path('trained-model/', views.TrainedModelView.as_view()),
    path('product-in-trained-model/', views.ProductInTrainedModelView.as_view()),
    path('ref-image/', views.RefImageView.as_view()),
    path('search-product/', views.SearchProduct.as_view()),
]