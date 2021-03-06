REST ORM
========
.. image:: https://readthedocs.org/projects/model-api/badge/?version=latest
    :target: http://model-api.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

REST ORM is a library for interacting with structured data sources.

.. code-block:: python

    from bogus import http # http client of your choice
    from rest_orm import fields, models


    class GoogleModel(models.AdaptedModel):
        id = fields.AdaptedInteger('[path][to][id]')
        first_item = fields.AdaptedString('[items][0]')

        def make_request(self, id):
            body = http.client.get('google.com/some/endpoint/{}'.format(id)).content
            return body # {'path': {'to': {'id': id}}, 'items': ['some value!']}


    model = GoogleModel().connect(15)
    assert model.id == 15
    assert model.first_item == 'some value!'


=============
Documentation
=============

Full documentation is available at: http://model-api.readthedocs.org/en/latest/

============
Installation
============

.. code-block:: bash

    $ pip install git+git://github.com/caxiam/model-api.git


============
Requirements
============
Tested on Python 2.7.

REST ORM does not require any external dependencies.

=======
License
=======
MIT
