from typing import TypeVar, Generic

L = TypeVar('L')
R = TypeVar('R')


class Either(Generic[L, R]):
    def is_left(self): raise NotImplementedError()

    def is_right(self): raise NotImplementedError()

    def left(self) -> L: raise NotImplementedError()

    def right(self) -> R: raise NotImplementedError()


class Left(Either):
    def __init__(self, v): self.v = v

    def is_left(self): return True

    def is_right(self): return False

    def left(self): return self.v

    def right(self): return None


class Right(Either):
    def __init__(self, v): self.v = v

    def is_left(self): return False

    def is_right(self): return True

    def left(self): return None

    def right(self): return self.v
