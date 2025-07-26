import unittest
from unittest.mock import patch, Mock
from configurator.services.property import Property
from configurator.services.property.array_type import ArrayType
from configurator.services.property.complex_type import ComplexType
from configurator.services.property.constant_type import ConstantType
from configurator.services.property.enum_array_type import EnumArrayType
from configurator.services.property.enum_type import EnumType
from configurator.services.property.object_type import ObjectType
from configurator.services.property.one_of_type import OneOfType
from configurator.services.property.ref_type import RefType
from configurator.services.property.simple_type import SimpleType
from configurator.services.property.custom_type import CustomType
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

    def test_property_factory_constant(self):
        """Test Property factory creates ConstantType for constant type"""
        data = {"name": "test", "type": "constant", "constant": "test_value"}
        prop = Property(data)
        self.assertIsInstance(prop, ConstantType)

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


if __name__ == '__main__':
    unittest.main() 