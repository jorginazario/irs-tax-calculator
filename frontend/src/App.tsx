import { Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar.tsx';
import CalculatorPage from './pages/CalculatorPage.tsx';
import HistoryPage from './pages/HistoryPage.tsx';
import AnalyticsPage from './pages/AnalyticsPage.tsx';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white shadow-sm">
        <div className="mx-auto max-w-4xl px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            IRS Tax Calculator
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Federal income tax estimation for Tax Year 2024
          </p>
        </div>
      </header>

      <NavBar />

      <Routes>
        <Route path="/" element={<CalculatorPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </div>
  );
}

export default App;
