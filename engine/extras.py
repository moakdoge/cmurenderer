from __future__ import annotations

from types import GenericAlias
from typing import Any, Callable, Generic, Type, TypeVar, dataclass_transform, overload

T = TypeVar("T")
R = TypeVar("R")

_NOT_FOUND = object()


class cached_property(Generic[T, R]):
    func: Callable[[T], R]
    attrname: str | None
    __doc__: str | None
    __module__: str

    def __init__(self, func: Callable[[T], R]) -> None:
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    def __set_name__(self, owner: type[T], name: str) -> None:
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )

    @overload
    def __get__(self, instance: None, owner: type[T] | None = None) -> "cached_property[T, R]":
        ...

    @overload
    def __get__(self, instance: T, owner: type[T] | None = None) -> R:
        ...

    def __get__(
        self,
        instance: T | None,
        owner: type[T] | None = None,
    ) -> "R | cached_property[T, R]":
        if instance is None:
            return self

        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )

        try:
            cache: dict[str, Any] = instance.__dict__  # type: ignore[attr-defined]
        except AttributeError:
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None

        val = cache.get(self.attrname, _NOT_FOUND)

        if val is _NOT_FOUND:
            val = self.func(instance)
            try:
                cache[self.attrname] = val
            except TypeError:
                msg = (
                    f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                    f"does not support item assignment for caching "
                    f"{self.attrname!r} property."
                )
                raise TypeError(msg) from None

        return val

    __class_getitem__ = classmethod(GenericAlias)
    

from typing import TypeVar, Type, Callable, Any

T = TypeVar("T")




@dataclass_transform()
def dataclass(init: bool = True, frozen: bool = False, slots: bool = False, repr: bool = True):
    def decorator(cls):
        nonlocal frozen, slots, repr
        
        annotations = getattr(cls, "__annotations__", {})
        fields = tuple(annotations.keys())
        defaults = {}
        if slots:
            namespace = dict(cls.__dict__)

            namespace.pop("__dict__", None)
            namespace.pop("__weakref__", None)

            # Important: remove field defaults before creating slots,
            # because slot names conflict with class variables.
            for name in fields:
                if name in namespace:
                    defaults[name] = namespace.pop(name)
                    
            f=list(fields)
            f.append("_frozen")
            namespace["__slots__"] = tuple(f)
            class DataMeta(type):
                def __repr__(cls):
                    pretty = []
                    tags = [
                        "[FROZEN]" if frozen else "",
                        "[SLOTS]" if slots else "",
                        "[REPR]" if repr else "",
                        "[INIT]" if init else "",
                    ]
                    for k,v in annotations.items():
                        pretty.append(f"{k}: {v.__name__} = {defaults[k]}" if k in defaults else f"{k}: {getattr(v, '__name__', v)}")
                    return f"<dataclass {cls.__name__}({','.join(pretty)}) {' '.join(tags)}>"
                
            if repr:
                k = DataMeta
            else:
                k = type
            new_cls = k(cls.__name__, cls.__bases__, namespace, )
            new_cls.__module__ = cls.__module__
            new_cls.__qualname__ = cls.__qualname__


            cls = new_cls
        annotations = getattr(cls, "__annotations__", {})

        fields = list(annotations.keys())

        def __init__(self, *args, **kwargs):
            for name, value in zip(fields, args):
                setattr(self, name, value)
            for name in fields[len(args):]:
                if name in kwargs:
                    setattr(self, name, kwargs[name])
                elif hasattr(cls, name):
                    if slots:
                        setattr(self, name, defaults[name])
                    else:
                        setattr(self, name, getattr(cls, name))
                else:
                    raise TypeError(f"Missing required argument: {name}")

            
            setattr(self, "_frozen", True)
            if hasattr(self, "__post_init__") and callable(getattr(self, "__post_init__", None)):
                self.__post_init__()
            
                
        def __repr__(self):
            values = ", ".join(
                f"{name}={getattr(self, name)!r}"
                for name in fields
            )
            return f"{cls.__name__}({values})"

        if init:
            cls.__init__ = __init__
        if repr:
            cls.__repr__ = __repr__
        if frozen:
            def __setattr__(self, k, v):
                if hasattr(self, "_frozen"):
                    raise AttributeError(f"{self.__class__.__name__} is frozen!")
                object.__setattr__(self, k, v)
            cls.__setattr__ = __setattr__


        return cls
    return decorator