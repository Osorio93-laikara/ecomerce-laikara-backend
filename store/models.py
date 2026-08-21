from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    description = models.TextField()

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    production_output = models.PositiveIntegerField(
        default=3800
    )

    production_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    profit_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    stock = models.IntegerField(
        default=0
    )

    image = models.ImageField(
        upload_to='products/'
    )

    def calculate_cost(self):

        total = Decimal("0.00")

        recipes = ProductionRecipe.objects.filter(
            product=self
        )

        for recipe in recipes:

            total += (
                recipe.quantity *
                recipe.material.price_per_unit
            )

        return total

    def update_cost(self):

        total_cost = Decimal("0.00")

        recipes = ProductionRecipe.objects.filter(
            product=self
        )

        for recipe in recipes:

            total_cost += (
                recipe.quantity *
                recipe.material.price_per_unit
            )

        self.production_cost = total_cost

        if self.production_output > 0:

            cost_per_unit = (
                total_cost /
                self.production_output
            )

            self.profit_per_unit = (
                self.selling_price -
                cost_per_unit
            ).quantize(
                Decimal("0.01")
            )

        else:

            self.profit_per_unit = Decimal("0.00")

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        self.update_cost()

    def __str__(self):

        return self.name
        
class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    image = models.ImageField(
        upload_to="products/gallery/"
    )


    def __str__(self):

        return self.product.name
    
class Customer(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='customer'
    )


    name = models.CharField(
        max_length=100
    )


    phone = models.CharField(
        max_length=20
    )


    address = models.TextField()



    def __str__(self):

        return self.name





class Order(models.Model):

    STATUS = (

        ('Pending','Pending'),

        ('Paid','Paid'),

        ('Shipped','Shipped'),

        ('Completed','Completed'),

        ('Cancelled','Cancelled'),

    )


    customer = models.ForeignKey(

        Customer,

        on_delete=models.CASCADE,

        related_name='orders'

    )


    total = models.DecimalField(

        max_digits=12,

        decimal_places=2

    )


    status = models.CharField(

        max_length=30,

        choices=STATUS,

        default='Pending'

    )

    note = models.TextField(
        blank=True,
        null=True
    )


    created = models.DateTimeField(

        auto_now_add=True

    )



    def __str__(self):

        return f'Order #{self.id}'





class OrderItem(models.Model):

    order = models.ForeignKey(

        Order,

        on_delete=models.CASCADE,

        related_name='items'

    )


    product = models.ForeignKey(

        Product,

        on_delete=models.CASCADE

    )


    qty = models.PositiveIntegerField()



    selling_price = models.DecimalField(

        max_digits=12,

        decimal_places=2

    )


    def subtotal(self):

        return self.qty * self.selling_price



    def __str__(self):

        return self.product.name

    def save(self, *args, **kwargs):

        if not self.selling_price:
            self.selling_price = (
                self.product.selling_price
            )

        super().save(*args, **kwargs)
    
class Material(models.Model):

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    quantity = models.IntegerField(
        default=0
    )

    unit = models.CharField(
        max_length=50
    )

    price_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    def save(self, *args, **kwargs):

        self.total_price = (
            self.quantity *
            self.price_per_unit
        )

        super().save(*args, **kwargs)

        # update semua product yang memakai material ini
        recipes = ProductionRecipe.objects.filter(
            material=self
        )

        for recipe in recipes:

            recipe.product.update_cost()



    def __str__(self):

        return self.name
    
class ProductionRecipe(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        self.product.update_cost()

    def delete(self, *args, **kwargs):

        product = self.product

        super().delete(*args, **kwargs)

        product.update_cost()

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"{self.material.name}"
        )

class Production(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    stock_added = models.BooleanField(
        default=False
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    profit_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        total = Decimal("0")

        recipes = ProductionRecipe.objects.filter(
            product=self.product
        )

        for recipe in recipes:

            material = recipe.material

            # Harga material per unit
            price = material.price_per_unit

            # Hitung kebutuhan material
            if self.product.production_output > 0:

                used = (
                    recipe.quantity *
                    self.quantity /
                    self.product.production_output
                )

            else:

                used = Decimal("0")

            # Tambah biaya material
            total += (
                used *
                price
            )

        # ======================
        # TOTAL COST
        # ======================

        self.total_cost = total

        # ======================
        # TOTAL SALES
        # ======================

        self.total_sales = (
            self.product.selling_price *
            self.quantity
        )

        # ======================
        # PROFIT
        # ======================

        self.profit = (
            self.total_sales -
            self.total_cost
        )

        # ======================
        # PROFIT PER UNIT
        # ======================

        if self.quantity > 0:

            self.profit_per_unit = (
                self.profit /
                self.quantity
            ).quantize(
                Decimal("0.01")
            )

        else:

            self.profit_per_unit = Decimal("0.00")

        super().save(*args, **kwargs)

    def __str__(self):

        return self.product.name
    
class Review(models.Model):

    RATING = (
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5')
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(
        choices=RATING
    )

    comment = models.TextField(
        blank=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = [
            'product',
            'customer'
        ]

class Wishlist(models.Model):

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        unique_together = (
            'customer',
            'product'
        )


    def __str__(self):
        return self.product.name