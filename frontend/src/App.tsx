import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import { Home } from './pages/Home';
import { AppView } from './pages/AppView';
import { Timeline } from './pages/Timeline';

import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/create" element={<Home />} />
        <Route path="/app/:id" element={<AppView />} />
        <Route path="/timeline/:id" element={<Timeline />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
