
# import generallibrary
# import generalvector
# import generalfile
# import generalgui
# generallibrary.attributes_to_markdown(generallibrary)
# generallibrary.attributes_to_markdown(generalvector)
# generallibrary.attributes_to_markdown(generalfile)
# generallibrary.attributes_to_markdown(generalgui)

from generallibrary import ObjInfo

class Foo:
    def bar(self):
        pass
objInfo = ObjInfo(Foo).generate_attributes(is_method=True)
print(objInfo.get_children())



