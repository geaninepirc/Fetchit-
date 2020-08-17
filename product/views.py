from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProductCategory, Option, OptionGroup, Product, ProductMedia, ProductOption
from .serializers import ProductCategorySerializer, OptionSerializer, OptionGroupSerializer, ProductSimpleSerializer, ProductDetailSerializer
# from automlsearch import utils
# from automlsearch.models import TrainedModel
from automlsearch.views import SearchProduct

from datetime import datetime, timezone
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create your views here.
class productCategoryList(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, *args, **kwargs):
        product_category_list = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(product_category_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

# class productCategoryInfo(APIView):
#     permission_classes = (permissions.AllowAny, )

#     def get(self, request, category_id, *args, **kwargs):
#         product_category_info = ProductCategory.objects.get(pk=category_id)

#         return Response([], status=status.HTTP_200_OK)

class optionList(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, *args, **kwargs):
        options = Option.objects.all()
        serializer = OptionSerializer(options, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)  

# class optionInfo(APIView):
#     permission_classes = (permissions.AllowAny, )

#     def get(self, option_id, request, *args, **kwargs):
#         option_info = Option.objects.get(pk=option_id)

#         return Response([], status=status.HTTP_200_OK)

class optionGroupList(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, *args, **kwargs):
        option_groups = OptionGroup.objects.all()
        serializer = OptionGroupSerializer(option_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

# class optionGroupInfo(APIView):
#     permission_classes = (permissions.AllowAny, )

#     def get(self, request, group_id, *args, **kwargs):
#         option_group_info = OptionGroup.objects.get(pk=group_id)

#         return Response([], status=status.HTTP_200_OK)

class productList(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, page_id=1, *args, **kwargs):
        products = Product.objects.filter(active=True)
        product_count = products.count()
        serializer = ProductSimpleSerializer(products[(page_id - 1) * 100 : page_id * 100], many=True, context={'request': request})
        
        return Response({
            'products': serializer.data,
            'product_count': product_count,
        }, status=status.HTTP_200_OK)

class productListWithCategory(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, category_id, page_id=1, *args, **kwargs):
        products = Product.objects.filter(product_category__id=category_id).filter(active=True)
        product_count = products.count()
        serializer = ProductSimpleSerializer(products[(page_id - 1) * 100 : page_id * 100], many=True, context={'request': request})

        return Response({
            'products': serializer.data,
            'product_count': product_count,
        }, status=status.HTTP_200_OK)

# class productListWithSearch(APIView):
#     permission_classes = (permissions.AllowAny, )

#     def post(self, request, page_id=1, *args, **kwargs):
#         search_string = request.data['search_string']
#         if category_id:
#             product_list = Product.objects.filter(product_category__id=category_id)
#             return Response([], status=status.HTTP_200_OK)
#         else:
#             product_list = Product.objects.all()
#             return Response([], status=status.HTTP_200_OK)

class productInfo(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, product_id, *args, **kwargs):
        product_info = Product.objects.get(pk=product_id)
        serializer = ProductDetailSerializer(product_info, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class searchProductWithImageFile(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        result = SearchProduct.post(self, request)
        return result

    



