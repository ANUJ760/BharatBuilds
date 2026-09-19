import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';
import { apiClarify, apiCreateApp, apiDeploy } from '../api/client';

export function Home() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [isClarifying, setIsClarifying] = useState(false);
  const [clarifications, setClarifications] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isBuilding, setIsBuilding] = useState(false);

  const handleClarify = async () => {
    if (!prompt) return;
    setIsClarifying(true);
    
    try {
      const data = await apiClarify(prompt);
      
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
      await apiDeploy(appRes.app_id, prompt, ownerId, appRes.title, resolvedAnswers);
      
      // Redirect to app view
      navigate(`/apps/${appRes.app_id}`);
    } catch (err: any) {
      if (err.status === 401) {
        // Redirect to login if unauthorized for deploy
        navigate(`/login?return=/create`);
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
    <div className="min-h-screen bg-[#f8f9fa] text-[#111] font-sans selection:bg-black selection:text-white overflow-hidden flex flex-col items-center justify-center relative">
      <div className="fixed inset-0 z-0 pointer-events-none">
        <Scene3D />
      </div>

      {/* Subtle overlay for legibility */}
      <div className="fixed inset-0 z-0 bg-white/30 backdrop-blur-[2px] pointer-events-none" />

      <nav className="fixed top-0 w-full z-50 px-8 py-6 flex justify-between items-center">
        <button onClick={() => navigate('/')} className="text-xl tracking-tighter font-medium flex items-center gap-2">
          <span className="material-symbols-outlined">arrow_back</span>
          Back
        </button>
      </nav>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-3xl px-6"
      >
        <h1 className="text-[clamp(32px,5vw,56px)] font-medium tracking-tight mb-8 text-center drop-shadow-sm text-[#111]">
          What would you like to build?
        </h1>
        
        <div className="bg-white/60 backdrop-blur-2xl border border-white/80 rounded-3xl p-3 shadow-2xl shadow-black/5 focus-within:shadow-black/10 focus-within:border-[#ccc] transition-all duration-300">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Build an e-waste drop-off tracker..."
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
                      <span>Design Architecture</span>
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

        {clarifications && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-8 space-y-6"
          >
            <div className="text-sm font-medium text-gray-500 uppercase tracking-widest text-center">Agent Clarifications</div>
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
    </div>
  );
}

export default Home;
