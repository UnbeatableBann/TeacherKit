import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import ConversationView from './pages/ConversationView';
import CatalogueAdmin from './pages/CatalogueAdmin';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />}>
            <Route path="conversations/:id" element={<ConversationView />} />
          </Route>
          <Route path="/admin" element={<CatalogueAdmin />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
