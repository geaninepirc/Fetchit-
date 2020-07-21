from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from .models import ProductSetInVisionAI, ProductInVisionAI, ReferrenceImagesInVisionAI, PRODUCT_CATEGORIES_IN_VISION_AI
from product.models import Product
from .serializers import ProductSetInVisionAISerializer, ProductInVisionAISerializer, ReferrenceImagesInVisionAISerializer
from . import utils

# Create your views here.
## template views for admin panel
def boundaryEdit(request, ref_img_id):

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(request.user)
    token = jwt_encode_handler(payload)
    
    ref_image = ReferrenceImagesInVisionAI.objects.get(pk=ref_img_id)
    ref_image_url = ref_image.gcs_storage_uri.replace('gs://', 'https://storage.googleapis.com/')
    
    bounding_poly = ref_image.bounding_poly
    if bounding_poly == None or bounding_poly == '':
        bounding_poly = '[]'
    
    return render(
        request, 
        'boundary_editor.html',
        {
            'token': token,
            'ref_image': ref_image,
            'ref_image_url': ref_image_url,
            'bounding_poly': bounding_poly
        }
    )

## api views
class ProductSetView(APIView):
    permission_classes = (permissions.IsAdminUser, )
    
    # get all the product sets
    def get(self, request, *args, **kwargs):
        product_sets = ProductSetInVisionAI.objects.all().order_by('display_name')
        serializer = ProductSetInVisionAISerializer(product_sets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # create a new product set
    def post(self, request, *args, **kwargs):
        new_product_set = ProductSetInVisionAI()
        new_product_set.display_name = request.data['display_name']

        result = utils.create_product_set(request.data['product_set_id'], request.data['display_name'])
        new_product_set.path = result.name
        new_product_set.save()

        serializer = ProductSetInVisionAISerializer(new_product_set)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # delete the product set
    def delete(self, request, *args, **kwargs):
        target_product_set = ProductSetInVisionAI.objects.get(pk=request.data['id'])
        utils.delete_product_set(target_product_set.path)
        target_product_set.delete()

        return Response({'success': True}, status=status.HTTP_202_ACCEPTED)

class ProductView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    # get all the products
    def get(self, request, *args, **kwargs):
        products = ProductInVisionAI.objects.filter(product_set__id=int(request.GET['product_set_id'])).order_by('display_name')
        serializer = ProductInVisionAISerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # create a new product
    def post(self, request, *args, **kwargs):
        new_product = ProductInVisionAI()
        new_product.display_name = request.data['display_name']
        product_set = ProductSetInVisionAI.objects.get(pk=request.data['product_set_id'])
        new_product.product_set = product_set
        new_product.product = Product.objects.get(pk=request.data['product_id'])
        new_product.product_category_in_vision_ai = request.data['product_category_in_vision_ai']
        result = utils.create_product_add_to_product_set(product_set.path, request.data['display_name'], PRODUCT_CATEGORIES_IN_VISION_AI[request.data['product_category_in_vision_ai'] - 1][1])
        new_product.path = result.name
        new_product.save()
        serializer = ProductInVisionAISerializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # delete the product
    def delete(self, request, *args, **kwargs):
        target_product = ProductInVisionAI.objects.get(pk=request.data['id'])
        utils.remove_product_from_product_set(target_product.path, target_product.product_set.path)
        utils.delete_product(target_product.path)
        target_product.delete()
        return Response({'success': True}, status=status.HTTP_202_ACCEPTED)

### ref image view for admin panel
class RefImageView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    # get all the ref. images
    def get(self, request, *args, **kwargs):
        ref_images = ReferrenceImagesInVisionAI.objects.filter(product__id=int(request.GET['product_id'])).order_by('vision_path')
        serializer = ReferrenceImagesInVisionAISerializer(ref_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # create a new ref. image ## for bounding poly editor
    def post(self, request, ref_img_id, *args, **kwargs):
        ref_image = ReferrenceImagesInVisionAI.objects.get(pk=ref_img_id)
        bounding_poly = request.data['bounding_poly']
        if len(bounding_poly) == 0:
            bounding_poly = None
        
        # response
        response = utils.create_reference_image(ref_image.product.path, ref_image.gcs_storage_uri, bounding_poly)
        print("## Ref. Image Response ##")
        print(response)
        print("## End ##")
        ref_image.vision_path = response['name']
        ref_image.bounding_poly = response['boundingPolys'][0]['normalizedVertices']
        ref_image.is_registerd = True
        ref_image.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)

    # edit the ref. image ## for bounding poly editor
    def put(self, request, ref_img_id, *args, **kwargs):
        ref_image = ReferrenceImagesInVisionAI.objects.get(pk=ref_img_id)
        bounding_poly = request.data['bounding_poly']
        if len(bounding_poly) == 0:
            bounding_poly = None

        # response
        utils.delete_reference_image(ref_image.vision_path)
        response = utils.create_reference_image(ref_image.product.path, ref_image.gcs_storage_uri, bounding_poly)
        ref_image.vision_path = response['name']
        print("## Ref. Image Response ##")
        print(response)
        print("## End ##")
        ref_image.bounding_poly = response['boundingPolys'][0]['normalizedVertices']
        ref_image.is_registerd = True
        ref_image.save()
        return Response({'success': True}, status=status.HTTP_202_ACCEPTED)

    # delete the ref. image
    def delete(self, request, ref_img_id, *args, **kwargs):
        ref_image = ReferrenceImagesInVisionAI.objects.get(pk=ref_img_id)
        utils.delete_reference_image(ref_image.vision_path)
        ref_image.delete()
        return Response({'success': True}, status=status.HTTP_202_ACCEPTED)

### ref. image API to create a ref. image without the bounding polys editor

class PureCreateRefImageView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    def post(self, request, *args, **kwargs):
        ref_image = ReferrenceImagesInVisionAI()
        ref_image.gcs_storage_uri = request.data['gcs_storage_uri']
        product_in_vision = ProductInVisionAI.objects.get(pk=request.data['product_in_vision_id'])
        ref_image.product = ProductInVisionAI.objects.get(pk=request.data['product_in_vision_id'])
        
        result = utils.create_reference_image(product_in_vision.path, request.data['gcs_storage_uri'])
        ref_image.vision_path = result['name']
        ref_image.is_registerd = True
        ref_image.save()
        serializer = ReferrenceImagesInVisionAISerializer(ref_image)

        return Response(serializer.data, status=status.HTTP_201_CREATED)