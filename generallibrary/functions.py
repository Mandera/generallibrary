import inspect
import re


class SigInfo:
    """
    Get info regarding a signature.
    Also useful for handling decorators.
    Unforgiving as it sets missing values to None.
    """
    def __init__(self, callableObject, *args, **kwargs):
        assert callable(callableObject)

        self.callableObject = callableObject
        # self.args = [] if args is None else list(args)
        # self.kwargs = {} if kwargs is None else kwargs.copy()

        # Stores *args and **kwargs indirectly in their own object if they exist
        # Can have missing parameters
        self.allArgs = {}

        # Normal arg
        for i, name in enumerate(self.positionalArgNames):
            if i >= len(args):
                break
            self.allArgs[name] = args[i]

        # Extract *args
        if self.packedArgsName:
            self.allArgs[self.packedArgsName] = []
        if len(args) > len(self.positionalArgNames):
            if not self.packedArgsName:
                raise AttributeError("Too many args without a packed *args parameter")

            self.allArgs[self.packedArgsName] = args[len(self.positionalArgNames):]


        if self.packedKwargsName:
            self.allArgs[self.packedKwargsName] = {}

        for name, value in kwargs.items():
            # Normal kwarg
            if name in self.names:
                self.allArgs[name] = value

            # Extract **kwargs
            else:
                if not self.packedKwargsName:
                    raise AttributeError("Too many kwargs without a packed **kwargs parameter")
                self.allArgs[self.packedKwargsName[0]][name] = value



    # ========= Level 1 - SIGNATURE PARAMETERS =========

    @property
    def parameters(self):
        """Get list of inspect parameter objects"""
        return inspect.signature(self.callableObject).parameters.values()

    @property
    def names(self):
        """Get list of parameter names"""
        return [param.name for param in self.parameters]

    @property
    def namesWithoutDefaults(self):
        """Get list of parameter names except those ones that have a default value"""
        return [param.name for param in self.parameters if param.name not in self.defaults]

    @property
    def namesWithoutPacked(self):
        """Get list of parameter names except *args or **kwargs"""
        return [param.name for param in self.parameters if param.name not in (self.packedArgsName + self.packedKwargsName)]

    @property
    def leadingArgNames(self):
        """
        Get names leading args that don't have default value.
        '*args' wont be included.
        'self' wont be included.
        """
        leadingArgNames = []
        for param in self.parameters:
            noDefault = param.default is inspect.Parameter.empty
            notSelf = param.name != "self"
            includedKind = param.kind.name in ("POSITIONAL_OR_KEYWORD", "POSITIONAL_ONLY")
            if not (noDefault and notSelf and includedKind):
                break
            leadingArgNames.append(param.name)
        return leadingArgNames

    @property
    def packedArgsName(self):
        """Get name of packed *args or None"""
        for param in self.parameters:
            if param.kind.name == "VAR_POSITIONAL":
                return param.name

    @property
    def packedKwargsName(self):
        """Get name of packed *kwargs or None"""
        for param in self.parameters:
            if param.kind.name == "VAR_KEYWORD":
                return param.name

    @property
    def defaults(self):
        """Get dict of default values"""
        d = {param.name: param.default for param in self.parameters if param.default is not param.empty}

        if "self" in self.names and "self" not in d:
            d["self"] = self.callableObject

        return d

    @property
    def positionalArgNames(self):
        """
        Get list of parameter names that can take a positional argument.
        `*args` included.
        """
        return [param.name for param in self.parameters if param.kind.name in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD", "VAR_POSITIONAL")]

    @property
    def keywordArgNames(self):
        """
        Get list of parameter names that can only take a keyword argument.
        Opposite of `self.positionalArgNames`.
        `**kwargs` included.
        """
        return [name for name in self.names if name not in self.positionalArgNames]

    def getIndexFromName(self, name):
        """Get index from name if name exists, else None"""
        if name in self.names:
            return self.names.index(name)

    # ========= Level 2 =========

    @property
    def unpackedArgs(self):
        """Return a list of all positional parameter values"""
        args = []
        for name in self.positionalArgNames:
            if name == self.packedArgsName:
                args.extend(self[self.packedArgsName])
            else:
                args.append(self[name])
        return args

    @property
    def unpackedKwargs(self):
        """Return a dict of parameters with their values excluding those in positionalArgNames / unpackedArgs"""
        kwargs = {}
        for name in self.keywordArgNames:
            if name == self.packedKwargsName:
                kwargs.update(self[self.packedKwargsName])
            else:
                kwargs[name] = self[name]
        return kwargs

    @property
    def unpackedAllArgs(self):
        """
        Return a dict with all parameters and their values.
        Entire *args and **kwargs objects will be included as well as unpacked **kwargs.
        Which means there are duplicate values if **kwargs is not empty.
        Missing values are set to None.
        """
        kwargs = {}
        for name in self.names:
            if name in self.allArgs:
                kwargs[name] = self.allArgs[name]

                if name == self.packedKwargsName:
                    kwargs.update(self.allArgs[name])

            elif name in self.defaults:
                kwargs[name] = self.defaults[name]

            else:
                kwargs[name] = None

        return kwargs


    # def validParameters(self):
    #     """Check if a call can be made by checking all if all required parameters are defined"""
    #     for name in self.names:
    #         if name == self.packedKwargsName:
    #             continue
    #         if name == self.packedArgsName:
    #             continue
    #         if name in self.defaults:
    #             continue
    #         if self[name] is None:
    #             raise AttributeError(f"{self} does not have valid parameters, it's missing {name}")

    # ========= Level 3 =========

    def __getitem__(self, name):
        """Get value of a parameter from unpackedAllArgs, otherwise None"""
        if name in self.unpackedAllArgs:
            return self.unpackedAllArgs[name]

    def __setitem__(self, name, value):
        if name not in self.names and self.packedKwargsName is None:
            raise AttributeError(f"Cannot set parameter '{name}' as there is no parameter with that name nor is there a packed kwargs parameter.")

        if name in self.allArgs:
            if name == self.packedArgsName and not isinstance(value, (tuple, list)):
                raise AttributeError(f"Packed args parameter value has to be list or tuple.")
            if name == self.packedKwargsName and not isinstance(value, dict):
                raise AttributeError(f"Packed kwargs parameter value has to be a dict.")

            self.allArgs[name] = value

        elif name in self.names:
            self.allArgs[name] = value

        elif self.packedKwargsName:
            self.allArgs[self.packedKwargsName][name] = value

    def __call__(self):
        """
        Calls callableObject with filled args and kwargs.
        Unfilled required parameters will get a None value
        """
        return self.callableObject(*self.unpackedArgs, **self.unpackedKwargs)

    def setParameters(self, /, **parameters):
        """Set parameters automatically in args or kwargs if the name exists in self.names."""
        for name, value in parameters.items():
            self[name] = value
        return self

    # ========= Other =========

    def copy(self):
        """Return a copy of this SigInfo"""
        return SigInfo(**attributes(self))

    def __repr__(self):
        return f"<SigInfo for '{self.callableObject.__class__.__name__}' with names '{', '.join(self.names)}'>"



ignore = ["+", "-", "*", "/", "(", ")", "sqrt"]
def _tokenize(expression):
    """
    Tokenize an expression
    Taken from https://stackoverflow.com/questions/61948141/python-function-from-mathematical-expression-string/61949248
    """
    return re.findall(r"(\b\w*[.]?\w+\b|[()+*\-/])", expression)

def calculate(expression, *args):
    """
    Calculate function which can take any expression. Enter args in the order that they appear.
    """
    seenArgs = {}
    newTokens = []
    tokens = _tokenize(expression)
    for token in tokens:
        try:
            float(token)
        except ValueError:
            tokenIsFloat = False
        else:
            tokenIsFloat = True

        if token in ignore or tokenIsFloat:
            newTokens.append(token)
        else:
            if token not in seenArgs:
                seenArgs[token] = str(args[len(seenArgs)])
            newTokens.append(seenArgs[token])
    return eval("".join(newTokens))

def defaults(dictionary, overwriteNone=False, **kwargs):
    """
    Overwrite kwargs with dictionary.
    Returns given dictionary with values updated by kwargs unless they already existed.

    :param dict dictionary:
    :param overwriteNone: Whether to overwrite None values or not.
    :param kwargs:
    """
    for key, value in dictionary.items():
        dictValueIsNone = value is None
        kwargsHasValue = key in kwargs
        if overwriteNone and dictValueIsNone and kwargsHasValue:
            continue

        # Overwrite kwargs with dictionary
        kwargs[key] = value

    return kwargs




from generallibrary.object import attributes
































