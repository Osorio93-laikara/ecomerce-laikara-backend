from rest_framework import serializers, viewsets

from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView
)

from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)
from .permissions import IsAdminOrReadOnly, IsAdminOnly


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


from .serializers import (

    ProductSerializer,
    CategorySerializer,
    CustomerSerializer,
    OrderSerializer,
    OrderItemSerializer,
    RegisterSerializer,
    ProfileSerializer,
    MaterialSerializer,
    ProductionRecipeSerializer,
    ProductionSerializer,
    ReviewSerializer,
    WishlistSerializer,
    ProductImageSerializer

)


from rest_framework_simplejwt.views import TokenObtainPairView

from .authentication import MyTokenObtainPairSerializer

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from rest_framework.decorators import action
from rest_framework.parsers import (
    MultiPartParser,
    FormParser
)


class ProductImageViewSet(viewsets.ModelViewSet):

    queryset = ProductImage.objects.all()

    serializer_class = ProductImageSerializer

    permission_classes = [
        IsAdminOnly
    ]

# ======================
# PRODUCT
# ======================

class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    permission_classes = [
        IsAdminOrReadOnly
    ]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]





# ======================
# CATEGORY
# ======================

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer

    permission_classes=[
        IsAdminOrReadOnly
    ]




# ======================
# CUSTOMER
# ======================

class CustomerViewSet(viewsets.ModelViewSet):

    queryset = Customer.objects.all()

    serializer_class = CustomerSerializer

    permission_classes = [
        IsAdminOnly
    ]

    def update(self, request, *args, **kwargs):

        if not request.user.is_staff:

            return Response(
                {
                    "error":
                    "Customer tidak boleh edit order"
                },
                status=403
            )

        return super().update(
            request,
            *args,
            **kwargs
        )



    def destroy(self, request, *args, **kwargs):

        if not request.user.is_staff:

            return Response(
                {
                    "error":
                    "Customer tidak boleh hapus order"
                },
                status=403
            )


        return super().destroy(
            request,
            *args,
            **kwargs
        )

# ======================
# ORDER
# ======================

class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all()

    serializer_class = OrderSerializer

    permission_classes = [
        IsAuthenticated
    ]


    def get_queryset(self):

        user = self.request.user


        # ADMIN LIHAT SEMUA ORDER

        if user.is_staff:

            return Order.objects.all()



        # CUSTOMER LIHAT ORDER SENDIRI

        customer = Customer.objects.filter(
            user=user
        ).first()


        if customer:

            return Order.objects.filter(
                customer=customer
            )


        return Order.objects.none()



    def perform_create(self, serializer):

        user = self.request.user


        # ADMIN

        if user.is_staff:

            serializer.save()

            return



        # CUSTOMER

        customer = Customer.objects.get(
            user=user
        )


        serializer.save(
            customer=customer
        )

    def update(self, request, *args, **kwargs):

        if not request.user.is_staff:

            return Response(
                {
                    "error":
                    "Customer tidak boleh edit order"
                },
                status=403
            )

        return super().update(
            request,
            *args,
            **kwargs
        )



    def destroy(self, request, *args, **kwargs):

        if not request.user.is_staff:

            return Response(
                {
                    "error":
                    "Customer tidak boleh hapus order"
                },
                status=403
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )

# ======================
# ORDER ITEM
# ======================

class OrderItemViewSet(viewsets.ModelViewSet):

    queryset = OrderItem.objects.all()

    serializer_class = OrderItemSerializer

    permission_classes = [
        IsAuthenticated
    ]


    def perform_create(self, serializer):

        order_item = serializer.save()


        product = order_item.product


        # kurangi stock

        if product.stock >= order_item.qty:

            product.stock -= order_item.qty

            product.save()


        else:

            raise Exception(
                "Stock product tidak cukup"
            )




# ======================
# REGISTER CUSTOMER
# ======================

class RegisterView(CreateAPIView):

    serializer_class = RegisterSerializer

    permission_classes = [
        AllowAny
    ]







# ======================
# PROFILE CUSTOMER
# ======================

