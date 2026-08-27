import { BookOpen } from "lucide-react";

export function Header() {
  return (
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
          <a href="#" className="text-muted-foreground transition-colors hover:text-foreground">
            History
          </a>
          <a href="#" className="text-muted-foreground transition-colors hover:text-foreground">
            Settings
          </a>
        </nav>
      </div>
    </header>
  );
}
