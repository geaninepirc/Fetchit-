from rest_framework import serializers

from .models import ProductSetInVisionAI, ProductInVisionAI, ReferrenceImagesInVisionAI

class ProductSetInVisionAISerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductSetInVisionAI
        fields = '__all__'

class ProductInVisionAISerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInVisionAI
        fields = '__all__'

class ReferrenceImagesInVisionAISerializer(serializers.ModelSerializer):

    class Meta:
        model = ReferrenceImagesInVisionAI
        fields = '__all__'