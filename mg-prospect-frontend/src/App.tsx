import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Leads } from './pages/Leads';
import { Campaigns } from './pages/Campaigns';
import { CRM } from './pages/CRM';
import { Templates } from './pages/Templates';
import { Login } from './pages/Login';
import { ResetPassword } from './pages/ResetPassword';
import { InterestForm } from './pages/InterestForm';
import { Unsubscribe } from './pages/Unsubscribe';

function App() {
  const isAuthenticated = !!localStorage.getItem('mg_token');

  // Rotas públicas que não usam o Layout do sistema
  if (window.location.pathname.startsWith('/interesse') || window.location.pathname.startsWith('/unsubscribe')) {
      return (
          <BrowserRouter>
              <Routes>
                  <Route path="/interesse" element={<InterestForm />} />
                  <Route path="/interesse/:token" element={<InterestForm />} />
                  <Route path="/unsubscribe/:token" element={<Unsubscribe />} />
              </Routes>
          </BrowserRouter>
      );
  }

  if (!isAuthenticated) {
    if (window.location.pathname === '/reset-password') {
        return <ResetPassword />;
    }
    return <Login />;
  }

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/crm" element={<CRM />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
export default App;