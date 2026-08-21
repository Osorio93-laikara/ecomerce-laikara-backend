from rest_framework import serializers
from django.contrib.auth.models import User

from store.models import (
    Product,
    Category,
    Customer,
    Order,
    OrderItem,
    Material,
    ProductionRecipe,
    Production,
    Review,
    Wishlist,
    ProductImage
)


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:

        model = ProductImage

        fields = [
            "id",
            "product",
            "image"
        ]

# ======================
# PRODUCT
# ======================

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    images = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    wishlist_id = serializers.SerializerMethodField()

    class Meta:

        model = Product

        fields = [
            *[field.name for field in Product._meta.fields],
            'category_name',
            'images',
            'favorite',
            'wishlist_id'
        ]



    def get_favorite(self,obj):

        request=self.context.get('request')

        if request.user.is_authenticated:

            return Wishlist.objects.filter(
                customer=request.user,
                product=obj
            ).exists()

        return False



    def get_wishlist_id(self,obj):

        request=self.context.get('request')

        if request.user.is_authenticated:

            wishlist=Wishlist.objects.filter(
                customer=request.user,
                product=obj
            ).first()

            if wishlist:
                return wishlist.id

        return None
    
    def get_images(self,obj):

        request = self.context.get(
            "request"
        )


        return [
            request.build_absolute_uri(
                img.image.url
            )
            for img in obj.images.all()
        ]



# ======================
# CATEGORY
# ======================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:

        model = Category

        fields = "__all__"





# ======================
# CUSTOMER
# ======================

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:

        model = Customer

        fields = "__all__"


# ======================
# ORDER ITEM
# ======================

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product',
            'product_name',
            'qty'
        ]


# ======================
# ORDER
# ======================

class OrderSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True
    )

    total_items = serializers.SerializerMethodField()

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'customer_name',
            'total',
            'status',
            'note',
            'created',
            'total_items',
            'items'
        ]

        read_only_fields = [
            'customer',
            'created'
        ]

    def get_total_items(self, obj):
        return sum(
            item.qty 
            for item in obj.items.all()
        )



# ======================
# REGISTER CUSTOMER
# ======================

class RegisterSerializer(serializers.ModelSerializer):


    username = serializers.CharField(
        write_only=True
    )


    password = serializers.CharField(
        write_only=True
    )



    class Meta:

        model = Customer


        fields = [

            'username',

            'password',

            'name',

            'phone',

            'address'

        ]




    def create(self, validated_data):


        username = validated_data.pop(
            'username'
        )


        password = validated_data.pop(
            'password'
        )


        user = User.objects.create_user(

            username=username,

            password=password

        )



        customer = Customer.objects.create(

            user=user,

            **validated_data

        )


        return customer





# ======================
# PROFILE
# ======================

class ProfileSerializer(serializers.ModelSerializer):


    username = serializers.CharField(

        source='user.username',

        read_only=True

    )



    class Meta:

        model = Customer


        fields = [

            'username',

            'name',

            'phone',

            'address'

        ]

class MaterialSerializer(serializers.ModelSerializer):

    class Meta:

        model = Material

        fields="__all__"



class ProductionRecipeSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )


    material_name = serializers.CharField(
        source='material.name',
        read_only=True
    )


    unit = serializers.CharField(
        source='material.unit',
        read_only=True
    )


    class Meta:

        model = ProductionRecipe

        fields = [
            'id',
            'product',
            'product_name',
            'material',
            'material_name',
            'quantity',
            'unit'
        ]


class ProductionSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = Production
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'total_cost',
            'total_sales',
            'profit',
            'profit_per_unit',
            'stock_added',
            'created'
        ]

class ReviewSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True
    )


    class Meta:

        model = Review

        fields = [
            'id',
            'product',
            'customer_name',
            'rating',
            'comment',
            'created'
        ]

        read_only_fields = [
            'customer_name',
            'created'
        ]


class WishlistSerializer(serializers.ModelSerializer):

    class Meta:

        model = Wishlist

        fields = [
            'id',
            'product',
            'customer',
            'created'
        ]

        read_only_fields = [
            'customer'
        ]