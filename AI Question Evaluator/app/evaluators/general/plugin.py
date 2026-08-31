from app.evaluators.base import SubjectPlugin
from app.strategies.core import (
    ConceptStrategy,
    ExactStrategy,
    NumericStrategy,
    OptionStrategy,
    SecurityStrategy,
    Strategy,
    UnitBasedStrategy,
)
from app.strategies.llm import LLMStrategy


class GeneralPlugin(SubjectPlugin):
    name = "general"

    @property
    def strategies(self) -> list[Strategy]:
        return [
            SecurityStrategy(),
            OptionStrategy(),
            ExactStrategy(),
            NumericStrategy(),
            ConceptStrategy(),
            LLMStrategy(),
            UnitBasedStrategy(),
        ]
