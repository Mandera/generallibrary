
import inspect
from types import MethodWrapperType


class _ObjInfoType:
    """ Only one of these methods starting with 'is_' will return True. """
    def type(self):
        """ Get a string of what type obj is. """
        for name, method in self.type_methods.items():
            if method(self):
                return True

    def is_module(self):
        """ Get whether obj is a module.

            :param generallibrary.ObjInfo self: """
        return inspect.ismodule(self.obj)

    def is_function(self):
        """ Get whether obj is a function.

            :param generallibrary.ObjInfo self: """
        return inspect.isfunction(self.obj) and not self.is_method()

    def is_class(self):
        """ Get whether obj is a class.

            :param generallibrary.ObjInfo self: """
        return inspect.isclass(self.obj)

    def is_property(self):
        """ Get whether obj is a property of a class.

                :param generallibrary.ObjInfo self: """
        return inspect.isdatadescriptor(self.obj)

    def is_instance(self):
        """ Get whether obj is an instance of it's class.
            I think every obj is technically an instance of something though.

            :param generallibrary.ObjInfo self: """
        return not hasattr(self.obj, "__name__") and not self.is_property() and not self.is_method()

    def is_method(self):
        """ Get whether obj is a method.

            :param generallibrary.ObjInfo self: """
        if inspect.ismethod(self.obj) or inspect.ismethoddescriptor(self.obj):
            return True

        if self.is_class() or not callable(self.obj):  # Unbound cls and static methods aren't "callable"
            return False

        if isinstance(self.obj, MethodWrapperType):
            return True

        if parent := self.get_parent():
            if parent.is_class():
                return True

        return False

    type_methods = {key: value for key, value in locals().items() if key != "type" and not key.startswith("_")}




