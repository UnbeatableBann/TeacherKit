import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { cn } from '../lib/utils';

export default function Layout() {
  const location = useLocation();
  const isFollowUpActive = location.pathname === '/' || location.pathname.startsWith('/conversations');

  return (
    <div className="flex flex-col h-screen w-full bg-slate-50 text-slate-900">
      <header className="flex-shrink-0 bg-white border-b border-slate-200">
        <div className="px-6 py-3 border-b border-slate-100">
          <h1 className="text-xl font-bold text-slate-900">AI Sales Assistant</h1>
        </div>
        <nav className="flex px-4">
          <NavLink
            to="/"
            className={
              cn(
                "px-4 py-3 text-sm font-medium border-b-2 transition-colors",
                isFollowUpActive
                  ? "border-[var(--color-primary)] text-[var(--color-primary)]"
                  : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
              )
            }
          >
            Generate Follow-up
          </NavLink>
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              cn(
                "px-4 py-3 text-sm font-medium border-b-2 transition-colors",
                isActive
                  ? "border-[var(--color-primary)] text-[var(--color-primary)]"
                  : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
              )
            }
          >
            Knowledge Base
          </NavLink>
        </nav>
      </header>
      <main className="flex-1 flex overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
