from rest_framework import serializers

from account.serializers import UserSerializer

from .models import Payment, PaymentNotification


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class PaymentNotificationSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    class Meta:
        model= PaymentNotification
        fields = "__all__"