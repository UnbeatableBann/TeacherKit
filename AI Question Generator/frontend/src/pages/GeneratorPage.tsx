import { useState, useEffect } from 'react';
import { DocumentUploader } from '@/components/generator/DocumentUploader';
import { GenerationForm } from '@/components/generator/GenerationForm';
import { ExamplePrompts } from '@/components/generator/ExamplePrompts';
import { QuestionList } from '@/components/generator/QuestionList';
import { uploadDocument, getDocumentStatus, generateQuestions } from '@/lib/api';
import { DocumentResponse, GenerationRequest, GenerationResponse } from '@/types';
import { AlertCircle, FileText } from 'lucide-react';

export function GeneratorPage() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [config, setConfig] = useState<Partial<GenerationRequest>>({
    total_questions: 10,
    requested_difficulty: 'Medium'
  });
  
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  // Polling logic for processing documents
  useEffect(() => {
    const processingDocs = documents.filter(d => d.status === 'processing' || d.status === 'uploaded');
    if (processingDocs.length === 0) return;

    const interval = setInterval(() => {
      processingDocs.forEach(async (doc) => {
        try {
          const status = await getDocumentStatus(doc.document_id);
          setDocuments(prev => prev.map(d => d.document_id === status.document_id ? status : d));
        } catch (e) {
          console.error("Failed to poll status for", doc.document_id);
        }
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [documents]);

  const handleFileSelect = async (file: File) => {
    // Optimistic UI update
    const tempId = `temp_${Date.now()}_${file.name}`;
    setDocuments(prev => [...prev, { document_id: tempId, filename: file.name, status: 'uploading', uploadProgress: 0 }]);
    
    try {
      const response = await uploadDocument(file, (progress) => {
        setDocuments(prev => prev.map(d => 
          d.document_id === tempId ? { ...d, status: 'uploading', uploadProgress: progress } : d
        ));
      });
      // Replace temp document with real one
      setDocuments(prev => prev.map(d => d.document_id === tempId ? response : d));
    } catch (err) {
      setDocuments(prev => prev.map(d => d.document_id === tempId ? { ...d, status: 'failed' } : d));
      setGlobalError(`Failed to upload ${file.name}`);
    }
  };

  const handleRemoveDocument = (docId: string) => {
    setDocuments(prev => prev.filter(d => d.document_id !== docId));
  };

  const handleConfigChange = (updates: Partial<GenerationRequest>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const areDocumentsReady = documents.length > 0 && documents.every(d => d.status === 'ready');
  const isValidConfig = !!(config.subject && config.class_level && config.total_questions && config.total_questions > 0);

  const handleGenerate = async () => {
    if (!areDocumentsReady || !isValidConfig) return;
    
    setIsGenerating(true);
    setGlobalError(null);
    setResult(null);

    const request: GenerationRequest = {
      document_ids: documents.filter(d => d.status === 'ready').map(d => d.document_id),
      subject: config.subject!,
      class_level: config.class_level!,
      total_questions: config.total_questions!,
      requested_topic: config.requested_topic,
      requested_difficulty: config.requested_difficulty as any
    };

    try {
      const response = await generateQuestions(request);
      setResult(response);
    } catch (err) {
      setGlobalError(err instanceof Error ? err.message : "Failed to generate questions");
    } finally {
      setIsGenerating(false);
    }
  };

  let validationError = "";
  if (documents.length > 0 && !areDocumentsReady) {
    validationError = "Please wait for all documents to finish processing.";
  } else if (!isValidConfig && documents.length > 0) {
    validationError = "Please fill in all required fields (Subject, Class, Count).";
  } else if (documents.length === 0) {
    validationError = "Upload at least one document.";
  }

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-500">
      
      {/* Intro */}
      <div className="text-center space-y-2 mb-10">
        <h1 className="text-3xl font-bold text-foreground">AI Question Generator</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Generate new questions based on previous-year examination papers while preserving their topic, difficulty, marks, and question patterns.
        </p>
      </div>

      {globalError && (
        <div className="bg-error-bg border border-error-border rounded-lg p-4 flex items-start gap-3 animate-in fade-in">
          <AlertCircle className="h-5 w-5 text-error shrink-0 mt-0.5" />
          <div className="text-sm text-error/90 font-medium">
            {globalError}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-5 space-y-6">
          <div className="card-container p-6 bg-white">
            <DocumentUploader 
              documents={documents} 
              onFileSelect={handleFileSelect} 
              onRemove={handleRemoveDocument} 
            />
          </div>
          
          <ExamplePrompts onSelect={handleConfigChange} />
        </div>

        <div className="lg:col-span-7 space-y-8">
          <GenerationForm 
            config={config} 
            onChange={handleConfigChange} 
            onSubmit={handleGenerate}
            isGenerating={isGenerating}
            canGenerate={areDocumentsReady && isValidConfig}
            validationError={validationError}
          />

          {!result && !isGenerating && (
            <div className="h-48 flex flex-col items-center justify-center border border-dashed border-border rounded-lg bg-card/50 text-muted-foreground text-sm p-6 text-center">
              <FileText className="w-8 h-8 mb-2 opacity-40" />
              <p>Configure parameters and generate to see questions.</p>
            </div>
          )}

          {isGenerating && (
            <div className="space-y-6 animate-pulse mt-8">
              <div className="h-32 bg-card border border-border rounded-lg"></div>
              <div className="h-40 bg-card border border-border rounded-lg"></div>
              <div className="h-32 bg-card border border-border rounded-lg"></div>
            </div>
          )}

          {result && !isGenerating && (
            <div className="mt-8">
              <QuestionList response={result} />
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
