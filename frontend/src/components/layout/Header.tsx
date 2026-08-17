import { BookOpen } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex h-14 max-w-5xl items-center px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          <span className="font-semibold text-foreground tracking-tight">AI Evaluation Engine</span>
        </div>
        <nav className="ml-auto flex items-center space-x-6 text-sm font-medium">
          <a href="#" className="text-foreground transition-colors hover:text-foreground/80">
            Evaluate
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
