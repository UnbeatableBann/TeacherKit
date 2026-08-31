from app.evaluators.base import SubjectPlugin
from app.strategies.core import (
    ConceptStrategy,
    ExactStrategy,
    GrammarStrategy,
    OptionStrategy,
    SecurityStrategy,
    Strategy,
    UnitBasedStrategy,
)
from app.strategies.llm import LLMStrategy


class EnglishPlugin(SubjectPlugin):
    name = "english"

    @property
    def strategies(self) -> list[Strategy]:
        return [
            SecurityStrategy(),
            OptionStrategy(),
            ExactStrategy(),
            ConceptStrategy(),
            GrammarStrategy(),
            LLMStrategy(),
            UnitBasedStrategy(),
        ]
