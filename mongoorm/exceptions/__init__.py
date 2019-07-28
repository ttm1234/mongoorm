class BaseErr(Exception):

    def prepend_msg(self, msg: str):
        new_args = []
        for i in self.args:
            new_args.append(i)

        if len(new_args) == 0:
            new_args[0] = msg
        elif not isinstance(new_args[0], str):
            new_args.insert(0, msg)
        else:
            new_args[0] = '{} {}'.format(msg, new_args[0])
        self.args = tuple(new_args)


class ConnectionErr(BaseErr):
    pass


class DocModelErr(BaseErr):
    pass


class ModelValidErr(BaseErr):
    pass


class UndefinedError(BaseErr):
    pass


class KeySyntaxError(BaseErr):
    pass


def put_cls_exception(e: BaseErr, cls):
    s = '<__class__ {} >'.format(cls.__name__)
    e.prepend_msg(s)
    return e


def put_inst_exception(e: BaseErr, instance):
    s = '< object at {} by __class__ {} >'.format(id(instance), instance.__class__.__name__)
    e.prepend_msg(s)
    return e


if __name__ == '__main__':
    pass
