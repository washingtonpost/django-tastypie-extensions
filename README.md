# django-tastypie-extensions

A set of extended capabilities for django-tastypie.

Includes:

* QueryByObjectModelResource

Roadmap:

* Tests (coming very soon!)

LICENSE: MIT


## How to use

### QueryByObjectModelResource

QueryByObjectModelResource is a class that blends the functionality of object querying,
with the standard tastypie query syntax.

Use this class in place of the standard ``ModelResource``.

    """models.py"""
    from django.db import models

    class Agency(models.Model):
        name = models.CharField(max_length=255)
        revenue = models.DecimalField()

    class TopModel(models.Model):
        name = models.CharField(max_length=255)
        agency = models.ForeignKey(Agency)


    """api.py"""
    from tastypie.api import Api
    from tastypie_extensions import QueryByObjectModelResource

    class MyExtendedResourceClass(QueryByObjectModelResource):

        class Meta:
            queryset = TopModel
            resource_name = 'topmodel'

    my_api = Api('v2')
    my_api.register(MyExtendedResourceClass())

You can query this using the normal tastypie syntax.

    http://mysite/topmodel/api/v2/topmodel/agency__name=Wicked/?format=json

You can also use an object syntax that is built from valid JSON.

    http://mysite/topmodel/api/v2/topmodel/agency={"name":"Wicked"}/?format=json


The format is based off of MongoDB's simple rest API but uses the standard django filter terms.

So, to query for a case insensitive full-text search (``icontains``):

    # QueryByObjectModelResource
    http://mysite/topmodel/api/v2/topmodel/agency={"icontains":{"name":"Wicked"}}/?format=json

    # ModelResource
    http://mysite/topmodel/api/v2/topmodel/agency__name__icontains=Wicked/?format=json

A greater than (``gt``):

    # QueryByObjectModelResource
    http://mysite/topmodel/api/v2/topmodel/agency={"gt":{"revenue":10000}}/?format=json

    # ModelResource
    http://mysite/topmodel/api/v2/topmodel/agency__revenue__gt=10000/?format=json

