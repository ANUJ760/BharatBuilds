import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scene3D } from '../components/Scene3D';

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
      // Simulate clarification if backend is not running, otherwise hit real API
      const res = await fetch('/apps/clarify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      setClarifications(data);
    } catch (err) {
      // Fallback for demo if backend is offline
      setTimeout(() => {
        setClarifications({
          questions: [
            { id: 'auth', text: 'Authentication Method', options: ['Magic Link', 'OAuth', 'Anonymous'], default: 'Magic Link' },
            { id: 'storage', text: 'Data Storage', options: ['PostgreSQL', 'DynamoDB', 'SQLite'], default: 'SQLite' }
          ]
        });
        setAnswers({ auth: 'Magic Link', storage: 'SQLite' });
      }, 1500);
    } finally {
      setIsClarifying(false);
    }
  };

  const handleBuild = async () => {
    setIsBuilding(true);
    try {
      const res = await fetch('/apps/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, owner_id: 'demo-user', title: 'Generated App' })
      });
      
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      navigate(`/app/${data.app_id}`);
    } catch (err) {
      // Fallback for demo
      setTimeout(() => navigate('/app/demo-app-123'), 1000);
    }
  };

  return (
    <div className="min-h-screen bg-white text-black font-sans selection:bg-black selection:text-white overflow-hidden flex flex-col items-center justify-center relative">
      <div className="fixed inset-0 z-0 pointer-events-none opacity-50">
        <Scene3D />
      </div>

      <nav className="fixed top-0 w-full z-50 px-8 py-6 flex justify-between items-center">
        <button onClick={() => navigate('/')} className="text-xl tracking-tighter font-medium flex items-center gap-2">
          <span className="material-symbols-outlined">arrow_back</span>
          Back
        </button>
      </nav>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-2xl px-6"
      >
        <h1 className="text-4xl font-medium tracking-tighter mb-8 text-center">What would you like to build?</h1>
        
        <div className="bg-white/40 backdrop-blur-xl border border-black/10 rounded-3xl p-2 shadow-2xl">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Build an e-waste drop-off tracker..."
            className="w-full h-32 bg-transparent resize-none p-6 text-xl outline-none placeholder:text-gray-400"
          />
          
          <div className="flex justify-end p-2">
            {!clarifications ? (
              <button 
                onClick={handleClarify}
                disabled={isClarifying || !prompt}
                className="px-6 py-3 bg-black text-white rounded-full font-medium hover:bg-gray-900 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isClarifying ? <span className="material-symbols-outlined animate-spin">sync</span> : 'Review Requirements'}
              </button>
            ) : (
              <button 
                onClick={handleBuild}
                disabled={isBuilding}
                className="px-6 py-3 bg-black text-white rounded-full font-medium hover:bg-gray-900 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isBuilding ? <span className="material-symbols-outlined animate-spin">sync</span> : 'Generate App'}
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
            {clarifications.questions.map((q: any) => (
              <div key={q.id} className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-black/5 shadow-sm">
                <h3 className="font-medium mb-4">{q.text}</h3>
                <div className="flex flex-wrap gap-2">
                  {q.options.map((opt: string) => (
                    <button
                      key={opt}
                      onClick={() => setAnswers({ ...answers, [q.id]: opt })}
                      className={`px-4 py-2 rounded-full text-sm transition-colors ${
                        answers[q.id] === opt 
                          ? 'bg-black text-white' 
                          : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
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
