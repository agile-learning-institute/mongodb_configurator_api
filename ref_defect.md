There appears to be a defect related to rendering schema with a ref type property. This test data can help describe the test case:

test.yaml - configuration file
```yaml
_locked: false
description: ''
file_name: test.yaml
title: ''
versions:
- _locked: false
  add_indexes: []
  drop_indexes: []
  migrations: []
  test_data: test.1.0.0.0.json
  version: 1.0.0.0
```

real.yaml - type file
```yaml
_locked: false
file_name: real.yaml
root:
  description: A Real Number
  name: real
  required: false
  schema:
    type: float
  type: simple
```

test.1.0.0.yaml - dictionary file
```yaml
_locked: false
file_name: test.1.0.0.yaml
root:
  additional_properties: false
  description: Dictionary for test collection
  name: root
  properties:
  - description: ''
    name: _id
    required: false
    type: identifier
  - description: A polymorphic list of shapes
    items:
      description: Array item
      name: item
      properties:
      - description: A Circle Type
        name: Circle
        ref: Circle
        required: false
        type: ref
      - description: A Square Type
        name: Square
        ref: Square
        required: false
        type: ref
      - description: A Rectangle
        name: Rectangle
        ref: Rectangle
        required: false
        type: ref
      required: false
      type: one_of
    name: list
    required: false
    type: array
  - description: ''
    name: last_saved
    required: false
    type: breadcrumb
  required: false
  type: object
```

Circle.yaml - dictionary
```yaml
_locked: false
file_name: Circle.yaml
root:
  additional_properties: false
  description: ''
  name: Circle
  properties:
  - constant: ''
    description: Circle Type
    name: type
    required: false
    type: constant
  - description: Circle Radius
    name: radius
    required: false
    type: real
  required: false
  type: object
```

Square.yaml - dictionary
```yaml
_locked: false
file_name: Square.yaml
root:
  additional_properties: false
  description: A square
  name: Square
  properties:
  - constant: ''
    description: A Square Type
    name: type
    required: false
    type: constant
  - description: The length/width of the square
    name: size
    required: false
    type: real
  required: false
  type: object
```

Rectangle.yaml - dictionary
```yaml
_locked: false
file_name: Rectangle.yaml
root:
  additional_properties: false
  description: A rectangle shape
  name: Rectangle
  properties:
  - constant: ''
    description: A Rectangle Type
    name: type
    required: false
    type: constant
  - description: 'The width '
    name: width
    required: false
    type: real
  - description: The height
    name: height
    required: false
    type: real
  required: false
  type: object
```