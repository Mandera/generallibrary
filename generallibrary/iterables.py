

class SortedList:
    """
    Controls a sorted list in ascending order.
    """
    def __init__(self, *objects, getValueFunc=None):
        """
        :param objects: Objects to be added instantly
        :param function[any] -> float getValueFunc: A function that only takes obj as parameter and returns a float to be used for sorting.
        """
        if objects and typeChecker(objects[0], "function", error=False):
            raise AttributeError("First object was a function, make sure to use the 'getValueFunc' key.")

        if getValueFunc is None:
            getValueFunc = lambda obj: obj

        self.getValueFunc = getValueFunc
        self.objects = []
        self._values = []
        self.add(*objects)

    def __contains__(self, item):
        return item in self.objects

    def __iter__(self):
        return self.objects.__iter__()

    def add(self, *objects):
        """
        Add objects to sorted list.
        """
        for newObj in objects:
            newValue = self.getValueFunc(newObj)
            for i, obj in enumerate(self.objects):
                value = self._values[i]
                if newValue <= value:
                    index = i
                    break
            else:
                index = len(self.objects)

            self.objects.insert(index, newObj)
            self._values.insert(index, newValue)

    def remove(self, *objects):
        """
        Remove objects from sorted list.
        """
        for removeObj in objects:
            if removeObj not in self.objects:
                continue

            index = self.objects.index(removeObj)
            del self.objects[index]
            del self._values[index]

def getIterable(obj):
    """
    Returns the iterable values of an object or False.
    Can be used for typechecking or iterating generic obj.

    Wrong way
    ---------
    >>> not getIterable(5)
    >>> True
    >>> not getIterable([])
    >>> True

    Right way
    ---------
    >>> getIterable(5) is False
    >>> True
    >>> getIterable([]) is False
    >>> False

    :param obj: Generic obj
    :return: Iterable list
    """
    if isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, list):
        return obj
    elif isinstance(obj, dict):
        return list(obj.values())
    else:
        return False

def isIterable(obj):
    """
    See if an obj is iterable or not, I kept using iterable function wrong.

    :param obj: Generic obj
    :rtype: bool
    """
    return getIterable(obj) is not False

def depth(obj):
    """
    Checks depths of an obj by keep going to the first value of obj.

    :param obj: Generic obj
    """
    depth = 0
    while True:
        if getIterable(obj):
            obj = iterFirstValue(obj)
            depth += 1
        else:
            return depth

def dictFirstValue(dictionary):
    """
    Get first 'random' value of a dictionary.

    :param dict dictionary: Generic dictionary
    :raises TypeError: If not dictionary
    """
    if not isinstance(dictionary, dict):
        raise TypeError("Not dictionary")

    if not dictionary:
        return None
    return dictionary[list(dictionary.keys())[0]]

def iterFirstValue(obj):
    """
    Get first 'random' value of an iterable.

    :param obj: Generic iterable
    :raises TypeError: If not iterable
    """
    if isIterable(obj) is False:
        raise TypeError("obj is not iterable")

    if isinstance(obj, tuple) or isinstance(obj, list):
        if not obj:
            return None
        else:
            return obj[0]
    elif isinstance(obj, dict):
        return dictFirstValue(obj)

def joinWithStr(delimeter, obj):
    """
    Like str.join() but it casts the values to strings first.

    :param obj: Generic iterable
    :param str delimeter: String to be put between values
    :raises TypeError: If obj is not iterable
    :return: A string containing values of obj with delimeter between each
    """
    if (obj := getIterable(obj)) is False:
        raise TypeError("obj is not iterable")

    return delimeter.join([str(value) for value in obj])

def addToListInDict(dictionary, key, value):
    """
    Add a value to a list inside a dictionary, if key doesn't exist then a new list is created.
    Since list is mutable we can change dictionary directly.

    :param dict dictionary:
    :param str key:
    :param any value:
    :return:
    """
    if key not in dictionary:
        dictionary[key] = [value]
    else:
        dictionary[key].append(value)



def _getRows_getRow(iterableObj, key=None):
    """
    Takes an object and returns a list of rows to use for appending.

    :param iterableObj: Iterable
    :param key: If iterableObj had a key to assigned it it's given here
    :return: A
    """
    row = [key] if key else []
    if isinstance(iterableObj, (list, tuple)):
        row.extend(iterableObj)
    elif isinstance(iterableObj, dict):
        for _, value in sorted(iterableObj.items()):
            row.append(value)
    return row

def getRows(obj):
    """
    All these objects result in [[1, 2, 3], [4, 5, 6]]
     | [[1, 2, 3], [4, 5, 6]]
     | [{"a": 1, "b": 2, "c": 3}, {"d": 4, "e": 5, "f": 6}]
     | {1: {"b": 2, "c": 3}, 4: {"e": 5, "f": 6}}
     | {1: [2, 3], 4: [5, 6]}

    :param any obj: Iterable (Optionally inside another iterable) or a value for a single cell
    :return:
    """
    rows = []
    if obj is None:
        return rows
    if isIterable(obj):
        if not len(obj):
            return rows

        if isinstance(obj, (list, tuple)):
            if isIterable(obj[0]):
                for subObj in obj:
                    rows.append(_getRows_getRow(subObj))
            else:
                rows.append(_getRows_getRow(obj))
        elif isinstance(obj, dict):
            if isIterable(dictFirstValue(obj)):
                for key, subObj in obj.items():
                    rows.append(_getRows_getRow(subObj, key))
            else:
                rows.append(_getRows_getRow(obj))
    else:
        rows.append([obj])
    return rows

from generallibrary.types import typeChecker








































































