"""Factory function for creating property types"""

def Property(data: dict):
    """Factory function to create the appropriate property type"""
    type_ = data.get('type', 'void')
    
    if type_ == 'array':
        from .array_type import ArrayType
        return ArrayType(data)
    elif type_ == 'complex':
        from .complex_type import ComplexType
        return ComplexType(data)
    elif type_ == 'enum_array':
        from .enum_array_type import EnumArrayType
        return EnumArrayType(data)
    elif type_ == 'enum':
        from .enum_type import EnumType
        return EnumType(data)
    elif type_ == 'object':
        from .object_type import ObjectType
        return ObjectType(data)
    elif type_ == 'one_of':
        from .one_of_type import OneOfType
        return OneOfType(data)
    elif type_ == 'ref':
        from .ref_type import RefType
        return RefType(data)
    elif type_ == 'simple':
        from .simple_type import SimpleType
        return SimpleType(data)
    else:
        from .custom_type import CustomType
        return CustomType(data) 