class ProfileView(RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer

    permission_classes = [
        IsAuthenticated
    ]



    def get_object(self):


        customer = Customer.objects.filter(

            user=self.request.user

        ).first()



        if customer:


            return customer




        return Customer.objects.create(

            user=self.request.user,

            name=self.request.user.username,

            phone='',

            address=''

        )



# ======================
# LOGIN JWT CUSTOM
# ======================

class MyTokenObtainPairView(TokenObtainPairView):

    serializer_class = MyTokenObtainPairSerializer

# ======================
# DASHBOARD STATISTIC
# ======================

class DashboardStatisticView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user = request.user

        # ==========================
        # ADMIN / CUSTOMER
        # ==========================

        if user.is_staff:

            orders = Order.objects.all()

        else:

            customer = Customer.objects.filter(
                user=user
            ).first()

            if customer:

                orders = Order.objects.filter(
                    customer=customer
                )

            else:

                orders = Order.objects.none()

        # ==========================
        # AMBIL DATA DARI DATABASE
        # ==========================

        statistic = (

            orders

            .annotate(
                month=TruncMonth("created")
            )

            .values("month")

            .annotate(

                orders=Count("id"),

                income=Sum("total")

            )

            .order_by("month")

        )

        # ==========================
        # UBAH MENJADI DICTIONARY
        # ==========================

        data = {}

        for item in statistic:

            key = item["month"].strftime("%Y-%m")

            data[key] = {

                "orders": item["orders"],

                "income": float(item["income"] or 0)

            }

        # ==========================
        # 12 BULAN TERAKHIR
        # ==========================

        today = date.today()

        first_month = today.replace(day=1) - relativedelta(months=11)

        result = []

        current = first_month

        while current <= today.replace(day=1):

            key = current.strftime("%Y-%m")

            result.append({

                "month": current.strftime("%B %Y"),

                "orders": data.get(
                    key,
                    {}
                ).get("orders", 0),

                "income": data.get(
                    key,
                    {}
                ).get("income", 0)

            })

            current = current + relativedelta(months=1)

        return Response(result)
    
# ======================
# DASHBOARD INSIGHT
# ======================

class DashboardInsightView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(self, request):

        user = request.user


        if user.is_staff:

            orders = Order.objects.all()

        else:

            customer = Customer.objects.filter(
                user=user
            ).first()


            if customer:

                orders = Order.objects.filter(
                    customer=customer
                )

            else:

                orders = Order.objects.none()



        # ======================
        # TOTAL REVENUE
        # ======================

        total_revenue = orders.aggregate(

            total=Sum("total")

        )["total"] or 0



        # ======================
        # BULAN INI
        # ======================

        today = date.today()


        current_month = orders.filter(

            created__year=today.year,

            created__month=today.month

        ).aggregate(

            total=Sum("total")

        )["total"] or 0




        # ======================
        # BULAN LALU
        # ======================


        last_month = today.replace(day=1) - relativedelta(months=1)


        previous_month = orders.filter(

            created__year=last_month.year,

            created__month=last_month.month

        ).aggregate(

            total=Sum("total")

        )["total"] or 0




        # ======================
        # GROWTH
        # ======================


        if previous_month > 0:

            growth = (

                (
                    float(current_month)
                    -
                    float(previous_month)
                )

                /

                float(previous_month)

            ) * 100


        else:

            growth = 0




        return Response({

            "revenue_growth":
                round(growth,2),


            "total_revenue":
                float(total_revenue),


            "customer_total":
                Customer.objects.count(),


            "product_total":
                Product.objects.count()

        })
    
class MaterialViewSet(viewsets.ModelViewSet):

    queryset = Material.objects.all()

    serializer_class = MaterialSerializer

    permission_classes=[
        IsAdminOnly
    ]



class ProductionRecipeViewSet(viewsets.ModelViewSet):

    queryset = ProductionRecipe.objects.all()

    serializer_class = ProductionRecipeSerializer

    permission_classes=[
        IsAdminOnly
    ]



class ProductionViewSet(viewsets.ModelViewSet):

    queryset = Production.objects.all()

    serializer_class = ProductionSerializer

    permission_classes=[
        IsAdminOnly
    ]


    def perform_create(self, serializer):


        product = serializer.validated_data['product']

        quantity = serializer.validated_data['quantity']


        total_cost = Decimal(0)



        recipes = ProductionRecipe.objects.filter(
            product=product
        )



        for recipe in recipes:


            material = recipe.material


            used_quantity = (
                recipe.quantity *
                quantity /
                product.production_output
            )


            unit_price = material.price_per_unit


            cost = (
                used_quantity *
                unit_price
            )


            total_cost += cost



            # cek stok dulu
            if material.quantity < used_quantity:

                raise Exception(
                    f"Stock {material.name} tidak cukup"
                )



            material.quantity -= used_quantity

            material.save()


        serializer.save(
            total_cost=total_cost
        )
    
    def perform_update(self, serializer):

        old = self.get_object()

        # ======================
        # KEMBALIKAN STOK LAMA
        # ======================

        old_recipes = ProductionRecipe.objects.filter(
            product=old.product
        )

        for recipe in old_recipes:

            material = recipe.material

            used = (
                recipe.quantity *
                old.quantity /
                old.product.production_output
            )

            material.quantity += used
            material.save()

        # ======================
        # DATA BARU
        # ======================

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        recipes = ProductionRecipe.objects.filter(
            product=product
        )

        # ======================
        # CEK STOK
        # ======================

        for recipe in recipes:

            material = recipe.material

            used = (
                recipe.quantity *
                quantity /
                product.production_output
            )

            if material.quantity < used:

                raise Exception(
                    f"Stock {material.name} tidak cukup"
                )

        # ======================
        # KURANGI STOK BARU
        # ======================

        for recipe in recipes:

            material = recipe.material

            used = (
                recipe.quantity *
                quantity /
                product.production_output
            )

            material.quantity -= used
            material.save()

        serializer.save()

    def perform_destroy(self, instance):

        recipes = ProductionRecipe.objects.filter(
            product=instance.product
        )

        for recipe in recipes:

            material = recipe.material

            used = (
                recipe.quantity *
                instance.quantity /
                instance.product.production_output
            )

            material.quantity += used
            material.save()

        instance.delete()

    @action(
        detail=True,
        methods=['post']
    )
    def move_to_stock(
        self,
        request,
        pk=None
    ):

        production = self.get_object()

        if production.stock_added:

            return Response({
                "message":
                "Stock sudah ditambahkan"
            })

        product = production.product

        # tambah stock product
        product.stock += production.quantity
        product.save()

        # tandai sudah masuk stock
        production.stock_added = True
        production.save()

        return Response({
            "message":
            "Stock berhasil ditambahkan"
        })

class ProductionCalculateView(APIView):
    permission_classes=[
        IsAdminOnly
    ]

    def post(self, request):

        product_id = request.data.get("product")

        production_qty = Decimal(
            str(request.data.get("quantity", 0))
        )


        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error":"Product tidak ditemukan"
                },
                status=404
            )


        recipes = ProductionRecipe.objects.filter(
            product=product
        )


        total_cost = Decimal("0")


        materials = []


        for recipe in recipes:


            material = recipe.material


            # jumlah kebutuhan untuk 1 batch
            recipe_qty = recipe.quantity


            # kebutuhan sesuai jumlah produksi
            used_qty = (
                recipe_qty *
                production_qty /
                product.production_output
            )


            unit_price = material.price_per_unit


            cost = (
                used_qty *
                unit_price
            )


            total_cost += cost


            materials.append({

                "material": material.name,

                "used": float(used_qty),

                "unit": material.unit,

                "cost": float(cost)

            })



        selling_price = product.selling_price


        total_sales = (
            selling_price *
            production_qty
        )


        profit = (
            total_sales -
            total_cost
        )



        if production_qty > 0:


            profit_per_piece = (
                profit /
                production_qty
            )


            cost_per_piece = (
                total_cost /
                production_qty
            )


        else:

            profit_per_piece = Decimal("0")

            cost_per_piece = Decimal("0")



        return Response({

            "product": product.name,

            "quantity": float(production_qty),

            "selling_price": float(selling_price),

            "total_cost": float(total_cost),

            "sale_total": float(total_sales),

            "profit": float(profit),

            "profit_per_piece": float(profit_per_piece),

            "cost_per_piece": float(cost_per_piece),

            "materials": materials

        })
    

