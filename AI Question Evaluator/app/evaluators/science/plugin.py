from app.evaluators.base import SubjectPlugin
from app.strategies.core import (
    ConceptStrategy,
    ExactStrategy,
    OptionStrategy,
    Strategy,
    UnitBasedStrategy,
)
from app.strategies.llm import LLMStrategy


class SciencePlugin(SubjectPlugin):
    name = "science"

    @property
    def strategies(self) -> list[Strategy]:
        return [
            OptionStrategy(),
            ExactStrategy(),
            ConceptStrategy(),
            LLMStrategy(),
            UnitBasedStrategy(),
        ]
