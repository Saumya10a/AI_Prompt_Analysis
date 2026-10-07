import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Overview } from './pages/Overview';
import { Categories } from './pages/Categories';
import { Models } from './pages/Models';
import { Ecosystem } from './pages/Ecosystem';
import { Reconciliation } from './pages/Reconciliation';
import { PromptLab } from './pages/PromptLab';
import { BarChart3, Database, Activity, GitCompare, FileText, Server } from 'lucide-react';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Overview', icon: BarChart3 },
    { path: '/categories', label: 'Categories', icon: Database },
    { path: '/models', label: 'Models', icon: Activity },
    { path: '/ecosystem', label: 'Ecosystem', icon: Server },
    { path: '/reconciliation', label: 'Reconciliation', icon: GitCompare },
    { path: '/prompt-lab', label: 'Prompt Lab', icon: FileText },
  ];

  return (
    <nav className="bg-white border-b border-slate-200 px-4 py-4 sm:px-6">
      <div className="mx-auto max-w-7xl lg:flex lg:items-center lg:justify-between lg:gap-6">
        <div className="mb-3 flex items-center gap-2 lg:mb-0">
          <BarChart3 className="h-8 w-8 shrink-0 text-blue-600" />
          <h1 className="text-xl font-bold text-slate-900">BDA Analytics</h1>
        </div>
        <div className="grid grid-cols-2 gap-1 sm:grid-cols-3 lg:flex lg:flex-wrap lg:justify-end">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex min-h-10 items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 sm:px-3 lg:px-3 ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50">
        <Navigation />
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/models" element={<Models />} />
            <Route path="/ecosystem" element={<Ecosystem />} />
            <Route path="/reconciliation" element={<Reconciliation />} />
            <Route path="/prompt-lab" element={<PromptLab />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
