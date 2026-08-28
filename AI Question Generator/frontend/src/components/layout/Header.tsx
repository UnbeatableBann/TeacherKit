import { BookOpen, History, X, Clock, FileText } from "lucide-react";
import { useState, useEffect } from "react";

export function Header() {
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (showHistory) {
      setHistory(JSON.parse(localStorage.getItem('generation_history') || '[]'));
    }
  }, [showHistory]);

  return (
    <>
      <header className="sticky top-0 z-50 glass-panel">
        <div className="mx-auto flex h-14 max-w-5xl items-center px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-indigo-600" />
            <span className="font-bold text-lg gradient-text tracking-tight">AI Question Generator</span>
          </div>
          <nav className="ml-auto flex items-center space-x-6 text-sm font-medium">
            <a href="#" className="text-foreground transition-colors hover:text-foreground/80">
              Generate
            </a>
            <button 
              onClick={() => setShowHistory(true)}
              className="text-muted-foreground transition-colors hover:text-foreground flex items-center gap-1"
            >
              <History className="w-4 h-4" />
              History
            </button>
            <a href="#" className="text-muted-foreground transition-colors hover:text-foreground">
              Settings
            </a>
          </nav>
        </div>
      </header>

      {/* History Modal */}
      {showHistory && (
        <div className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden">
            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
              <h2 className="font-semibold flex items-center gap-2">
                <Clock className="w-4 h-4 text-indigo-600" />
                Generation History
              </h2>
              <button onClick={() => setShowHistory(false)} className="p-1 hover:bg-gray-200 rounded-full text-gray-500">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4 overflow-y-auto flex-1 space-y-4">
              {history.length === 0 ? (
                <div className="text-center text-gray-400 py-10">
                  No history found. Generate some questions first!
                </div>
              ) : (
                history.map((item, i) => (
                  <div key={i} className="border border-gray-100 rounded-lg p-4 space-y-3 bg-white hover:shadow-sm transition-shadow">
                    <div className="flex justify-between items-start text-sm">
                      <div className="text-gray-500">
                        {new Date(item.timestamp).toLocaleString()}
                      </div>
                      <div className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded text-xs font-medium">
                        {item.response.generated_count} Questions
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-sm bg-gray-50 p-3 rounded-md">
                      <div><span className="text-gray-500">Subject:</span> {item.request.subject}</div>
                      <div><span className="text-gray-500">Class:</span> {item.request.class_level}</div>
                      <div><span className="text-gray-500">Topic:</span> {item.request.requested_topic || 'Any'}</div>
                      <div><span className="text-gray-500">Difficulty:</span> {item.request.requested_difficulty || 'Any'}</div>
                    </div>

                    <div className="space-y-1">
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">Source Documents</div>
                      {item.documents?.map((doc: any) => (
                        <div key={doc.document_id} className="flex items-center gap-1.5 text-sm text-gray-700">
                          <FileText className="w-3.5 h-3.5 text-blue-500" />
                          <span className="truncate">{doc.filename}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
