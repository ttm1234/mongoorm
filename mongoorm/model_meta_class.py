from .exceptions import DocModelErr
from .meta import Meta
from .fields import _FieldBase
from .utils import log

doc_model_name = 'DocModel'


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        log("构造{}对象".format(name), bases, attrs.get('__inheritance__'))
        if name == doc_model_name:
            return type.__new__(cls, name, bases, attrs)
        elif attrs.get('__inheritance__', False):
            return type.__new__(cls, name, bases, attrs)
        else:
            attrs = handle_attr(name, attrs)
            m = type.__new__(cls, name, bases, attrs)

            # 冗余信息
            for name, field in m.__mappings__.items():
                field.name = name
                field.cls_model = m

            return m


def handle_attr(name, attrs):
    attrs['__inheritance__'] = False
    mappings = {}
    new_attrs = {}
    for k, v in attrs.items():
        if not isinstance(v, _FieldBase):
            new_attrs[k] = v
        else:
            mappings[k] = v
    attrs = new_attrs
    attrs['__mappings__'] = mappings
    attrs['__payload__'] = dict()

    _new_cls_valid(name, attrs)

    return attrs


def _new_cls_valid(name, attrs):
    if not isinstance(attrs.get('meta'), Meta):
        raise DocModelErr('Model {} error, Meta class is required, or __inheritance__ = True??'.format(name))

    if '_id' not in attrs['__mappings__'] or (not attrs['__mappings__']['_id'].required):
        raise DocModelErr('Model {} error, _id is required as primary key, and must be required=True in kwargs'.format(name))
