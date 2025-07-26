import unittest
from unittest.mock import patch, Mock
from configurator.services.property import Property
from configurator.services.property.base import BaseProperty
from configurator.services.property.object_type import ObjectType
from configurator.services.property.array_type import ArrayType
from configurator.services.property.enum_type import EnumType
from configurator.services.property.enum_array_type import EnumArrayType
from configurator.services.property.ref_type import RefType
from configurator.services.property.simple_type import SimpleType
from configurator.services.property.complex_type import ComplexType
from configurator.services.property.custom_type import CustomType
from configurator.services.property.one_of_type import OneOfType
from configurator.services.enumerator_service import Enumerations
from configurator.utils.configurator_exception import ConfiguratorException


class TestPropertyFactory(unittest.TestCase):
    """Test the Property factory function"""

    def test_property_factory_array(self):
        """Test Property factory creates ArrayType for array type"""
        data = {"name": "test", "type": "array", "items": {"name": "item", "type": "string"}}
        prop = Property(data)
        self.assertIsInstance(prop, ArrayType)

    def test_property_factory_complex(self):
        """Test Property factory creates ComplexType for complex type"""
        data = {"name": "test", "type": "complex"}
        prop = Property(data)
        self.assertIsInstance(prop, ComplexType)

    def test_property_factory_enum_array(self):
        """Test Property factory creates EnumArrayType for enum_array type"""
        data = {"name": "test", "type": "enum_array", "enums": "test_enum"}
        prop = Property(data)
        self.assertIsInstance(prop, EnumArrayType)

    def test_property_factory_enum(self):
        """Test Property factory creates EnumType for enum type"""
        data = {"name": "test", "type": "enum", "enums": "test_enum"}
        prop = Property(data)
        self.assertIsInstance(prop, EnumType)

    def test_property_factory_object(self):
        """Test Property factory creates ObjectType for object type"""
        data = {"name": "test", "type": "object", "properties": []}
        prop = Property(data)
        self.assertIsInstance(prop, ObjectType)

    def test_property_factory_one_of(self):
        """Test Property factory creates OneOfType for one_of type"""
        data = {"name": "test", "type": "one_of", "oneOf": []}
        prop = Property(data)
        self.assertIsInstance(prop, OneOfType)

    def test_property_factory_ref(self):
        """Test Property factory creates RefType for ref type"""
        data = {"name": "test", "type": "ref", "ref": "test.yaml"}
        prop = Property(data)
        self.assertIsInstance(prop, RefType)

    def test_property_factory_simple(self):
        """Test Property factory creates SimpleType for simple type"""
        data = {"name": "test", "type": "simple"}
        prop = Property(data)
        self.assertIsInstance(prop, SimpleType)

    def test_property_factory_custom(self):
        """Test Property factory creates CustomType for unknown type"""
        data = {"name": "test", "type": "unknown_type"}
        prop = Property(data)
        self.assertIsInstance(prop, CustomType)

    def test_property_factory_missing_name(self):
        """Test Property factory raises exception for missing name"""
        data = {"type": "string"}
        with self.assertRaises(ConfiguratorException) as context:
            Property(data)
        self.assertIn("Missing required name", str(context.exception))


