from .connection import register_connection
from .doc_model import DocModel
from .meta import Meta


"""
[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

核心理念：
1.查询和构造 model 时不做类型检查。只在保存时检查校验类型，如 .save 和 find_and_modify 和 find_one_and_update 等。
2.查询到的 doc 如果 field 有 model 里尚未定义的则隐性保存并在 .save 时原样保存。

todo 创建 model 的 db_alias-collection 不能重复
todo order_by('-age')
todo 查询 filter_by[_one] 中支持 and or 等操作
todo 支持枚举
todo mongodb 其他数据类型
todo aio_mongoorm
todo 查询的语法改进Model.age >= 1
todo pymongo 版本适配，当前 pymongo==3.7.2

todo done!!!! 增加 filter_by[_one] 支持 age__gt=1 语法
todo done!!!! self.to_json(), incloude ObjectId()
todo done!!!! 支持 user = User(_id=1, name='xxx', ...)
todo done!!!! DocModel 继承
todo done!!!! self.really_delete
todo done!!!! 查询语法校验 key 是否定义
todo done!!!! find one and update 中对应 update 中的kv进行类型校验

################################# tutorial ######################################

{demo}

"""

