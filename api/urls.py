from django.urls import include, path

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenRefreshView
)


from .views import (

    ProductViewSet,

    CategoryViewSet,

    CustomerViewSet,

    OrderViewSet,

    OrderItemViewSet,

    RegisterView,

    ProfileView,

    MyTokenObtainPairView,

    DashboardStatisticView,

    DashboardInsightView,

    MaterialViewSet,
    ProductionRecipeViewSet,
    ProductionViewSet,

    ProductionCalculateView,
    ReviewViewSet,
    WishlistViewSet,
    ProductImageViewSet

)



router = DefaultRouter()



router.register(
    r"products",
    ProductViewSet
)

router.register(
    "product-images",
    ProductImageViewSet
)

router.register(
    r"categories",
    CategoryViewSet
)


router.register(
    r"customers",
    CustomerViewSet
)

router.register(
    r"orders",
    OrderViewSet
)

router.register(
    r"order-items",
    OrderItemViewSet
)

router.register(
    r"materials",
    MaterialViewSet
)


router.register(
    r"production-recipe",
    ProductionRecipeViewSet
)


router.register(
    r"production",
    ProductionViewSet
)


router.register(
    r'reviews',
    ReviewViewSet,
    basename='reviews'
)

router.register(
    'wishlist',
    WishlistViewSet,
    basename='wishlist'
)


urlpatterns = [


    path(
        "",
        include(router.urls)
    ),



    path(
        "register/",
        RegisterView.as_view()
    ),



    path(
        "login/",
        MyTokenObtainPairView.as_view()
    ),



    path(
        "refresh/",
        TokenRefreshView.as_view()
    ),



    path(
        "profile/",
        ProfileView.as_view()
    ),

    path(
        "dashboard/statistic/",
        DashboardStatisticView.as_view()
    ),

    path(
        "dashboard/insight/",
        DashboardInsightView.as_view()
    ),

    path(
        "calculate-production/",
        ProductionCalculateView.as_view()
    ),


]