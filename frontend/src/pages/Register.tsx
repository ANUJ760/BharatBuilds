import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';
import { signUpWithCognito, confirmRegistration } from '../api/auth';

function Register() {
  const [step, setStep] = useState<'register' | 'verify'>('register');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnUrl = searchParams.get('return') || '/';

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await signUpWithCognito(email, password);
      setSuccess("Registration successful! We've sent a verification code to your email.");
      setStep('verify');
    } catch (err: any) {
      console.error('Registration failed:', err);
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await confirmRegistration(email, code);
      setSuccess("Account verified successfully! Redirecting to login...");
      setTimeout(() => navigate(`/login?return=${encodeURIComponent(returnUrl)}`), 2000);
    } catch (err: any) {
      console.error('Verification failed:', err);
      setError(err.message || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6 }}
      className="min-h-screen bg-[#f8f9fa] flex items-center justify-center relative overflow-hidden"
    >
      <div className="fixed inset-0 z-0">
        <Scene3D />
      </div>

      <div className="fixed inset-0 z-0 bg-white/30 backdrop-blur-[2px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="relative z-10 w-full max-w-md bg-white/70 backdrop-blur-xl border border-white rounded-3xl p-8 shadow-2xl shadow-black/5"
      >
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-black rounded-xl mx-auto flex items-center justify-center mb-6 shadow-lg shadow-black/20">
            <span className="material-symbols-outlined text-white">{step === 'register' ? 'person_add' : 'mark_email_read'}</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#111]">{step === 'register' ? 'Create Account' : 'Verify Email'}</h1>
          <p className="text-sm text-gray-500 mt-2 font-medium">{step === 'register' ? 'Join BharatBuilds to deploy apps' : 'Enter the code sent to your email'}</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-red-50 text-red-600 text-sm font-medium border border-red-100 text-center">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-6 p-3 rounded-xl bg-green-50 text-green-600 text-sm font-medium border border-green-100 text-center">
            {success}
          </div>
        )}

        {step === 'register' ? (
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-white/50 border border-black/5 rounded-xl focus:outline-none focus:border-black focus:bg-white transition-all text-sm font-medium"
                placeholder="you@example.com"
                required
              />
            </div>
            
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-white/50 border border-black/5 rounded-xl focus:outline-none focus:border-black focus:bg-white transition-all text-sm font-medium"
                placeholder="••••••••"
                required
                minLength={8}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-[#111] text-white py-3 rounded-xl text-[15px] font-medium hover:bg-black transition-all hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Sign Up'
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerify} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Verification Code</label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full px-4 py-3 bg-white/50 border border-black/5 rounded-xl focus:outline-none focus:border-black focus:bg-white transition-all text-sm font-medium tracking-widest text-center"
                placeholder="000000"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading || !code}
              className="w-full mt-2 bg-[#111] text-white py-3 rounded-xl text-[15px] font-medium hover:bg-black transition-all hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Verify Account'
              )}
            </button>
          </form>
        )}
        
        {step === 'register' && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500 font-medium">
              Already have an account?{' '}
              <Link to={`/login?return=${encodeURIComponent(returnUrl)}`} className="text-black font-semibold hover:underline">
                Log in
              </Link>
            </p>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}

export default Register;
