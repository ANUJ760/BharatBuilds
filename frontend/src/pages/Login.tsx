import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';
import { Logo } from '../components/imagica/Logo';
import { loginWithCognito } from '../api/auth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    
    setLoading(true);
    setError(null);
    try {
      await loginWithCognito(email, password);
      setLoading(false);
      
      const params = new URLSearchParams(window.location.search);
      const returnUrl = params.get('return') || '/';
      navigate(returnUrl);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || 'Login failed');
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen bg-[#f8f9fa] text-[#111] font-sans selection:bg-black selection:text-white flex flex-col items-center justify-center relative overflow-hidden z-[100]"
    >
      <Scene3D />
      
      {/* Navbar Minimal */}
      <nav className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-10 py-5">
        <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
          <Logo />
          <span className="text-[15px] font-semibold tracking-[-0.02em] text-[#111] drop-shadow-sm bg-white/30 px-2 py-0.5 rounded-md backdrop-blur-md">
            Small Software Cloud
          </span>
        </button>
      </nav>

      {/* Auth Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10 pointer-events-none"
      >
        <div className="pointer-events-auto p-10 flex flex-col items-center text-center bg-white/60 backdrop-blur-2xl border border-white/50 shadow-2xl rounded-3xl">
          <h2 className="text-[clamp(24px,3vw,32px)] font-medium tracking-tight text-[#111] mb-2 drop-shadow-sm">
            Welcome to Small Software Cloud
          </h2>
          <p className="text-[14px] text-gray-600 mb-2 font-medium">
            Sign in to build, deploy and manage your small software.
          </p>

          {error && (
            <div className="w-full p-3 mb-4 bg-red-50 text-red-600 rounded-xl text-sm border border-red-100">
              {error}
            </div>
          )}

          <form 
            onSubmit={handleLogin} 
            className="w-full flex flex-col gap-4 mt-6"
          >
            <input
              type="email"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-5 py-3.5 rounded-xl bg-white/70 border border-white/80 focus:outline-none focus:ring-2 focus:ring-black/5 focus:bg-white text-[15px] shadow-sm transition-all"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-5 py-3.5 rounded-xl bg-white/70 border border-white/80 focus:outline-none focus:ring-2 focus:ring-black/5 focus:bg-white text-[15px] shadow-sm transition-all"
            />
            <button 
              type="submit"
              disabled={loading}
              className="w-full px-5 py-3.5 rounded-xl bg-[#111] text-white text-[14px] font-medium shadow-xl shadow-black/10 hover:shadow-black/20 hover:-translate-y-0.5 hover:bg-[#000] transition-all disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-2"
            >
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Sign In'}
            </button>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
}
