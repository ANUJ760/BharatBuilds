import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import { Home } from './pages/Home';
import { AppView } from './pages/AppView';
import { Timeline } from './pages/Timeline';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/create" element={<Home />} />
        <Route path="/apps/:id" element={<AppView />} />
        <Route path="/apps/:id/timeline" element={<Timeline />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
