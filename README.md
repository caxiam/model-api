## REST ORM
A library for interacting with structured data sources.

### Why REST ORM

#### Features
- [x] Easy deserialization of complex paths.
- [x] Type sensitive deserialization.
- [x] Configuration for handling missing fields.
- [x] Simple integration with your HTTP client of choice.

#### Coming Soon
- [ ] Support for serializing filters into URL parameters.

### Getting Started

#### Models
Defining your model does not require any configuration beyond subclassing the `AdaptedModel` class.

```python
class Model(rest_orm.models.AdaptedModel):
    pass
```

However, the above is not very useful and can be extended by adding the following:
* Add a field with a valid path.
* Add a `make_request` method that returns a valid JSON string.

```python
class Model(rest_orm.models.AdaptedModel):
    id = rest_orm.fields.AdaptedInteger('[key]')

    def make_request(self):
        httpClient = CLIENT # you can use whatever you want
        response = httpClient.get('google.com/some/json/endpoint')
        return response.body
```

You can call this model and use it in your code by executing the following:

```python
x = Model().connect()
assert x.id == 1 # True
```

You can specify an arbitrary amounts of arguments and keyword arguments on the make_request function which can then be called on the connect method.

```python
x = Model().connect(cart_id, product_id)
```

#### Fields
Defining a field requires only that the `path` argument is satisfied.  The path argument is a valid string path value or a `None` type value.  Specifying `None` returns the entire data set as that fields value.

The `path` argument behaves exactly like a normal Python attribute retrieval.  You can specify keys as strings and indexes as numbers.  For example, the following path is acceptable:

```python
obj = {
    'key': [{
        'term': [1, 2, 3]
    }]
}
value = rest_orm.fields.AdaptedField('[key][0][term][-1]')
```

The `value` variable would then be equal to the `key` key's first item's `term` key's last item.  In other words, the path specified points to the `3` value in the object defined above it.

**Optional arguments:**
* `allow_missing`: If the value cannot be found, setting this kwarg to true will raise an error.
* `missing`: Specifying this kwarg allows missing values to default to the value of your choice.
* `validate`: Accepts a callable reference and errs if the returned value fails.


#### Requests
To make a request, you can define a `make_request` method on your model.  The make_request method can accept an arbitrary amount of arguments and keyword arguments.  You can do anything you want within this method.  The only rule is that you must return a valid json string as the only return value.

```python
def make_request(self, a, b, c, d=1, e=2, f=3):
    # Psuedo code; obviously this would be implemented according to your requirements.
    return httpClient.post(url=url.format(a, b, c, d), body={'e': e, 'f': f})
```

#### Local or Offline Handling
You do not need to make a request to a remote endpoint in order to use this library.  You may call the `loads` or `load` method on a JSON string or Python dictionary respectively.

```python
# Load a JSON string
model = Model().loads('{"x": 1}') # model.x == 1

# Load a python dictionary
model = Model().load({"x": 1}) # model.x == 1
```
