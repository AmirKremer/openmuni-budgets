from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from openbudget.api import serializers
from openbudget.apps.entities.models import Entity, Domain, DomainDivision
from openbudget.apps.budgets.models import BudgetTemplate, BudgetTemplateNode, Budget, BudgetItem, Actual, ActualItem


@api_view(['GET'])
def api_root(request, format=None):
    """The entry endpoint of our API"""

    return Response({
        'entities': reverse('entity-list', request=request),
        'budgets': reverse('budget-list', request=request),
        'actuals': reverse('actual-list', request=request),
    })


class EntityList(generics.ListAPIView):
    """API endpoint that represents a list of geopols"""

    model = Entity
    serializer_class = serializers.EntityLinked


class EntityDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single geopol"""

    model = Entity
    serializer_class = serializers.EntityLinked


class DomainList(generics.ListAPIView):
    """API endpoint that represents a list of domains"""

    model = Domain
    serializer_class = serializers.DomainLinked


class DomainDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single domain"""

    model = Domain
    serializer_class = serializers.DomainLinked


class DomainDivisionList(generics.ListAPIView):
    """API endpoint that represents a list of domain divisions"""

    model = DomainDivision
    serializer_class = serializers.DomainDivisionLinked


class DomainDivisionDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single domain division"""

    model = DomainDivision
    serializer_class = serializers.DomainDivisionLinked


class BudgetTemplateDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single budget template"""

    model = BudgetTemplate
    serializer_class = serializers.BudgetTemplateLinked


class BudgetTemplateNodeDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single budget template node"""

    model = BudgetTemplateNode
    serializer_class = serializers.BudgetTemplateNodeLinked


class BudgetList(generics.ListAPIView):
    """API endpoint that represents a list of budgets"""

    model = Budget
    serializer_class = serializers.BudgetLinked


class BudgetDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single budget"""

    model = Budget
    serializer_class = serializers.BudgetLinked


class BudgetItemList(generics.ListAPIView):
    """API endpoint that represents a list of bitems"""

    model = BudgetItem
    serializer_class = serializers.BudgetItemLinked


class BudgetItemDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single bitem"""

    model = BudgetItem
    serializer_class = serializers.BudgetItemLinked


class ActualList(generics.ListAPIView):
    """API endpoint that represents a list of actuals"""

    model = Actual
    serializer_class = serializers.ActualLinked


class ActualDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single actual"""

    model = Actual
    serializer_class = serializers.ActualLinked


class ActualItemList(generics.ListAPIView):
    """API endpoint that represents a list of actual items"""

    model = ActualItem
    serializer_class = serializers.ActualItemLinked


class ActualItemDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single actual item"""

    model = ActualItem
    serializer_class = serializers.ActualItemLinked
