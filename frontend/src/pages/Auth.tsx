import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Auth() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setLoading(true);
    // In a real app, this would hit /auth/login or similar to send OTP/Magic Link
    // For now, we simulate a login that gives a fake token after a delay
    setTimeout(() => {
      localStorage.setItem('bb_token', 'mock_jwt_token_for_' + email);
      localStorage.setItem('bb_user', email);
      setLoading(false);
      setSent(true);
      
      setTimeout(() => {
        navigate('/'); // Go back to landing to use the PromptEngine
      }, 1500);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#e8e8e8] text-[#111] font-sans selection:bg-black selection:text-white flex flex-col items-center justify-center relative overflow-hidden">
      
      {/* Navbar Minimal */}
      <nav className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-10 py-5">
        <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
          <div className="relative w-7 h-7 rounded-full border-[2px] border-[#111] flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-[#111] absolute -left-1 top-1/2 -translate-y-1/2" />
          </div>
          <span className="text-[15px] font-semibold tracking-[-0.02em] text-[#111]">
            Small Software Cloud
          </span>
        </button>
      </nav>

      {/* Auth Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="preview-panel p-10 flex flex-col items-center text-center">
          <h2 className="text-[clamp(24px,3vw,32px)] font-normal tracking-[-0.02em] text-[#222] mb-2">
            Welcome back
          </h2>
          <p className="text-[14px] text-[#777] mb-8">
            Enter your email to sign in or create an account
          </p>

          {!sent ? (
            <form onSubmit={handleLogin} className="w-full flex flex-col gap-4">
              <input
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-5 py-3 rounded-xl bg-white/70 border border-[#ddd] focus:outline-none focus:border-[#aaa] focus:bg-white text-[15px] transition-all"
              />
              <button 
                type="submit"
                disabled={loading}
                className="w-full px-5 py-3 rounded-xl bg-[#111] text-white text-[14px] font-medium hover:bg-[#333] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Continue with Email'}
              </button>
            </form>
          ) : (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full p-6 rounded-xl bg-[#e8ffe8] border border-[#b2e5b2] text-[#2a7a2a] text-[14px]"
            >
              <div className="font-semibold mb-1">Check your email</div>
              <div>We've sent a magic link to {email}</div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