class ReviewViewSet(viewsets.ModelViewSet):

    queryset = Review.objects.all()

    serializer_class = ReviewSerializer


    def get_queryset(self):

        queryset = Review.objects.all()

        product = self.request.query_params.get(
            "product"
        )

        if product:
            queryset = queryset.filter(
                product_id=product
            )

        return queryset


    def perform_create(self, serializer):

        customer = Customer.objects.get(
            user=self.request.user
        )

        product = serializer.validated_data["product"]


        # Cek apakah customer sudah review produk ini
        if Review.objects.filter(
            product=product,
            customer=customer
        ).exists():

            raise serializers.ValidationError(
                {
                    "error":
                    "Anda sudah memberikan review untuk produk ini."
                }
            )


        serializer.save(
            customer=customer
        )


    def perform_update(self, serializer):

        # Edit rating/comment saja
        serializer.save()

    @action(
        detail=False,
        methods=['get'],
        url_path='my-review'
    )
    def my_review(self, request):

        if not request.user.is_authenticated:
            return Response({})


        try:

            customer = Customer.objects.get(
                user=request.user
            )

        except Customer.DoesNotExist:

            return Response({})


        product = request.query_params.get(
            "product"
        )


        review = Review.objects.filter(
            customer=customer,
            product_id=product
        ).first()


        if review:

            serializer = self.get_serializer(
                review
            )

            return Response(
                serializer.data
            )


        return Response({})
    
class WishlistViewSet(viewsets.ModelViewSet):

    queryset = Wishlist.objects.all()

    serializer_class = WishlistSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return Wishlist.objects.filter(
            customer=self.request.user
        )

    def perform_create(self, serializer):

        serializer.save(
            customer=self.request.user
        )