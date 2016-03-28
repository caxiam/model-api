## REST ORM

REST ORM is a library for interacting with structured data sources.

```python
from rest_orm import fields, models

import http # or whatever you want to use


class GoogleModel(models.AdaptedModel):
    id = fields.AdaptedInteger('[path][to][id]')
    first_item = fields.AdaptedString('[items][0]')

    def make_request(self, id):
        body = http.client.get('google.com/some/endpoint/{}'.format(id)).content
        return body # {'path': {'to': {'id': id}}}


model = GoogleModel().connect(15)
assert model.id == 15
assert model.first_item == 'some value!'
```

#### Documentation

Link to docs when they're up.

#### Installation

```python
pip install git+git://github.com/caxiam/model-api.git
```

#### Requirements
Tested on Python 2.7.

REST ORM does not require any external dependencies.

#### License
MIT
