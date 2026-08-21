from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class MyTokenObtainPairSerializer(
    TokenObtainPairSerializer
):


    def validate(self, attrs):

        data = super().validate(attrs)


        user = self.user


        if user.is_staff:

            data['role'] = 'admin'

        else:

            data['role'] = 'customer'


        return data