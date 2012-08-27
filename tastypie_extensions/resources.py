import json

from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from tastypie.resources import ModelResource
from tastypie.utils import dict_strip_unicode_keys


class QueryByObjectModelResource(ModelResource):
    """
    A mixin that allows you to query by passing a JSON object into the
    ``query_by_object`` parameter of the URL
    """

    def get_query_bits_from_dict(self, dictionary, keys_list=[], value=None):

        for key, expr in dictionary.items():
            if isinstance(expr, dict):
                keys_list.append(key)
                keys_list, value = self.get_query_bits_from_dict(expr,
                    keys_list=keys_list, value=value)

            if len(expr) > 1 and 'filter' in expr:
                filter_key = expr.pop('filter')
                final_key, value = expr.items()[0]
                keys_list.extend([final_key, filter_key])

        return(keys_list, value)

    def build_filters(self, filters=None):
        """
        Given a dictionary of filters, create the necessary ORM-level filters.

        Keys should be resource fields, **NOT** model fields.

        Valid values are either a list of Django filter types (i.e.
        ``['startswith', 'exact', 'lte']``), the ``ALL`` constant or the
        ``ALL_WITH_RELATIONS`` constant.

        At the declarative level:
            filtering = {
                'resource_field_name': ['exact', 'startswith', 'endswith',
                    'contains'],
                'resource_field_name_2': ['exact', 'gt', 'gte', 'lt', 'lte',
                    'range'],
                'resource_field_name_3': ALL,
                'resource_field_name_4': ALL_WITH_RELATIONS,
                ...
            }
        Accepts the filters as a dict. None by default, meaning no filters.
        """
        if filters is None:
            filters = {}

        qs_filters = {}
        if hasattr(self._meta, 'queryset'):
            # Get the possible query terms from the current QuerySet.
            if hasattr(self._meta.queryset.query.query_terms, 'keys'):
                # Django 1.4 & below compatibility.
                query_terms = self._meta.queryset.query.query_terms.keys()
            else:
                # Django 1.5+.
                query_terms = self._meta.queryset.query.query_terms
        else:
            query_terms = QUERY_TERMS.keys()

        for filter_expr, value in filters.items():
            filter_type = 'exact'
            # Check first to see if a value can be decoded as json
            try:
                value_dict = json.loads(value)
                filter_bits, value = self.get_query_bits_from_dict(value_dict,
                    keys_list=[], value=None)
                field_name = filter_expr

            except ValueError:
                filter_bits = filter_expr.split(LOOKUP_SEP)
                field_name = filter_bits.pop(0)

            if not field_name in self.fields:
                # It's not a field we know about. Move along citizen.
                continue

            if len(filter_bits) and filter_bits[-1] in query_terms:
                filter_type = filter_bits.pop()
            lookup_bits = self.check_filtering(field_name, filter_type,
                filter_bits)
            value = self.filter_value_to_python(value, field_name, filters,
                filter_expr, filter_type)

            db_field_name = LOOKUP_SEP.join(lookup_bits)
            qs_filter = "%s%s%s" % (db_field_name, LOOKUP_SEP, filter_type)
            qs_filters[qs_filter] = value

        return dict_strip_unicode_keys(qs_filters)
