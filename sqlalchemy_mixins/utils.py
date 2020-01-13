# noinspection PyPep8Naming
class classproperty(object):
    """
    @property for @classmethod
    taken from http://stackoverflow.com/a/13624858
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

# class classproperty_with_cache(object):
#     """
#     @property for @classmethod
#     taken from http://stackoverflow.com/a/13624858
#     """
#
#     def __init__(self, fget):
#         self.fget = fget
#         self.cache = None
#
#     def __get__(self, owner_self, owner_cls):
#         if self.cache is None:
#             self.cache = self.fget(owner_cls)
#         return self.cache
