import copy
from bson import ObjectId

from ..exceptions import UndefinedError, ModelValidErr

undefined_obj = object()
None_type = type(None)


class _FieldBase(object):
    """
    primary key is _id
    """
    def __init__(
            self,
            required=True,
            nullabled=True,
            choices=None,
            default=undefined_obj,
            validation=None,
    ):
        choices = copy.deepcopy(choices)

        self.required = required
        self.nullabled = nullabled
        self.choices = choices
        self.default = default
        self.validation = validation
        self.type = None
        # 冗余
        self.name = None
        self.cls_model = None

        self.init_valid()

    def init_valid(self):
        for i in ('required', 'nullabled'):
            assert isinstance(getattr(self, i), bool)
        assert self.choices is None or isinstance(self.choices, (list, tuple, None_type))
        assert self.validation is None or callable(self.validation)

    def validate(self, v):
        if not self.nullabled and v is None:
            # todo
            raise ModelValidErr('validate error, nullabled is False, can not be None')
        if v is not None:
            # 如果可以 None，默认类型校验和choices 通过
            if self.type is not None:
                if self.type is float:
                    type_ok = isinstance(v, (float, int, ))
                elif self.type is int:
                    type_ok = (not isinstance(v, bool)) and isinstance(v, int)
                else:
                    type_ok = isinstance(v, self.type)
                if not type_ok:
                    raise ModelValidErr('validate error, {} required, not {}'.format(self.type, v))

            if self.choices is not None and v not in self.choices:
                raise ModelValidErr('validate error, must be in {}, not {}'.format(self.choices, v))

        if self.validation is not None and not self.validation(v):
            raise ModelValidErr('{} can not be validate by {} validation'.format(v, self.__class__.__name__))

    def get_default_value(self):
        if self.default is undefined_obj:
            raise UndefinedError()
        elif callable(self.default):
            return self.default()
        else:
            return copy.deepcopy(self.default)


class FieldString(_FieldBase):

    def __init__(self, **kwargs):
        super(FieldString, self).__init__(**kwargs)
        self.type = str

        # todo 算了吧
        # try:
        #     v = self.get_default_value()
        #     assert isinstance(v, self.type)
        # except UndefinedError as e:
        #     pass
        # except Exception as e:
        #     raise e


class FieldInteger(_FieldBase):

    def __init__(self, **kwargs):
        super(FieldInteger, self).__init__(**kwargs)
        self.type = int


class FieldBoolean(_FieldBase):

    def __init__(self, **kwargs):
        super(FieldBoolean, self).__init__(**kwargs)
        self.type = bool


class FieldFloat(_FieldBase):

    def __init__(self, **kwargs):
        super(FieldFloat, self).__init__(**kwargs)
        self.type = float


class FieldList(_FieldBase):

    def __init__(self, **kwargs):
        super(FieldList, self).__init__(**kwargs)
        self.type = list


class FieldDict(_FieldBase):

    def __init__(self, **kwargs):
        super(FieldDict, self).__init__(**kwargs)
        self.type = dict


class FieldObjectId(_FieldBase):

    def __init__(self, **kwargs):

        super(FieldObjectId, self).__init__(**kwargs)
        self.type = ObjectId


# todo 最好别用这个
class FieldAny(_FieldBase):

    def __init__(self, **kwargs):

        super(FieldAny, self).__init__(**kwargs)
        self.type = None
