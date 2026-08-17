import { useState } from "react";
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

export function EvaluationForm({ onSubmit, isLoading }: EvaluationFormProps) {
  const [subject, setSubject] = useState<Subject>("science");
  const [classLevel, setClassLevel] = useState<ClassLevel>("std_8");
  const [category, setCategory] = useState<QuestionCategory>("subjective");
  const [type, setType] = useState<QuestionType>("explanation");
  
  const [questionText, setQuestionText] = useState("Explain why plants need sunlight for photosynthesis.");
  const [referenceText, setReferenceText] = useState("Plants use sunlight as an energy source to convert carbon dioxide and water into glucose, releasing oxygen.");
  const [expectedConcepts, setExpectedConcepts] = useState("energy source, convert carbon dioxide and water, glucose, releasing oxygen");
  const [studentAnswer, setStudentAnswer] = useState("Plants need sunlight to make food.");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const request: EvaluationRequest = {
      question: {
        id: "q" + Date.now(),
        text: questionText,
        subject,
        class_level: classLevel,
        category,
        type,
      },
      reference_answer: {
        text: referenceText,
        expected_concepts: expectedConcepts.split(",").map(c => c.trim()).filter(Boolean),
      },
      student_answer: {
        content: studentAnswer,
        source: "text",
      }
    };
    onSubmit(request);
  };

  return (
    <Card>
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
                <option value="explanation">Explanation</option>
                <option value="short_answer">Short Answer</option>
                <option value="proof">Proof</option>
                <option value="mcq">MCQ</option>
                <option value="numeric">Numeric</option>
                <option value="unit_based">Unit-based</option>
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
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Reference Answer</Label>
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
