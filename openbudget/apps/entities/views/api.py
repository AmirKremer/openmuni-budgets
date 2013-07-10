from rest_framework import generics
from openbudget.apps.international.utilities import translated_fields
from openbudget.apps.entities import serializers
from openbudget.apps.entities import models


class DomainList(generics.ListAPIView):
    """Called via an API endpoint that represents a list of domains."""

    model = models.Domain
    serializer_class = serializers.DomainBase
    ordering = ['id', 'name','created_on', 'last_modified']
    search_fields = ['name'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map()

        ### FILTERS
        has_divisions = self.request.QUERY_PARAMS.get('has_divisions', None)
        has_entities = self.request.QUERY_PARAMS.get('has_entities', None)

        # HAS_DIVISIONS: return domains that currently have divisions.
        matches = []
        if has_divisions == 'true':
            for obj in queryset:
                if obj.divisions.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        elif has_divisions == 'false':
            for obj in queryset:
                if not obj.divisions.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        # HAS_ENTITIES: return domains that currently have entities.
        matches = []
        if has_entities == 'true':
            for obj in queryset:
                if obj.entities:
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        elif has_entities == 'false':
            for obj in queryset:
                if not obj.entities:
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        return queryset


class DomainDetail(generics.RetrieveAPIView):
    """Called via an API endpoint that represents a single domain."""

    model = models.Domain
    queryset = model.objects.related_map()
    serializer_class = serializers.DomainDetail


class DivisionList(generics.ListAPIView):
    """Called via an API endpoint that represents a list of divisions."""

    model = models.Division
    serializer_class = serializers.DivisionBase
    ordering = ['id', 'name', 'created_on', 'last_modified']
    search_fields = ['name'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map()

        ### FILTERS
        budgeting = self.request.QUERY_PARAMS.get('budgeting', None)
        has_entities = self.request.QUERY_PARAMS.get('has_entities', None)
        domains = self.request.QUERY_PARAMS.get('domains', None)
        indexes = self.request.QUERY_PARAMS.get('indexes', None)

        # BUDGETING: return divisions that are budgeting, or not.
        if budgeting == 'true':
            queryset = queryset.filter(budgeting=True)
        elif budgeting == 'false':
            queryset = queryset.filter(budgeting=False)

        # HAS_ENTITIES: return divisions that currently have entities.
        matches = []
        if has_entities == 'true':
            for obj in queryset:
                if obj.entities.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        elif has_entities == 'false':
            for obj in queryset:
                if not obj.entities.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        # DOMAINS: return divisions that belong to the given domains(s).
        if domains:
            domains = domains.split(',')
            queryset = queryset.filter(domain__in=domains)

        # INDEXES: return divisions of the given index(s).
        if indexes:
            indexes = indexes.split(',')
            queryset = queryset.filter(index__in=indexes)

        return queryset


class DivisionDetail(generics.RetrieveAPIView):
    """Called via an API endpoint that represents a single division."""

    model = models.Division
    queryset = model.objects.related_map()
    serializer_class = serializers.DivisionDetail


class EntityList(generics.ListAPIView):
    """Called via an API endpoint that represents a list of entities."""

    model = models.Entity
    serializer_class = serializers.EntityBase
    ordering = ['id', 'name', 'created_on', 'last_modified']
    search_fields = ['name', 'description'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map()

        ### FILTERS
        budgeting = self.request.QUERY_PARAMS.get('budgeting', None)
        has_sheets = self.request.QUERY_PARAMS.get('has_sheets', None)
        divisions = self.request.QUERY_PARAMS.get('divisions', None)
        parents = self.request.QUERY_PARAMS.get('parents', None)

        # BUDGETING: return entities that are budgeting, or not.
        if budgeting == 'true':
            queryset = queryset.filter(division__budgeting=True)
        elif budgeting == 'false':
            queryset = queryset.filter(division__budgeting=False)

        # HAS_SHEETS: return entities that currently have sheets.
        matches = []
        if has_sheets == 'true':
            for obj in queryset:
                if obj.sheets.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        elif has_sheets == 'false':
            for obj in queryset:
                if not obj.sheets.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        # DIVISIONS: return entities that belong to the given division(s).
        if divisions:
            divisions = divisions.split(',')
            queryset = queryset.filter(division__in=divisions)

        # PARENTS: return entities that are children of given parent(s).
        if parents:
            parents = parents.split(',')
            queryset = queryset.filter(parent__in=parents)

        return queryset


class EntityDetail(generics.RetrieveAPIView):
    """Called via an API endpoint that represents a single entity."""

    model = models.Entity
    queryset = model.objects.related_map()
    serializer_class = serializers.EntityDetail
