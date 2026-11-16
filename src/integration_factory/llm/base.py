"""Provider-agnostic LLM contract. Nodes depend on this, never on a vendor SDK."""
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    def complete(self, system: str, prompt: str) -> str:
        """Free-text completion."""
        ...

    def structured(self, system: str, prompt: str, schema: type[T]) -> T:
        """Completion constrained to a Pydantic schema (code constrains the LLM)."""
        ...
