from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from rest_framework import permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TrainedModel, ProductInTrainedModel
from product.models import Product
from .serializers import TrainedModelSerializer, ProductInTrainedModelSerializer
from . import utils

from datetime import datetime, timezone
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_ROOT = 'machine_learning_data/search'

# Create your views here.
class TrainedModelView(APIView):
    permission_classes = (permissions.IsAdminUser, )
    # parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    
    # get the latest trained model
    def get(self, request, *args, **kwargs):
        trained_model = TrainedModel.objects.order_by('-reg_date')[0]
        serializer = TrainedModelSerializer(trained_model)

        return Response(serializer.data, status=status.HTTP_200_OK)
      
    # create a new trained model
    def post(self, request, *args, **kwargs):
        file_list = request.FILES.getlist('model_files')
        model_file = file_list[0]
        model_file_name = 'model_{}.hdf5'.format(int(datetime.now().timestamp()))
        class_indices_file = file_list[1]
        class_indices_file_name = 'class_indices_{}.json'.format(int(datetime.now().timestamp()))
        
        private_storage = FileSystemStorage(location=os.path.join(BASE_DIR, 'machine_learning_data/models'))
        private_storage.save(model_file_name, model_file)
        private_storage.save(class_indices_file_name, class_indices_file)

        new_model = TrainedModel()
        new_model.model_path = 'machine_learning_data/models/{}'.format(model_file_name)
        new_model.class_indices_path = 'machine_learning_data/models/{}'.format(class_indices_file_name)
        new_model.batch_size = int(request.data['batch_size'])
        new_model.image_size = request.data['image_size']
        new_model.data_folder = request.data['data_folder']
        new_model.train_folder = request.data['train_folder']
        new_model.val_folder = request.data['val_folder']
        new_model.save()

        model_file_path = os.path.join(BASE_DIR, new_model.model_path)
        utils.load_search_model(model_file_path)

        serializer = TrainedModelSerializer(new_model)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # edit parameters of the trained model
    def put(self, request, *args, **kwargs):
        model_id = int(request.data['model_id'])
        file_list = request.FILES.getlist('model_files')
        model_file = file_list[0]
        model_file_name = 'model_{}.hdf5'.format(int(datetime.now().timestamp()))
        class_indices_file = file_list[1]
        class_indices_file_name = 'class_indices_{}.json'.format(int(datetime.now().timestamp()))

        private_storage = FileSystemStorage(location=os.path.join(BASE_DIR, 'machine_learning_data/models'))
        private_storage.save(model_file_name, model_file)
        private_storage.save(class_indices_file_name, class_indices_file)

        current_model = TrainedModel.objects.get(pk=model_id)
        current_model.model_path = 'machine_learning_data/models/{}'.format(model_file_name)
        current_model.class_indices_path = 'machine_learning_data/models/{}'.format(class_indices_file_name)
        current_model.batch_size = request.data['batch_size']
        current_model.image_size = request.data['image_size']
        current_model.data_folder = request.data['data_folder']
        current_model.train_folder = request.data['train_folder']
        current_model.val_folder = request.data['val_folder']
        current_model.reg_date = datetime.now(tz=timezone.utc)
        current_model.save()

        serializer = TrainedModelSerializer(current_model)

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class ProductInTrainedModelView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    # get the list of Products with the latest trained model
    def get(self, request, *args, **kwargs):
        products = ProductInTrainedModel.objects.order_by('-reg_date')
        serializer = ProductInTrainedModelSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # create a new product for the machine learning model
    def post(self, request, *args, **kwargs):
        new_product = ProductInTrainedModel()
        product_obj = Product.objects.get(pk=request.data['product_id'])
        new_product.product = product_obj
        new_product.product_uid = 'prdct_{}'.format(product_obj.pk)
        new_product.save()

        serializer = ProductInTrainedModelSerializer(new_product)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # edit the product for the machine learning model
    def delete(self, request, *args, **kwargs):
        ProductInTrainedModel.objects.get(pk=request.data['product_id']).delete()

        return Response({'success': True}, status=status.HTTP_202_ACCEPTED)

class RefImageView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    def post(self, request, *args, **kwargs):
        ref_image = request.FILES['ref_image']
        product_id = int(request.data['product_id'])
        train_or_test = request.data['train_or_test']
        
        latest_trained_model = TrainedModel.objects.order_by('-reg_date')[0]
        product_info = ProductInTrainedModel.objects.get(pk=product_id)
        private_storage = FileSystemStorage(location=os.path.join(BASE_DIR, 'machine_learning_data/{}'.format(latest_trained_model.data_folder)))
        ref_image_name = '{}_{}_{}'.format(product_info.product_uid, int(datetime.now().timestamp()), ref_image.name)
        # train or val
        if train_or_test == 'true':
            private_storage.save('{}/{}/{}'.format(latest_trained_model.train_folder, product_info.product_uid, ref_image_name), ref_image)
        elif train_or_test == 'false':
            private_storage.save('{}/{}/{}'.format(latest_trained_model.val_folder, product_info.product_uid, ref_image_name), ref_image)

        return Response({'success': True}, status=status.HTTP_201_CREATED)

class CreateTrainModelView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    def post(self, request, *args, **kwargs):
        image_width = request.data['image_width']
        image_height = request.data['image_height']
        batch_size = request.data['batch_size']
        model = utils.create_initial_model(ProductInTrainedModel.objects.count(), image_width, image_height)
        train_path = os.path.join(BASE_DIR, 'machine_learning_data', request.data['data_folder'], request.data['train_folder'])
        val_path = os.path.join(BASE_DIR, 'machine_learning_data', request.data['data_folder'], request.data['val_folder'])
        save_root = os.path.join(BASE_DIR, 'machine_learning_data', 'train')
        utils.train_model(model, batch_size, image_width, image_height, train_path, val_path, save_root )

        return Response({'success': True}, status=status.HTTP_200_OK)


class SearchProduct(APIView):
    permission_classes = (permissions.IsAdminUser, )

    def post(self, request, *args, **kwargs):
        # print(settings.ML_MODEL)
        search_image = request.FILES['search_image']
        private_storage = FileSystemStorage(location=os.path.join(BASE_DIR, SEARCH_ROOT))
        search_image_name = 'search_{}_{}'.format(int(datetime.now().timestamp()), search_image.name)
        private_storage.save(search_image_name, search_image)
        search_image_path = os.path.join(BASE_DIR, SEARCH_ROOT, search_image_name)
        
        latest_trained_model = TrainedModel.objects.order_by('-reg_date')[0]
        
        if settings.ML_MODEL == None:
            model_file_path = os.path.join(BASE_DIR, latest_trained_model.model_path)
            utils.load_search_model(model_file_path)
        image_dimension = latest_trained_model.image_size.split(", ")

        result = utils.search_class(search_image_path, int(image_dimension[0]), int(image_dimension[1]))

        adjusted_result = [{'id': idx, 'similarity': value} for idx, value in enumerate(result) if 1 == 1]

        return_result = utils.create_readable_product_list(adjusted_result, os.path.join(BASE_DIR, latest_trained_model.class_indices_path))

        return Response(return_result, status=status.HTTP_200_OK)