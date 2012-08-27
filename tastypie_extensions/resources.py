import json

from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from tastypie.resources import ModelResource
from tastypie.utils import dict_strip_unicode_keys


class QueryByObjectModelResource(ModelResource):
    """
    A mixin that allows you to query by passing a JSON object into the
    ``query_by_object`` parameter of the URL
    """

    def filter_value_to_python(self, value, field_name, filters, filter_expr,
            filter_type):
        """
        Turn the string ``value`` into a python object.
        """
        # Simple values
        if value in ['true', 'True', True]:
            value = True
        elif value in ['false', 'False', False]:
            value = False
        elif value in ('nil', 'none', 'None', None):
            value = None

        # Split on ',' if not empty string and either an in or range filter.
        if filter_type in ('in', 'range') and len(value):
            if isinstance(value, list):
                return(value)

            elif hasattr(filters, 'getlist'):
                value = []

                for part in filters.getlist(filter_expr):
                    value.extend(part.split(','))

            else:
                value = value.split(',')

        return value

    def get_query_bits_from_dict(self, dictionary, keys_list=[], value=None):
        """
        A special method that examines dictionaries and extracts keys and values.

        ``keys_list`` and ``value`` are required for the ``filter_bits`` list,
        and ``value``, respectively, in  in ``::meth::<build_filters> build_filters``.
        """
        # If dictionary contains a query parameter, build the filter_bits
        # based on that parameter
        if dictionary.keys()[0] in self._meta.queryset.query.query_terms:
            # check to see if the values are a dict
            if isinstance(dictionary.values()[0], dict):
                # Add the key that represents the field
                keys_list.extend(dictionary.values()[0].keys())
                # Add the key that represents the filter
                keys_list.extend(dictionary.keys())
                value = dictionary.values()[0].values()[0]

            # If it's not a dictionary, then it is a direct key, value pair
            else:
                keys_list.extend(dictionary.keys())
                if not value:
                    value = dictionary.values()[0]

            return(keys_list, value)

        # Iterate over the dictionary and create a keys_list
        for key, expr in dictionary.items():
            # If this is a dict, extract the key and pass it back into this method
            if isinstance(expr, dict):
                keys_list.append(key)
                keys_list, value = self.get_query_bits_from_dict(expr,
                    keys_list=keys_list, value=value)
            # If this is just a key/value pair, it is the end of iteration,
            # add to keys_list, value
            else:
                keys_list.append(key)
                value = expr

        return(keys_list, value)

    def build_filters(self, filters=None):
        """
        An enhanced tastypie method that will first check to see if a value
        passed inside of a filter can be decoded as JSON.  If so, it passes those
        values to ``::meth::<get_query_bits_from_dict> get_query_bits_from_dict``.
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
                # Because the python json module is not as strict as JSON standards
                # We must check to make sure that the value loaded is a dict
                if not isinstance(value_dict, dict):
                    value_dict = None
            except ValueError:
                value_dict = None

            # If a value is decoded, it passes that dict into a special method
            if value_dict:
                # Get the value and filter_bits from the method.
                filter_bits, value = self.get_query_bits_from_dict(value_dict,
                    keys_list=[], value=None)
                # Because the field_name and the filter_expr are backward,
                # we need to set the field name = to filter expr
                field_name = filter_expr

            # If not, stick with standard tastypie stuff
            else:
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
