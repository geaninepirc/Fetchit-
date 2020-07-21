from rest_framework import serializers

from .models import TrainedModel, ProductInTrainedModel

class TrainedModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainedModel
        fields = '__all__'

class ProductInTrainedModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInTrainedModel
        fields = '__all__'