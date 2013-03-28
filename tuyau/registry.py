
class TypeRegistry(object):
    """Mixin to help register serializable classes"""

    @classmethod
    def from_json(registry, doc):
        cls = doc.pop('class')
        return registry.CLASSES[cls](**doc)

    @classmethod
    def register_class(registry, cond_cls):
        registry.CLASSES[cond_cls.__name__] = cond_cls
        return cond_cls

    def to_json(self):
        dct = self.__dict__.copy()
        dct['class'] = self.__class__.__name__

        return dct
