import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/select";
import type { EvaluationRequest, QuestionCategory, Subject, ClassLevel, QuestionType } from "@/types";

interface EvaluationFormProps {
  onSubmit: (request: EvaluationRequest) => void;
  isLoading: boolean;
}

const CATEGORY_TYPES: Record<QuestionCategory, { value: QuestionType; label: string }[]> = {
  subjective: [
    { value: "explanation", label: "Explanation" },
    { value: "short_answer", label: "Short Answer" },
    { value: "descriptive", label: "Descriptive" },
    { value: "essay", label: "Essay" },
    { value: "proof", label: "Proof" },
    { value: "derivation", label: "Derivation" },
  ],
  objective: [
    { value: "exact_answer", label: "Exact Answer" },
    { value: "mcq", label: "MCQ" },
    { value: "multiple_select", label: "Multiple Select" },
    { value: "true_false", label: "True / False" },
    { value: "fill_in_the_blank", label: "Fill in the Blank" },
  ],
  numerical: [
    { value: "numeric", label: "Numeric" },
    { value: "formula", label: "Formula" },
    { value: "unit_based", label: "Unit-based" },
  ],
};

export function EvaluationForm({ onSubmit, isLoading }: EvaluationFormProps) {
  const [subject, setSubject] = useState<Subject>("science");
  const [classLevel, setClassLevel] = useState<ClassLevel>("std_8");
  const [category, setCategory] = useState<QuestionCategory>("subjective");
  const [type, setType] = useState<QuestionType>("explanation");
  
  const [questionText, setQuestionText] = useState("Explain why plants need sunlight for photosynthesis.");
  const [referenceText, setReferenceText] = useState("Plants use sunlight as an energy source to convert carbon dioxide and water into glucose, releasing oxygen.");
  const [expectedConcepts, setExpectedConcepts] = useState("energy source, convert carbon dioxide and water, glucose, releasing oxygen");
  const [studentAnswer, setStudentAnswer] = useState("Plants need sunlight to make food.");
  
  // New state for MCQ options
  const [mcqOptions, setMcqOptions] = useState("A: True\nB: False");
  const [correctOptionIds, setCorrectOptionIds] = useState("A");

  // Sync category and type
  useEffect(() => {
    const allowedTypes = CATEGORY_TYPES[category].map(t => t.value);
    if (!allowedTypes.includes(type)) {
      setType(allowedTypes[0]);
    }
  }, [category, type]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    let parsedOptions = undefined;
    if (type === "mcq" || type === "multiple_select") {
       parsedOptions = mcqOptions.split("\n").filter(Boolean).map((line, idx) => {
         const parts = line.split(":");
         return {
           id: parts[0]?.trim() || String(idx),
           text: parts.slice(1).join(":").trim() || line
         };
       });
       // Ensure at least 2 options for validation
       if (parsedOptions.length < 2) {
           parsedOptions.push({ id: "dummy1", text: "Dummy Option 1" });
           parsedOptions.push({ id: "dummy2", text: "Dummy Option 2" });
       }
    }

    const request: EvaluationRequest = {
      question: {
        id: "q" + Date.now(),
        text: questionText,
        subject,
        class_level: classLevel,
        category,
        type,
        ...(parsedOptions ? { options: parsedOptions } : {})
      },
      reference_answer: {
        text: referenceText,
        expected_concepts: expectedConcepts.split(",").map(c => c.trim()).filter(Boolean),
        ...(type === "mcq" || type === "multiple_select" ? { correct_option_ids: correctOptionIds.split(",").map(id => id.trim()) } : {})
      },
      student_answer: {
        content: studentAnswer,
        source: "text",
      }
    };
    onSubmit(request);
  };

  const isOptionType = type === "mcq" || type === "multiple_select";

  return (
    <Card className="glass-panel">
      <CardHeader>
        <CardTitle>Evaluate Student Answer</CardTitle>
        <CardDescription>Enter the evaluation rubric and the student's response below.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Subject</Label>
              <NativeSelect value={subject} onChange={e => setSubject(e.target.value as Subject)}>
                <option value="mathematics">Mathematics</option>
                <option value="science">Science</option>
                <option value="english">English</option>
                <option value="history">History</option>
                <option value="general">General</option>
              </NativeSelect>
            </div>
            <div className="space-y-2">
              <Label>Class Level</Label>
              <NativeSelect value={classLevel} onChange={e => setClassLevel(e.target.value as ClassLevel)}>
                <option value="std_5">Std 5</option>
                <option value="std_8">Std 8</option>
                <option value="std_10">Std 10</option>
                <option value="std_12">Std 12</option>
                <option value="ug">Undergrad</option>
              </NativeSelect>
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <NativeSelect value={category} onChange={e => setCategory(e.target.value as QuestionCategory)}>
                <option value="subjective">Subjective</option>
                <option value="objective">Objective</option>
                <option value="numerical">Numerical</option>
              </NativeSelect>
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <NativeSelect value={type} onChange={e => setType(e.target.value as QuestionType)}>
                {CATEGORY_TYPES[category].map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </NativeSelect>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-border">
            <div className="space-y-2">
              <Label>Question</Label>
              <Textarea 
                value={questionText}
                onChange={e => setQuestionText(e.target.value)}
                required
                className="h-20"
              />
            </div>
            
            {isOptionType && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-muted/50 p-4 rounded-md">
                <div className="space-y-2">
                  <Label>Options (Format: ID: Text)</Label>
                  <Textarea 
                    value={mcqOptions}
                    onChange={e => setMcqOptions(e.target.value)}
                    className="h-24"
                    placeholder="A: Option 1&#10;B: Option 2"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Correct Option IDs (Comma-separated)</Label>
                  <Textarea 
                    value={correctOptionIds}
                    onChange={e => setCorrectOptionIds(e.target.value)}
                    className="h-24"
                    placeholder="A, B"
                  />
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Reference Answer / Text</Label>
                <Textarea 
                  value={referenceText}
                  onChange={e => setReferenceText(e.target.value)}
                  className="h-32"
                  placeholder="Expected correct answer..."
                />
              </div>
              <div className="space-y-2">
                <Label>Expected Concepts (Comma-separated)</Label>
                <Textarea 
                  value={expectedConcepts}
                  onChange={e => setExpectedConcepts(e.target.value)}
                  className="h-32"
                  placeholder="concept 1, concept 2..."
                />
              </div>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-border">
            <div className="space-y-2">
              <Label>Student Answer</Label>
              <Textarea 
                value={studentAnswer}
                onChange={e => setStudentAnswer(e.target.value)}
                required
                className="h-32 bg-secondary/30"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button type="submit" disabled={isLoading} className="w-full md:w-auto">
              {isLoading ? "Evaluating Answer..." : "Evaluate Answer"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
