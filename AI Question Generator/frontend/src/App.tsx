
import { Header } from '@/components/layout/Header';
import { GeneratorPage } from '@/pages/GeneratorPage';

function App() {
  return (
    <div className="min-h-screen animated-gradient-bg flex flex-col">
      <Header />
      <main className="flex-1">
        <GeneratorPage />
      </main>
    </div>
  );
}

export default App;
