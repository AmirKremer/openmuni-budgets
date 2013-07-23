from rest_framework import serializers
from openbudget.apps.accounts import models


class AccountBaseSerializer(serializers.HyperlinkedModelSerializer):
    """Base Account serializer, exposing our defaults for accounts."""

    class Meta:
        model = models.Account
        fields = ['url', 'id', 'uuid', 'first_name', 'last_name', 'username',
                  'date_joined', 'email']


class AccountMin(serializers.ModelSerializer):
    """A minimal serializer for use as a nested entity representation."""

    avatar = serializers.Field(source='get_avatar')

    class Meta:
        model = models.Account
        fields = ['id', 'first_name', 'last_name', 'avatar']
