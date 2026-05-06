from __future__ import annotations

from types import GenericAlias
from typing import Any, Callable, Generic, TypeVar, overload

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