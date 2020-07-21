from rest_framework import serializers

from .models import ProductCategory, OptionGroup, Option, Product, ProductMedia, ProductOption, ProductStockPrice

class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = '__all__'

class OptionGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = OptionGroup
        fields = '__all__'

class ProductSimpleSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return_string = ''
        try:
            product_option_prices = ProductStockPrice.objects.filter(product__id=obj.id)
            max_price = max([prc.price for prc in product_option_prices])
            min_price = min([prc.price for prc in product_option_prices])
            if max_price == min_price:
                return_string = "$ " + str(max_price)
            else:
                return_string = "$ " + str(min_price) + " - " + str(max_price)
        except Exception as e:
            return_string = 'No Price'

        return return_string

    class Meta:
        model = Product
        fields = ('id', 'name', 'unit', 'price', 'short_description', 'thumbnail', 'location', 'sold_count')

class ProductMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductMedia
        fields = '__all__'

class ProductOptionSerializer(serializers.ModelSerializer):
    option_name = serializers.SerializerMethodField()

    def get_option_name(self, obj):
        return obj.option.display_name

    class Meta:
        model = ProductOption
        fields = '__all__'

class ProductStockPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductStockPrice
        fields = '__all__'

class ProductDetailSerializer(serializers.ModelSerializer):
    product_media = serializers.SerializerMethodField()
    product_options = serializers.SerializerMethodField()
    product_option_groups = serializers.SerializerMethodField()
    product_stock_prices = serializers.SerializerMethodField()

    def get_product_media(self, obj):
        request = self.context.get("request", None)
        media_list = ProductMedia.objects.filter(product__id=obj.id)
        mediaSerializer = ProductMediaSerializer(media_list, many=True, context={'request': request})
        return mediaSerializer.data
    def get_product_options(self, obj):
        option_list = ProductOption.objects.filter(product__id=obj.id).filter(active=True)
        optionSerializer = ProductOptionSerializer(option_list, many=True)
        return optionSerializer.data
    def get_product_option_groups(self, obj):
        option_list = ProductOption.objects.filter(product__id=obj.id).filter(active=True)
        group_id_list = [op.option_group_id for op in option_list]
        group_list = OptionGroup.objects.filter(id__in=group_id_list)
        groupSerializer = OptionGroupSerializer(group_list, many=True)
        return groupSerializer.data
    def get_product_stock_prices(self, obj):
        stock_price_list = ProductStockPrice.objects.filter(product__id=obj.id)
        stockPriceSerializer = ProductStockPriceSerializer(stock_price_list, many=True)
        return stockPriceSerializer.data

    class Meta:
        model = Product
        fields = '__all__'

