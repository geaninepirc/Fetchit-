from django.urls import path
from . import views

urlpatterns = [
    path('product-categories', views.productCategoryList.as_view()),
    # path('product-category/<int:category_id>', views.productCategoryInfo.as_view()),
    path('options', views.optionList.as_view()),
    # path('option/<int:optiond_id>', views.optionInfo.as_view()),
    path('option-groups', views.optionGroupList.as_view()),
    # path('option-group/<int:group_id>', views.optionGroupInfo.as_view()),
    path('products', views.productList.as_view()),
    path('products/<int:page_id>', views.productList.as_view()),
    path('products-with-category/<int:category_id>', views.productListWithCategory.as_view()),
    path('products-with-category/<int:category_id>/<int:page_id>', views.productListWithCategory.as_view()),
    # path('search', views.productListWithSearch.as_view()),
    # path('search/<int:page_id>', views.productListWithCategory.as_view()),
    path('search-with-captured-image', views.searchProductWithImageFile.as_view()),
    # path('search-with-captured-image-base64', views.searchProductWithImageBase64.as_view()),
    path('product/<int:product_id>', views.productInfo.as_view()),
]