from enum import StrEnum


class ClassLevel(StrEnum):
    STD_1 = "std_1"
    STD_2 = "std_2"
    STD_3 = "std_3"
    STD_4 = "std_4"
    STD_5 = "std_5"
    STD_6 = "std_6"
    STD_7 = "std_7"
    STD_8 = "std_8"
    STD_9 = "std_9"
    STD_10 = "std_10"
    STD_11 = "std_11"
    STD_12 = "std_12"
    UG = "ug"


class Subject(StrEnum):
    MATHEMATICS = "mathematics"
    SCIENCE = "science"
    ENGLISH = "english"
    HISTORY = "history"
    GENERAL = "general"


class QuestionCategory(StrEnum):
    OBJECTIVE = "objective"
    NUMERICAL = "numerical"
    SUBJECTIVE = "subjective"


class QuestionType(StrEnum):
    MCQ = "mcq"
    MULTIPLE_SELECT = "multiple_select"
    TRUE_FALSE = "true_false"
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    EXACT_ANSWER = "exact_answer"
    NUMERIC = "numeric"
    FORMULA = "formula"
    UNIT_BASED = "unit_based"
    SHORT_ANSWER = "short_answer"
    EXPLANATION = "explanation"
    DESCRIPTIVE = "descriptive"
    ESSAY = "essay"
    PROOF = "proof"
    DERIVATION = "derivation"


class AnswerSource(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"


class EvaluationStatus(StrEnum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    INSUFFICIENT_REFERENCE = "insufficient_reference"
    EVALUATION_FAILURE = "evaluation_failure"


class EvidenceStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
