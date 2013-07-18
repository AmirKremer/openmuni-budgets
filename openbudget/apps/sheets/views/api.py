from rest_framework import generics
from rest_framework.response import Response
from openbudget.apps.international.utilities import translated_fields
from openbudget.apps.sheets import serializers
from openbudget.apps.sheets import models


class TemplateList(generics.ListAPIView):
    """API endpoint that represents a list of templates."""

    model = models.Template
    serializer_class = serializers.TemplateBase
    ordering = ['id', 'name', 'period_start', 'created_on', 'last_modified']
    search_fields = ['name', 'description'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map_min()

        ### FILTERS
        domains = self.request.QUERY_PARAMS.get('domains', None)
        divisions = self.request.QUERY_PARAMS.get('divisions', None)
        entities = self.request.QUERY_PARAMS.get('entities', None)

        # DOMAINS: return templates used in the given domain(s).
        if domains:
            domains = domains.split(',')
            queryset = queryset.filter(divisions__domain__in=domains).distinct()

        # DIVISIONS: return templates used in the given division(s).
        if divisions:
            divisions = divisions.split(',')
            queryset = queryset.filter(divisions__in=divisions)

        # ENTITIES: return templates used by the given entity(-ies).
        if entities:
            entities = entities.split(',')
            queryset = queryset.filter(using_sheets__entity__in=entities)

        # DEFAULT: We just want to return "official" templates, unless a
        # specific filter requires otherwise
        if not self.request.QUERY_PARAMS:
            queryset = queryset.exclude(divisions=None)

        return queryset


class TemplateDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single template."""

    model = models.Template
    queryset = model.objects.related_map()
    serializer_class = serializers.TemplateDetail


class TemplateNodeList(generics.ListAPIView):
    """API endpoint that represents a list of template nodes."""

    model = models.TemplateNode
    serializer_class = serializers.TemplateNodeBase
    ordering = ['id', 'name', 'description', 'created_on', 'last_modified']
    search_fields = ['name', 'description'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map_min()

        ### FILTERS
        templates = self.request.QUERY_PARAMS.get('templates', None)
        entities = self.request.QUERY_PARAMS.get('entities', None)
        parents = self.request.QUERY_PARAMS.get('parents', None)

        # for latest query only:
        entity = self.request.QUERY_PARAMS.get('entity', None)
        latest = self.request.QUERY_PARAMS.get('latest', None)

        # TEMPLATES: return template nodes used in the given template(s).
        if templates:
            templates = templates.split(',')
            queryset = queryset.filter(templates__in=templates)

        # ENTITIES: return template nodes of templates used by the given entity(-ies).
        if entities:
            entities = entities.split(',')
            queryset = queryset.filter(using_sheets__entity__in=entities)

        # PARENTS: return nodes that are children of given parent(s).
        if parents and parents == 'none':
            queryset = queryset.filter(parent__isnull=True)

        elif parents:
            parents = parents.split(',')
            queryset = queryset.filter(parent__in=parents)

        # Check about this
        # was implemented for timeline. Have a feeling we can do it more
        # efficiently elsewhere.
        if entity is not None:
            if latest:
                queryset = models.Template.objects.latest_of(entity=entity).nodes
            else:
                pass

        return queryset


class TemplateNodeDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single template node."""

    model = models.TemplateNode
    queryset = model.objects.related_map()
    serializer_class = serializers.TemplateNodeBase


class SheetList(generics.ListAPIView):
    """API endpoint that represents a list of budget sheets."""

    model = models.Sheet
    serializer_class = serializers.SheetBase
    ordering = ['id', 'entity__name', 'period_start', 'created_on', 'last_modified']
    search_fields = ['entity__name', 'description', 'period_start',
                     'period_end'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map_min()

        ### FILTERS
        entities = self.request.QUERY_PARAMS.get('entities', None)
        divisions = self.request.QUERY_PARAMS.get('divisions', None)
        templates = self.request.QUERY_PARAMS.get('templates', None)
        budget_gt = self.request.QUERY_PARAMS.get('budget_gt', None)
        budget_gte = self.request.QUERY_PARAMS.get('budget_gte', None)
        budget_lt = self.request.QUERY_PARAMS.get('budget_gt', None)
        budget_lte = self.request.QUERY_PARAMS.get('budget_gte', None)
        actual_gt = self.request.QUERY_PARAMS.get('actual_gt', None)
        actual_gte = self.request.QUERY_PARAMS.get('actual_gte', None)
        actual_lt = self.request.QUERY_PARAMS.get('actual_gt', None)
        actual_lte = self.request.QUERY_PARAMS.get('actual_gte', None)

        # ENTITIES: return sheets that belong to the given entity(-ies).
        if entities:
            entities = entities.split(',')
            queryset = queryset.filter(entity__in=entities)

        # DIVISIONS: return sheets that are under the given division(s).
        if divisions:
            divisions = divisions.split(',')
            queryset = queryset.filter(entity__division_id__in=divisions)

        # TEMPLATES: return sheets that use the given template(s).
        if templates:
            templates = templates.split(',')
            queryset = queryset.filter(template__in=templates)

        # BUDGET_GT: return sheet items with a budget amount greater than the
        # given amount.
        #if budget_gt:
        #    queryset = queryset.filter(budget__gt=budget_gt)

        # BUDGET_LT: return sheet items with a budget amount less than the
        # given amount.
        #if budget_lt:
        #    queryset = queryset.filter(budget__lt=budget_lt)

        # BUDGET_GTE: return sheets with a budget amount greater than or
        # equal to the given amount.
        #if budget_gte:
        #    queryset = queryset.filter(budget__gte=budget_gte)

        # BUDGET_LTE: return sheets with a budget amount less than or
        # equal to the given amount.
        #if budget_lte:
        #    queryset = queryset.filter(budget__lte=budget_lte)

        # ACTUAL_GT: return sheets with an actual amount greater than the
        # given amount.
        #if actual_gt:
        #    queryset = queryset.filter(actual__gt=actual_gt)

        # ACTUAL_LT: return sheets with an actual amount less than the
        # given amount.
        #if actual_lt:
        #    queryset = queryset.filter(budget__lt=actual_lt)

        # ACTUAL_GTE: return sheets with an actual amount greater than or
        # equal to the given amount.
        #if actual_gte:
        #    queryset = queryset.filter(budget__gte=actual_gte)

        # ACTUAL_LTE: return sheets with an actual amount less than or
        # equal to the given amount.
        #if actual_lte:
        #    queryset = queryset.filter(budget__lte=actual_lte)

        return queryset


class SheetDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single budget."""

    model = models.Sheet
    queryset = model.objects.related_map()
    serializer_class = serializers.SheetDetail


class SheetItemList(generics.ListAPIView):
    """API endpoint that represents a list of budget items."""

    model = models.SheetItem
    serializer_class = serializers.SheetItemBase
    ordering = ['id', 'sheet__entity__name', 'node__code', 'created_on',
                'last_modified']
    search_fields = ['sheet__entity__name', 'node__code', 'node__name',
                     'description'] + translated_fields(model)

    def get_queryset(self):
        queryset = self.model.objects.related_map()

        ### FILTERS
        has_discussion = self.request.QUERY_PARAMS.get('has_discussion', None)
        sheets = self.request.QUERY_PARAMS.get('sheets', None)
        entities = self.request.QUERY_PARAMS.get('entities', None)
        divisions = self.request.QUERY_PARAMS.get('divisions', None)
        parents = self.request.QUERY_PARAMS.get('parents', None)
        direction = self.request.QUERY_PARAMS.get('direction', None)
        codes = self.request.QUERY_PARAMS.get('codes', None)
        budget_gt = self.request.QUERY_PARAMS.get('budget_gt', None)
        budget_gte = self.request.QUERY_PARAMS.get('budget_gte', None)
        budget_lt = self.request.QUERY_PARAMS.get('budget_lt', None)
        budget_lte = self.request.QUERY_PARAMS.get('budget_lte', None)
        actual_gt = self.request.QUERY_PARAMS.get('actual_gt', None)
        actual_gte = self.request.QUERY_PARAMS.get('actual_gte', None)
        actual_lt = self.request.QUERY_PARAMS.get('actual_lt', None)
        actual_lte = self.request.QUERY_PARAMS.get('actual_lte', None)

        # HAS_DISCUSSION: return sheet items that have user discussion.
        matches = []
        if has_discussion == 'true':
            for obj in queryset:
                if obj.discussion.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        elif has_discussion == 'false':
            for obj in queryset:
                if not obj.discussion.all():
                    matches.append(obj.pk)
            queryset = queryset.filter(pk__in=matches)

        # SHEETS: return sheets that belong to the given entity(-ies).
        if sheets:
            sheets = sheets.split(',')
            queryset = queryset.filter(sheet__in=sheets)

        # ENTITIES: return sheet items that belong to the given entity(-ies).
        if entities:
            entities = entities.split(',')
            queryset = queryset.filter(sheet__entity__in=entities)

        # DIVISIONS: return sheet items that are under the given division(s).
        if divisions:
            divisions = divisions.split(',')
            queryset = queryset.filter(sheet__entity__division_id__in=divisions)

        # DIRECTION: return sheet items in the given direction.
        if direction:
            direction = direction.upper()
            queryset = queryset.filter(node__direction=direction)

        # CODES: return sheet items that match the given code(s).
        if codes:
            codes = codes.split(',')
            queryset = queryset.filter(node__code__in=codes)

        # PARENTS: return items that are children of given parent(s).
        if parents and parents == 'none':
            queryset = queryset.filter(node__parent__isnull=True)

        elif parents:
            parents = parents.split(',')
            queryset = queryset.filter(node__parent__code__in=parents)

        # BUDGET_GT: return sheet items with a budget amount greater than the
        # given amount.
        if budget_gt:
            queryset = queryset.filter(budget__gt=budget_gt)

        # BUDGET_LT: return sheet items with a budget amount less than the
        # given amount.
        if budget_lt:
            queryset = queryset.filter(budget__lt=budget_lt)

        # BUDGET_GTE: return sheet items with a budget amount greater than or
        # equal to the given amount.
        if budget_gte:
            queryset = queryset.filter(budget__gte=budget_gte)

        # BUDGET_LTE: return sheet items with a budget amount less than or
        # equal to the given amount.
        if budget_lte:
            queryset = queryset.filter(budget__lte=budget_lte)

        # ACTUAL_GT: return sheet items with an actual amount greater than the
        # given amount.
        if actual_gt:
            queryset = queryset.filter(actual__gt=actual_gt)

        # ACTUAL_LT: return sheet items with an actual amount less than the
        # given amount.
        if actual_lt:
            queryset = queryset.filter(budget__lt=actual_lt)

        # ACTUAL_GTE: return sheet items with an actual amount greater than or
        # equal to the given amount.
        if actual_gte:
            queryset = queryset.filter(budget__gte=actual_gte)

        # ACTUAL_LTE: return sheet items with an actual amount less than or
        # equal to the given amount.
        if actual_lte:
            queryset = queryset.filter(budget__lte=actual_lte)

        return queryset


class SheetItemDetail(generics.RetrieveAPIView):
    """API endpoint that represents a single budget item."""

    model = models.DenormalizedSheetItem
    queryset = model.objects.related_map()
    serializer_class = serializers.SheetItemBase


class SheetItemTimeline(generics.ListAPIView):
    """API endpoint that retrieves a timeline of sheet items.

    The timeline is created according to the given entity, node(s)
    """

    def get(self, request, entity_pk, *args, **kwargs):
        """GET handler for retrieving all budget items and actual items of the node's timeline, filtered by entity"""

        nodes = self.request.QUERY_PARAMS.get('nodes', None)
        if nodes:
            nodes = [int(node_id) for node_id in nodes.split(',')]
        else:
            # Provide a sensible default.
            # If there is no node query param, let's return the top level nodes,
            # as used in the latest Sheet.
            print 'HERE'
            print models.Sheet.objects.latest_of(entity_pk).sheetitems
            #nodes = [for models.Sheet.objects.latest_of(entity_pk).shee]
            #TODO: handle case of no nodes specified
            pass
        items = models.SheetItem.objects.timeline(nodes, entity_pk)

        serialized_timeline = serializers.SheetTimeline(items, many=True).data

        return Response(serialized_timeline)
