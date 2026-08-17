# V1 Architecture

```text
Text -> StudentAnswer normalization -> Evaluation Engine -> Subject Plugin
     -> Answer/Domain Strategies -> Evidence -> Error Diagnosis
     -> Score -> Structured Result
```

Future image/OCR/handwriting and voice/ASR are input-side processors only. They
will normalize into `StudentAnswer`; the evaluator remains modality-agnostic.

Question taxonomy:
- Objective: MCQ, Multiple Select, True/False, Fill in the Blank, Exact Answer
- Numerical: Numeric, Formula, Unit-based
- Subjective: Short Answer, Explanation, Descriptive, Essay, Proof, Derivation

Subject plugins: Mathematics, Science, English, History, General.

The engine is intentionally not a direct LLM judge. Deterministic and
subject-specific strategies provide evidence; semantic/reasoning capabilities
can later be added behind the strategy boundary.
