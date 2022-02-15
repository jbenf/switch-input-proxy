from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar


class State(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context



T = TypeVar('T', bound=State)

class Context(Generic[T]):
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state: T
    """
    A reference to the current state of the Context.
    """

    def __init__(self, state: T) -> None:
        self.transition_to(state)

    def transition_to(self, state: T):
        """
        The Context allows changing the State object at runtime.
        """

        self._state = state
        self._state.context = self




