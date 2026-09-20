import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';
import { apiClarify, apiCreateApp, apiDeploy } from '../api/client';
import { Settings, X } from 'lucide-react';

export function Home() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [isClarifying, setIsClarifying] = useState(false);
  const [clarifications, setClarifications] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isBuilding, setIsBuilding] = useState(false);
  const [error, setError] = useState('');

  // Settings state
  const [showSettings, setShowSettings] = useState(false);
  const [credentials, setCredentials] = useState(() => {
    try {
      const stored = localStorage.getItem('bb_credentials');
      return stored ? JSON.parse(stored) : { aws_access_key_id: '', aws_secret_access_key: '', aws_region: 'ap-south-1' };
    } catch {
      return { aws_access_key_id: '', aws_secret_access_key: '', aws_region: 'ap-south-1' };
    }
  });

  const saveCredentials = (newCreds: any) => {
    setCredentials(newCreds);
    localStorage.setItem('bb_credentials', JSON.stringify(newCreds));
  };

  const getActiveCredentials = () => {
    if (credentials.aws_access_key_id && credentials.aws_secret_access_key) {
      return credentials;
    }
    return undefined;
  };

  const handleClarify = async () => {
    if (!prompt) return;
    setIsClarifying(true);
    setError('');
    
    try {
      const data = await apiClarify(prompt, getActiveCredentials());
      
      if (data.needs_clarification && data.questions && data.questions.length > 0) {
        setClarifications(data);
        // Pre-fill answers with suggested defaults
        const defaultAnswers: Record<string, string> = {};
        data.questions.forEach((q: any) => {
          defaultAnswers[q.question] = q.suggested_default;
        });
        setAnswers(defaultAnswers);
      } else {
        // If no clarification needed, just proceed directly to build
        await buildApp();
      }
    } catch (err: any) {
      console.error(err);
      setError('Backend unavailable — proceeding with direct build...');
      // Fallback: skip clarify and go straight to build
      setTimeout(() => {
        buildApp();
      }, 1500);
    } finally {
      setIsClarifying(false);
    }
  };

  const buildApp = async (resolvedAnswers: Record<string, string> = {}) => {
    setIsBuilding(true);
    try {
      const ownerId = localStorage.getItem('bb_user') || sessionStorage.getItem('bb_user') || 'anonymous';
      
      // Create app
      const appRes = await apiCreateApp(prompt, ownerId);
      
      // Trigger deploy pipeline with clarifications
      await apiDeploy(appRes.app_id, prompt, ownerId, appRes.title, resolvedAnswers, getActiveCredentials());
      
      // Redirect to app view with droplet transition
      window.dispatchEvent(new CustomEvent('burst-auth'));
      setTimeout(() => {
        navigate(`/apps/${appRes.app_id}`);
      }, 1000);
    } catch (err: any) {
      if (err.status === 401) {
        // Redirect to login if unauthorized for deploy
        window.dispatchEvent(new CustomEvent('burst-auth'));
        setTimeout(() => {
          navigate(`/login?return=/create`);
        }, 1000);
      } else {
        console.error(err);
      }
      setIsBuilding(false);
    }
  };

  const handleBuild = async () => {
    await buildApp(answers);
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0, filter: 'blur(10px)', transition: { duration: 0.4 } }}
      transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen bg-[#f8f9fa] text-[#111] font-sans selection:bg-black selection:text-white overflow-hidden flex flex-col items-center justify-center relative z-[100]"
    >
      <div className="fixed inset-0 z-0">
        <Scene3D />
      </div>

      {/* Subtle overlay for legibility */}
      <div className="fixed inset-0 z-0 bg-white/30 backdrop-blur-[2px] pointer-events-none" />

      <nav className="fixed top-0 w-full z-50 px-8 py-6 flex justify-between items-center pointer-events-auto">
        <button onClick={() => navigate('/')} className="text-xl tracking-tighter font-medium flex items-center gap-2">
          <span className="material-symbols-outlined">arrow_back</span>
          Back
        </button>
        <button onClick={() => setShowSettings(true)} className="p-2 rounded-full hover:bg-black/5 transition-colors flex items-center gap-2 text-sm font-medium">
          <Settings className="w-5 h-5" />
          <span>BYOK</span>
        </button>
      </nav>

      <AnimatePresence>
        {showSettings && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-black/20 backdrop-blur-sm flex items-center justify-center p-4 pointer-events-auto"
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl relative"
            >
              <button onClick={() => setShowSettings(false)} className="absolute top-6 right-6 p-1 rounded-md hover:bg-black/5">
                <X className="w-5 h-5" />
              </button>
              <h2 className="text-xl font-semibold mb-2">Bring Your Own Key</h2>
              <p className="text-sm text-gray-500 mb-6">Connect your own AWS Bedrock account to bypass platform rate limits.</p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">AWS Access Key ID</label>
                  <input type="text" value={credentials.aws_access_key_id} onChange={e => saveCredentials({...credentials, aws_access_key_id: e.target.value})} className="w-full px-4 py-2.5 bg-black/5 rounded-xl text-sm outline-none border border-transparent focus:border-black/20" placeholder="AKIA..." />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">AWS Secret Access Key</label>
                  <input type="password" value={credentials.aws_secret_access_key} onChange={e => saveCredentials({...credentials, aws_secret_access_key: e.target.value})} className="w-full px-4 py-2.5 bg-black/5 rounded-xl text-sm outline-none border border-transparent focus:border-black/20" placeholder="Secret Key" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">AWS Region</label>
                  <input type="text" value={credentials.aws_region} onChange={e => saveCredentials({...credentials, aws_region: e.target.value})} className="w-full px-4 py-2.5 bg-black/5 rounded-xl text-sm outline-none border border-transparent focus:border-black/20" placeholder="us-east-1" />
                </div>
              </div>
              <button onClick={() => setShowSettings(false)} className="mt-8 w-full py-3 bg-[#111] text-white rounded-xl font-medium text-sm hover:bg-black">
                Save Settings
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-3xl px-6 pointer-events-none"
      >
        <h1 className="text-[clamp(32px,5vw,56px)] font-medium tracking-tight mb-2 text-center drop-shadow-sm text-[#111] pointer-events-auto">
          What do you want to build?
        </h1>
        <p className="text-center text-[15px] text-gray-500 mb-8 font-medium pointer-events-auto">
          Describe the small software you need in plain language.
        </p>
        
        <div className="pointer-events-auto bg-white/60 backdrop-blur-2xl border border-white/80 rounded-3xl p-3 shadow-2xl shadow-black/5 focus-within:shadow-black/10 focus-within:border-[#ccc] transition-all duration-300">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the app you want to build…"
            className="w-full h-40 bg-transparent resize-none p-6 text-[18px] outline-none placeholder:text-gray-400 font-medium"
          />
          
          <div className="flex justify-end p-2">
            {!clarifications ? (
                <button 
                  onClick={handleClarify}
                  disabled={isClarifying || !prompt.trim()}
                  className="px-6 py-3 rounded-2xl bg-[#111] text-white text-[15px] font-medium hover:bg-black transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 flex items-center gap-2"
                >
                  {isClarifying ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Build App</span>
                      <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                    </>
                  )}
                </button>
              ) : (
                <button 
                  onClick={handleBuild}
                  disabled={isBuilding}
                  className="px-6 py-3 rounded-2xl bg-[#111] text-white text-[15px] font-medium hover:bg-black transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 flex items-center gap-2"
                >
                  {isBuilding ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Deploy Application</span>
                      <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
                    </>
                  )}
                </button>
            )}
          </div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 px-5 py-3 rounded-2xl bg-amber-50/80 backdrop-blur-xl border border-amber-200 text-amber-800 text-[14px] font-medium text-center pointer-events-auto"
          >
            {error}
          </motion.div>
        )}

        {clarifications && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-8 space-y-6 pointer-events-auto"
          >
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold text-[#111] mb-2">Before we build, let’s clarify a few things.</h2>
              <p className="text-sm text-gray-500">Choose a suggested answer or enter your own.</p>
            </div>
            {clarifications.questions.map((q: any, i: number) => (
              <div key={i} className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-black/5 shadow-sm">
                <h3 className="font-medium mb-1">{q.question}</h3>
                <p className="text-sm text-gray-500 mb-4">{q.why_it_matters}</p>
                <div className="flex flex-col gap-3">
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setAnswers({ ...answers, [q.question]: q.suggested_default })}
                      className={`px-4 py-2 rounded-full text-sm transition-colors ${
                        answers[q.question] === q.suggested_default 
                          ? 'bg-black text-white' 
                          : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {q.suggested_default} (Suggested)
                    </button>
                  </div>
                  <input
                    type="text"
                    placeholder="Or type your own answer..."
                    value={answers[q.question] !== q.suggested_default ? answers[q.question] || '' : ''}
                    onChange={(e) => setAnswers({ ...answers, [q.question]: e.target.value })}
                    className="w-full px-4 py-2 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-black text-sm"
                  />
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
}

export default Home;
