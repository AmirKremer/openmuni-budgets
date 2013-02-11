from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from omuni.api.serializers import GeoPoliticalEntitySerializer, BudgetSerializer, BudgetItemSerializer
from omuni.govts.models import GeoPoliticalEntity
from omuni.budgets.models import Budget, BudgetItem


@api_view(['GET'])
def api_root(request, format=None):
    """The entry endpoint of our API."""

    return Response({
        'geopols': reverse('geopolitcalentity-list', request=request),
        'budgets': reverse('budget-list', request=request),
    })


class GeoPoliticalEntityList(generics.ListAPIView):
    """API endpoint that represents a list of geopols."""

    model = GeoPoliticalEntity
    serializer_class = GeoPoliticalEntitySerializer


class GeoPoliticalEntityDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single geopol."""

    model = GeoPoliticalEntity
    serializer_class = GeoPoliticalEntitySerializer


class BudgetList(generics.ListAPIView):
    """API endpoint that represents a list of budgets."""

    model = Budget
    serializer_class = BudgetSerializer


class BudgetDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single budget."""

    model = Budget
    serializer_class = BudgetSerializer


class BudgetItemList(generics.ListAPIView):
    """API endpoint that represents a list of bitems."""

    model = BudgetItem
    serializer_class = BudgetItemSerializer


class BudgetItemDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single bitem."""

    model = BudgetItem
    serializer_class = BudgetItemSerializer
