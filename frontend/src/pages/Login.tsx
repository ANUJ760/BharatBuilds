import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';
import { Logo } from '../components/imagica/Logo';
import { loginWithCognito, confirmRegistration } from '../api/auth';

export default function Login() {
  const [step, setStep] = useState<'login' | 'verify'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
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
      if (err.code === 'UserNotConfirmedException' || err.name === 'UserNotConfirmedException' || err.message?.includes('not confirmed')) {
        setStep('verify');
        setError("Account not verified. Please enter the verification code sent to your email.");
      } else {
        setError(err.message || 'Login failed');
      }
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !code) return;
    
    setLoading(true);
    setError(null);
    try {
      await confirmRegistration(email, code);
      setSuccess("Account verified successfully! Logging you in...");
      // Auto login after verify
      await loginWithCognito(email, password);
      
      const params = new URLSearchParams(window.location.search);
      const returnUrl = params.get('return') || '/';
      navigate(returnUrl);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || 'Verification failed');
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0, scale: 0.98, transition: { duration: 0.3 } }}
      transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen bg-[#f8f9fa] text-[#111] font-sans selection:bg-black selection:text-white flex flex-col items-center justify-center relative overflow-hidden z-[100]"
    >
      <Scene3D />
      
      {/* Navbar Minimal */}
      <nav className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-10 py-5">
        <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
          <Logo />
          <span className="text-[15px] font-semibold tracking-[-0.02em] text-[#111] drop-shadow-sm bg-white/30 px-2 py-0.5 rounded-md backdrop-blur-md">
            SmallOps
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
            {step === 'login' ? 'Welcome to SmallOps' : 'Verify your Account'}
          </h2>
          <p className="text-[14px] text-gray-600 mb-2 font-medium">
            {step === 'login' ? 'Sign in to build, deploy and manage your small software.' : 'Check your email for a verification code.'}
          </p>

          {error && (
            <div className="w-full p-3 mb-4 bg-red-50 text-red-600 rounded-xl text-sm border border-red-100">
              {error}
            </div>
          )}
          
          {success && (
            <div className="w-full p-3 mb-4 bg-green-50 text-green-600 rounded-xl text-sm border border-green-100">
              {success}
            </div>
          )}

          {step === 'login' ? (
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
                className="w-full px-5 py-3.5 rounded-xl bg-white/70 border border-white/80 focus:outline-none focus:ring-2 focus:ring-black/5 focus:bg-white text-[15px] shadow-sm transition-all text-gray-900 placeholder:text-gray-400"
              />
              <div className="relative w-full">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-5 py-3.5 rounded-xl bg-white/70 border border-white/80 focus:outline-none focus:ring-2 focus:ring-black/5 focus:bg-white text-[15px] shadow-sm transition-all text-gray-900 placeholder:text-gray-400"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none flex items-center justify-center"
                >
                  <span className="material-symbols-outlined text-[20px]">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              <button 
                type="submit"
                disabled={loading}
                className="w-full px-5 py-3.5 rounded-xl bg-[#111] text-white text-[14px] font-medium shadow-xl shadow-black/10 hover:shadow-black/20 hover:-translate-y-0.5 hover:bg-[#000] transition-all disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-2"
              >
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Sign In'}
              </button>
            </form>
          ) : (
            <form 
              onSubmit={handleVerify} 
              className="w-full flex flex-col gap-4 mt-6"
            >
              <input
                type="text"
                placeholder="000000"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                className="w-full px-5 py-3.5 rounded-xl bg-white/70 border border-white/80 focus:outline-none focus:ring-2 focus:ring-black/5 focus:bg-white text-[15px] shadow-sm transition-all text-center tracking-widest"
              />
              <button 
                type="submit"
                disabled={loading || !code}
                className="w-full px-5 py-3.5 rounded-xl bg-[#111] text-white text-[14px] font-medium shadow-xl shadow-black/10 hover:shadow-black/20 hover:-translate-y-0.5 hover:bg-[#000] transition-all disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-2"
              >
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Verify & Log In'}
              </button>
            </form>
          )}
          
          {step === 'login' && (
            <div className="mt-6 text-center w-full">
              <p className="text-sm text-gray-600 font-medium">
                Don't have an account?{' '}
                <button 
                  type="button" 
                  onClick={() => {
                    const params = new URLSearchParams(window.location.search);
                    const returnUrl = params.get('return') || '/';
                    navigate(`/register?return=${encodeURIComponent(returnUrl)}`);
                  }} 
                  className="text-black font-semibold hover:underline"
                >
                  Sign up
                </button>
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
