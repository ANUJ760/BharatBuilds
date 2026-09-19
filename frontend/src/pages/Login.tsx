import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

export default function Login() {
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setLoading(true);
    // Simulate sending OTP via Cognito
    setTimeout(() => {
      setLoading(false);
      setStep('otp');
    }, 1000);
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp) return;

    setLoading(true);
    // Simulate verifying OTP and getting tokens
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
            {step === 'email' ? 'Enter your email to sign in or create an account' : `Enter the 6-digit code sent to ${email}`}
          </p>

          <AnimatePresence mode="wait">
            {step === 'email' ? (
              <motion.form 
                key="email-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                onSubmit={handleSendCode} 
                className="w-full flex flex-col gap-4"
              >
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
                  {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Send Code'}
                </button>
              </motion.form>
            ) : (
              <motion.form 
                key="otp-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                onSubmit={handleVerify} 
                className="w-full flex flex-col gap-4"
              >
                <input
                  type="text"
                  placeholder="000000"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  required
                  className="w-full px-5 py-3 rounded-xl bg-white/70 border border-[#ddd] focus:outline-none focus:border-[#aaa] focus:bg-white text-[24px] text-center tracking-[0.5em] font-mono transition-all"
                />
                <button 
                  type="submit"
                  disabled={loading || otp.length < 6}
                  className="w-full px-5 py-3 rounded-xl bg-[#111] text-white text-[14px] font-medium hover:bg-[#333] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Verify'}
                </button>
                <button
                  type="button"
                  onClick={() => setStep('email')}
                  className="text-[13px] text-[#555] hover:text-[#111] mt-2 transition-colors"
                >
                  Use a different email
                </button>
              </motion.form>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
