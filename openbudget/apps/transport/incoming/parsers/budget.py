from copy import deepcopy
from openbudget.apps.budgets.models import BudgetTemplate, Budget, BudgetItem
from openbudget.apps.entities.models import Entity
from openbudget.apps.transport.incoming.parsers import register
from openbudget.apps.transport.incoming.parsers.budgettemplate import BudgetTemplateParser
from openbudget.apps.transport.incoming.errors import MetaParsingError, NodeNotFoundError


class BudgetParser(BudgetTemplateParser):

    container_model = Budget
    item_model = BudgetItem
    ITEM_ATTRIBUTES = ('amount', 'node', 'description', 'budget')
    ITEM_CLEANING_EXCLUDE = ['node', 'budget']

    def __init__(self, container_object_dict):
        super(BudgetTemplateParser, self).__init__(container_object_dict)
        self.template_parser = self._init_template_parser()

    @classmethod
    def resolve(cls, deferred):
        container_dict = deferred['container']

        if not container_dict:
            raise Exception('Deferred object missing container dict: %s' % container_dict)

        instance = cls(container_dict)
        instance.objects_lookup = deferred['items']

        instance.template_parser.objects_lookup = deferred['template_parser']['items']

        return instance

    def validate(self, data, keep_cache=False):
        if self.template_parser:
            template_valid, template_errors = self.template_parser.validate(data=deepcopy(data), keep_cache=True)
        else:
            template_valid = False
            template_errors = []

        valid, budget_errors = super(BudgetParser, self).validate(data)

        if self.template_parser:
            self.template_parser._clear_cache()

        return template_valid and valid, budget_errors + template_errors

    def save(self, dry=False):
        template_saved = True

        if not dry:
            template_saved = self.template_parser.save()

        if template_saved:
            return super(BudgetParser, self).save(dry)

        return False

    def deferred(self):
        deferred = super(BudgetParser, self).deferred()
        deferred['template_parser'] = self.template_parser.deferred()
        return deferred

    def _save_item(self, obj, key, is_node=False):
        # check if we already saved this object and have it in cache
        if key in self.saved_cache:
            return self.saved_cache[key]

        self._add_to_container(obj, key)

        item = self._create_item(obj, key)

        # cache the saved object
        self.saved_cache[key] = item

    def _create_container(self, container_dict=None, exclude=None):

        data = container_dict or self.container_object_dict
        data['template'] = self.template_parser.container_object

        fields_to_exclude = ['template']
        if exclude:
            fields_to_exclude += exclude

        super(BudgetTemplateParser, self)._create_container(container_dict=data, exclude=fields_to_exclude)

    def _create_item(self, obj, key):

        if key in self.template_parser.saved_cache:
            obj['node'] = self.template_parser.saved_cache[key]

        elif self.dry:
            # prepare data for the error
            columns = ['code', 'parent', 'parentscope']
            values = []
            for col in columns:
                if col not in obj:
                    columns.remove(col)
                else:
                    values.append(obj[col])
            self.throw(
                NodeNotFoundError(
                    row=self.rows_objects_lookup[key],
                    columns=columns,
                    values=values
                )
            )
        else:
            #TODO: handle this error properly, since at this stage there shouldn't be any missing nodes
            raise Exception()

        self._clean_object(obj, key)
        if not self.dry:
            item = self.item_model.objects.create(**obj)
        else:
            item = self.item_model(**obj)
            self._dry_clean(item, self.rows_objects_lookup[key], exclude=self.ITEM_CLEANING_EXCLUDE)

        return item

    def _add_to_container(self, obj, key):
        if not self.dry:
            obj['budget'] = self.container_object

    def _init_template_parser(self):
        container_dict_copy = deepcopy(self.container_object_dict)

        #TODO: refactor this into a proper cleanup method
        if 'template' in container_dict_copy:
            del container_dict_copy['template']

        parent_template = self._get_parent_template(container_dict_copy)

        if 'period_end' in container_dict_copy:
            del container_dict_copy['period_end']

        if parent_template:
            return BudgetTemplateParser(container_dict_copy, extends=parent_template)

        return False

    def _get_parent_template(self, container_dict):

        entity = self._set_entity()
        # set the entity also on the template container object
        # it will be used for generating a name and cleaned later
        container_dict['entity'] = entity

        if entity:
            #TODO: implement forward looking for budgets with a template to inherit
            qs = self.container_model.objects.filter(
                entity=entity,
                period_end__lte=container_dict['period_start']
            ).order_by('-period_end')[:1]

            if qs.count():
                return qs[0].template
            else:
                # try getting the standard template for this entity's division
                qs = BudgetTemplate.objects.filter(divisions=entity.division).order_by('-period_start')[:1]
                if qs.count():
                    return qs[0]
                else:
                    #TODO: handle this case of no previous template found
                    raise Exception

    def _set_entity(self):

        container_dict = self.container_object_dict

        try:
            if not isinstance(container_dict['entity'], Entity):
                entity = Entity.objects.get(
                    pk=container_dict['entity']
                )
                container_dict['entity'] = entity

                return entity

            else:
                return container_dict['entity']

        except Entity.DoesNotExist as e:
            if self.dry:
                self.throw(
                    MetaParsingError(
                        reason='Could not find Entity with key: %s' % container_dict['entity']
                    )
                )
            else:
                raise e


register('budget', BudgetParser)
