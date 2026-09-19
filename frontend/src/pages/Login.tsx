import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';

export default function Login() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setLoading(true);
    // Directly log in (Mocking)
    setTimeout(() => {
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      if (!isLocalhost) {
        localStorage.setItem('bb_token', 'mock_jwt_token_for_' + email);
        localStorage.setItem('bb_user', email);
      } else {
        sessionStorage.setItem('bb_token', 'mock_jwt_token_for_' + email);
        sessionStorage.setItem('bb_user', email);
      }
      setLoading(false);
      
      // Redirect back to return URL or home
      const params = new URLSearchParams(window.location.search);
      const returnUrl = params.get('return') || '/';
      navigate(returnUrl);
    }, 1000);
  };

  return (
    <motion.div 
      initial={{ y: "15vh", opacity: 0 }} 
      animate={{ y: 0, opacity: 1 }} 
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="min-h-screen bg-[#f8f9fa] text-[#111] font-sans selection:bg-black selection:text-white flex flex-col items-center justify-center relative overflow-hidden"
    >
      <Scene3D />
      
      {/* Navbar Minimal */}
      <nav className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-10 py-5">
        <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
          <div className="relative w-7 h-7 rounded-full border-[2px] border-[#111] flex items-center justify-center bg-white/50 backdrop-blur-md">
            <div className="w-1.5 h-1.5 rounded-full bg-[#111] absolute -left-1 top-1/2 -translate-y-1/2" />
          </div>
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
          <p className="text-[13px] text-gray-500 mb-8">
            Enter your email to receive a secure login code.
          </p>

          <form 
            onSubmit={handleLogin} 
            className="w-full flex flex-col gap-4"
          >
            <input
              type="email"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-5 py-3.5 rounded-xl bg-white/70 border border-white/80 focus:outline-none focus:ring-2 focus:ring-black/5 focus:bg-white text-[15px] shadow-sm transition-all"
            />
            <button 
              type="submit"
              disabled={loading}
              className="w-full px-5 py-3.5 rounded-xl bg-[#111] text-white text-[14px] font-medium shadow-xl shadow-black/10 hover:shadow-black/20 hover:-translate-y-0.5 hover:bg-[#000] transition-all disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-2"
            >
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Continue'}
            </button>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
}
