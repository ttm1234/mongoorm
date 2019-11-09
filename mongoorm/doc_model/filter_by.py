from ..exceptions import KeySyntaxError


def d_from_kv(k: str, v):
    """
    :param k name__gte:
    :param v:
    """
    if k.count('__') > 1:
        raise KeySyntaxError('k ({}) 双下划线不能出现两次'.format(k))

    k_name, k_method = k.split('__')
    d = {
        'ne': '$ne',
        'lt': '$lt',
        'lte': '$lte',
        'gt': '$gt',
        'gte': '$gte',
        'in': '$in',
        'nin': '$nin',
        'exists': '$exists',
        'mod': '$mod',
        'all': '$all',
        'size': '$size',
        'contains': '$regex',
        'regex': '$regex',
    }
    if k_method not in d:
        raise KeySyntaxError('k ({}) 方法没找到 ({})'.format(k, k_method))

    r = {
        k_name: {
            d[k_method]: v
        }
    }
    return r


class FilterBy(object):
    """
    todo: and or not nor type regex_options
    """
    @classmethod
    def _filter_to_find(cls, **cond):
        """
        :param cond: {a=1, c__gt=2, c__lt=3...}
        :return: {
            'a': 1,
            'c': {
                '$gt': 2,
                '$lt': 3,
            }
        }
        """
        r = dict()
        for k, v in cond.items():
            assert isinstance(k, str)
            if '__' in k:
                d = d_from_kv(k, v)
                k, v = None, None
                for a, b in d.items():
                    k, v = a, b
                    break
                if k in r:
                    r[k].update(v)
                else:
                    r.update(d)
            else:
                r[k] = v

        return r