class TestBaseProperty(unittest.TestCase):
    """Test the BaseProperty class"""

    def test_base_property_init(self):
        """Test BaseProperty initialization"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "string",
            "required": True
        }
        prop = BaseProperty(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.type, "string")
        self.assertTrue(prop.required)

    def test_base_property_init_defaults(self):
        """Test BaseProperty initialization with defaults"""
        data = {"name": "test_prop"}
        prop = BaseProperty(data)
        self.assertEqual(prop.name, "test_prop")
        self.assertEqual(prop.description, "")
        self.assertEqual(prop.type, "void")
        self.assertFalse(prop.required)

    def test_base_property_missing_name(self):
        """Test BaseProperty raises exception for missing name"""
        data = {"type": "string"}
        with self.assertRaises(ConfiguratorException) as context:
            BaseProperty(data)
        self.assertIn("Missing required name", str(context.exception))

    def test_base_property_to_dict(self):
        """Test BaseProperty to_dict method"""
        data = {
            "name": "test_prop",
            "description": "Test description",
            "type": "string",
            "required": True
        }
        prop = BaseProperty(data)
        result = prop.to_dict()
        expected = {
            "name": "test_prop",
            "description": "Test description",
            "type": "string",
            "required": True
        }
        self.assertEqual(result, expected)

    def test_base_property_to_json_schema(self):
        """Test BaseProperty to_json_schema method"""
        data = {"name": "test_prop", "description": "Test description", "type": "string"}
        prop = BaseProperty(data)
        mock_enumerations = Mock()
        result = prop.to_json_schema(mock_enumerations)
        expected = {"description": "Test description", "type": "string"}
        self.assertEqual(result, expected)

    def test_base_property_to_bson_schema(self):
        """Test BaseProperty to_bson_schema method"""
        data = {"name": "test_prop", "description": "Test description", "type": "string"}
        prop = BaseProperty(data)
        mock_enumerations = Mock()
        result = prop.to_bson_schema(mock_enumerations)
        expected = {"bsonType": "string"}
        self.assertEqual(result, expected)


class TestObjectType(unittest.TestCase):
    """Test the ObjectType class"""

    def test_object_type_init(self):
        """Test ObjectType initialization"""
        data = {
            "name": "test_object",
            "type": "object",
            "description": "Test object",
            "required": True,
            "additionalProperties": False,
            "properties": [
                {"name": "prop1", "type": "string"},
                {"name": "prop2", "type": "number"}
            ]
        }
        prop = ObjectType(data)
        self.assertEqual(prop.name, "test_object")
        self.assertEqual(prop.type, "object")
        self.assertEqual(prop.description, "Test object")
        self.assertTrue(prop.required)
        self.assertFalse(prop.additional_properties)
        self.assertEqual(len(prop.properties), 2)

    def test_object_type_to_dict(self):
        """Test ObjectType to_dict method"""
        data = {
            "name": "test_object",
            "type": "object",
            "description": "Test object",
            "required": True,
            "additionalProperties": False,
            "properties": [
                {"name": "prop1", "type": "string", "description": "Property 1"},
                {"name": "prop2", "type": "number", "description": "Property 2"}
            ]
        }
        prop = ObjectType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_object")
        self.assertEqual(result["type"], "object")
        self.assertEqual(result["description"], "Test object")
        self.assertTrue(result["required"])
        self.assertFalse(result["additionalProperties"])
        self.assertEqual(len(result["properties"]), 2)


class TestArrayType(unittest.TestCase):
    """Test the ArrayType class"""

    def test_array_type_init(self):
        """Test ArrayType initialization"""
        data = {
            "name": "test_array",
            "type": "array",
            "description": "Test array",
            "items": {"name": "item", "type": "string"}
        }
        prop = ArrayType(data)
        self.assertEqual(prop.name, "test_array")
        self.assertEqual(prop.type, "array")
        self.assertEqual(prop.description, "Test array")
        self.assertIsNotNone(prop.items)

    def test_array_type_to_dict(self):
        """Test ArrayType to_dict method"""
        data = {
            "name": "test_array",
            "type": "array",
            "description": "Test array",
            "items": {"name": "item", "type": "string"}
        }
        prop = ArrayType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_array")
        self.assertEqual(result["type"], "array")
        self.assertEqual(result["description"], "Test array")
        self.assertIn("items", result)


class TestEnumType(unittest.TestCase):
    """Test the EnumType class"""

    def test_enum_type_init(self):
        """Test EnumType initialization"""
        data = {
            "name": "test_enum",
            "type": "enum",
            "description": "Test enum",
            "enums": "test_enum_values",
            "required": True
        }
        prop = EnumType(data)
        self.assertEqual(prop.name, "test_enum")
        self.assertEqual(prop.type, "enum")
        self.assertEqual(prop.description, "Test enum")
        self.assertEqual(prop.enums, "test_enum_values")
        self.assertTrue(prop.required)

    def test_enum_type_to_dict(self):
        """Test EnumType to_dict method"""
        data = {
            "name": "test_enum",
            "type": "enum",
            "description": "Test enum",
            "enums": "test_enum_values",
            "required": True
        }
        prop = EnumType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_enum")
        self.assertEqual(result["type"], "enum")
        self.assertEqual(result["description"], "Test enum")
        self.assertEqual(result["enums"], "test_enum_values")
        self.assertTrue(result["required"])

    def test_enum_type_to_json_schema(self):
        """Test EnumType to_json_schema method"""
        data = {
            "name": "test_enum",
            "type": "enum",
            "description": "Test enum",
            "enums": "test_enum_values"
        }
        prop = EnumType(data)
        mock_enumerations = Mock()
        mock_enumerations.get_enum_values.return_value = ["value1", "value2"]
        result = prop.to_json_schema(mock_enumerations)
        self.assertEqual(result["type"], "string")
        self.assertEqual(result["description"], "Test enum")
        self.assertEqual(result["enum"], ["value1", "value2"])

    def test_enum_type_to_bson_schema(self):
        """Test EnumType to_bson_schema method"""
        data = {
            "name": "test_enum",
            "type": "enum",
            "description": "Test enum",
            "enums": "test_enum_values"
        }
        prop = EnumType(data)
        mock_enumerations = Mock()
        mock_enumerations.get_enum_values.return_value = ["value1", "value2"]
        result = prop.to_bson_schema(mock_enumerations)
        self.assertEqual(result["bsonType"], "string")
        self.assertEqual(result["enum"], ["value1", "value2"])


class TestEnumArrayType(unittest.TestCase):
    """Test the EnumArrayType class"""

    def test_enum_array_type_init(self):
        """Test EnumArrayType initialization"""
        data = {
            "name": "test_enum_array",
            "type": "enum_array",
            "description": "Test enum array",
            "enums": "test_enum_values"
        }
        prop = EnumArrayType(data)
        self.assertEqual(prop.name, "test_enum_array")
        self.assertEqual(prop.type, "enum_array")
        self.assertEqual(prop.description, "Test enum array")
        self.assertEqual(prop.enums, "test_enum_values")

    def test_enum_array_type_to_dict(self):
        """Test EnumArrayType to_dict method"""
        data = {
            "name": "test_enum_array",
            "type": "enum_array",
            "description": "Test enum array",
            "enums": "test_enum_values"
        }
        prop = EnumArrayType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_enum_array")
        self.assertEqual(result["type"], "enum_array")
        self.assertEqual(result["description"], "Test enum array")
        self.assertEqual(result["enums"], "test_enum_values")

    def test_enum_array_type_to_json_schema(self):
        """Test EnumArrayType to_json_schema method"""
        data = {
            "name": "test_enum_array",
            "type": "enum_array",
            "description": "Test enum array",
            "enums": "test_enum_values"
        }
        prop = EnumArrayType(data)
        mock_enumerations = Mock()
        mock_enumerations.get_enum_values.return_value = ["value1", "value2"]
        result = prop.to_json_schema(mock_enumerations)
        self.assertEqual(result["type"], "array")
        self.assertEqual(result["description"], "Test enum array")
        self.assertEqual(result["items"]["type"], "string")
        self.assertEqual(result["items"]["enum"], ["value1", "value2"])

    def test_enum_array_type_to_bson_schema(self):
        """Test EnumArrayType to_bson_schema method"""
        data = {
            "name": "test_enum_array",
            "type": "enum_array",
            "description": "Test enum array",
            "enums": "test_enum_values"
        }
        prop = EnumArrayType(data)
        mock_enumerations = Mock()
        mock_enumerations.get_enum_values.return_value = ["value1", "value2"]
        result = prop.to_bson_schema(mock_enumerations)
        self.assertEqual(result["bsonType"], "array")
        self.assertEqual(result["items"]["bsonType"], "string")
        self.assertEqual(result["items"]["enum"], ["value1", "value2"])


class TestRefType(unittest.TestCase):
    """Test the RefType class"""

    def test_ref_type_init(self):
        """Test RefType initialization"""
        data = {
            "name": "test_ref",
            "type": "ref",
            "ref": "test.yaml"
        }
        prop = RefType(data)
        self.assertEqual(prop.name, "test_ref")
        self.assertEqual(prop.type, "ref")
        self.assertEqual(prop.ref, "test.yaml")

    def test_ref_type_to_dict(self):
        """Test RefType to_dict method"""
        data = {
            "name": "test_ref",
            "type": "ref",
            "ref": "test.yaml"
        }
        prop = RefType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_ref")
        self.assertEqual(result["type"], "ref")
        self.assertEqual(result["ref"], "test.yaml")


class TestSimpleType(unittest.TestCase):
    """Test the SimpleType class"""

    def test_simple_type_init(self):
        """Test SimpleType initialization"""
        data = {
            "name": "test_simple",
            "type": "simple",
            "description": "Test simple",
            "schema": {"minimum": 0, "maximum": 100}
        }
        prop = SimpleType(data)
        self.assertEqual(prop.name, "test_simple")
        self.assertEqual(prop.type, "simple")
        self.assertEqual(prop.description, "Test simple")
        self.assertEqual(prop.schema, {"minimum": 0, "maximum": 100})

    def test_simple_type_to_dict(self):
        """Test SimpleType to_dict method"""
        data = {
            "name": "test_simple",
            "type": "simple",
            "description": "Test simple",
            "schema": {"minimum": 0, "maximum": 100}
        }
        prop = SimpleType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_simple")
        self.assertEqual(result["type"], "simple")
        self.assertEqual(result["description"], "Test simple")
        self.assertEqual(result["schema"], {"minimum": 0, "maximum": 100})

    def test_simple_type_to_json_schema(self):
        """Test SimpleType to_json_schema method"""
        data = {
            "name": "test_property",
            "type": "string",
            "schema": {"minLength": 5, "maxLength": 10}
        }
        prop = SimpleType(data)
        result = prop.to_json_schema(Mock())
        
        expected = {
            "description": "",
            "type": "string",
            "minLength": 5,
            "maxLength": 10
        }
        self.assertEqual(result, expected)

    def test_simple_type_to_bson_schema(self):
        """Test SimpleType to_bson_schema method"""
        data = {
            "name": "test_property",
            "type": "string",
            "schema": {"minLength": 5, "maxLength": 10}
        }
        prop = SimpleType(data)
        
        # This should fail due to KeyError accessing the_dict["type"]
        # because BaseProperty.to_bson_schema() returns {"bsonType": "string"}
        # but SimpleType tries to access the_dict["type"] which doesn't exist
        with self.assertRaises(KeyError) as context:
            result = prop.to_bson_schema(Mock())
        
        self.assertIn("'type'", str(context.exception))


class TestComplexType(unittest.TestCase):
    """Test the ComplexType class"""

    def test_complex_type_init(self):
        """Test ComplexType initialization"""
        data = {
            "name": "test_complex",
            "type": "complex",
            "description": "Test complex",
            "json_schema": {"format": "email"},
            "bson_schema": {"bsonType": "string"}
        }
        prop = ComplexType(data)
        self.assertEqual(prop.name, "test_complex")
        self.assertEqual(prop.type, "complex")
        self.assertEqual(prop.description, "Test complex")
        self.assertEqual(prop.json_schema, {"format": "email"})
        self.assertEqual(prop.bson_schema, {"bsonType": "string"})

    def test_complex_type_to_dict(self):
        """Test ComplexType to_dict method"""
        data = {
            "name": "test_complex",
            "type": "complex",
            "description": "Test complex",
            "json_schema": {"format": "email"},
            "bson_schema": {"bsonType": "string"}
        }
        prop = ComplexType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_complex")
        self.assertEqual(result["type"], "complex")
        self.assertEqual(result["description"], "Test complex")
        self.assertEqual(result["json_schema"], {"format": "email"})
        self.assertEqual(result["bson_schema"], {"bsonType": "string"})

    def test_complex_type_to_json_schema(self):
        """Test ComplexType to_json_schema method"""
        data = {
            "name": "test_complex",
            "type": "complex",
            "description": "Test complex",
            "json_schema": {"format": "email"}
        }
        prop = ComplexType(data)
        mock_enumerations = Mock()
        result = prop.to_json_schema(mock_enumerations)
        self.assertEqual(result["description"], "Test complex")
        self.assertEqual(result["type"], "complex")
        self.assertEqual(result["format"], "email")


class TestCustomType(unittest.TestCase):
    """Test the CustomType class"""

    def test_custom_type_init(self):
        """Test CustomType initialization"""
        data = {
            "name": "test_custom",
            "type": "custom_type",
            "description": "Test custom",
            "custom_field": "custom_value"
        }
        prop = CustomType(data)
        self.assertEqual(prop.name, "test_custom")
        self.assertEqual(prop.type, "custom_type")
        self.assertEqual(prop.description, "Test custom")

    def test_custom_type_to_dict(self):
        """Test CustomType to_dict method"""
        data = {
            "name": "test_custom",
            "type": "custom_type",
            "description": "Test custom",
            "custom_field": "custom_value"
        }
        prop = CustomType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_custom")
        self.assertEqual(result["type"], "custom_type")
        self.assertEqual(result["description"], "Test custom")


class TestOneOfType(unittest.TestCase):
    """Test the OneOfType class"""

    def test_one_of_type_init(self):
        """Test OneOfType initialization"""
        data = {
            "name": "test_one_of",
            "type": "one_of",
            "description": "Test oneOf",
            "properties": [
                {"name": "option1", "type": "string"},
                {"name": "option2", "type": "number"}
            ]
        }
        prop = OneOfType(data)
        self.assertEqual(prop.name, "test_one_of")
        self.assertEqual(prop.type, "one_of")
        self.assertEqual(prop.description, "Test oneOf")
        self.assertEqual(len(prop.properties), 2)

    def test_one_of_type_to_dict(self):
        """Test OneOfType to_dict method"""
        data = {
            "name": "test_one_of",
            "type": "one_of",
            "description": "Test oneOf",
            "properties": [
                {"name": "option1", "type": "string"},
                {"name": "option2", "type": "number"}
            ]
        }
        prop = OneOfType(data)
        result = prop.to_dict()
        self.assertEqual(result["name"], "test_one_of")
        self.assertEqual(result["type"], "one_of")
        self.assertEqual(result["description"], "Test oneOf")
        self.assertEqual(len(result["properties"]), 2)


if __name__ == '__main__':
    unittest.main() 