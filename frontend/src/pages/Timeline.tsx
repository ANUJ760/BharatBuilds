import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export const Timeline = () => {
  const { id } = useParams();
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetch(`/apps/${id}/timeline`)
        .then(res => res.json())
        .then(data => {
          setTimelineData(data.steps || []);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          // Fallback mock data
          setTimelineData([
            { id: '1', title: 'Clarify Ambiguity', description: 'Asked user for fields.', status: 'success' },
            { id: '2', title: 'Generate Schema', description: 'Created 2 tables.', status: 'success' },
            { id: '3', title: 'Deploy Fargate', description: 'Deployed in 12s.', status: 'success' }
          ]);
          setLoading(false);
        });
    }
  }, [id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-[#050505] text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-white selection:text-black flex flex-col">
      <nav className="w-full z-50 px-8 py-6 flex justify-between items-center border-b border-white/10">
        <Link to={`/app/${id}`} className="text-xl tracking-tighter font-medium flex items-center gap-2 hover:opacity-70 transition-opacity">
          <span className="material-symbols-outlined">arrow_back</span>
          Back to Workspace
        </Link>
        <div className="flex items-center gap-2 text-sm font-medium font-mono text-[#71717A]">
          <span className="w-2 h-2 rounded-full bg-[#4edea3]"></span>
          Timeline ID: {id}
        </div>
      </nav>

      <div className="flex-1 flex flex-col items-center justify-center p-8 relative overflow-hidden">
        {/* Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-white/5 rounded-full blur-[120px] pointer-events-none"></div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative z-10 w-full max-w-3xl"
        >
          <div className="text-center mb-16">
            <h1 className="text-5xl font-medium tracking-tighter mb-4">Decision Timeline</h1>
            <p className="text-[#a1a1aa]">Inspect every action taken by the agent. Instantly revert to any prior state.</p>
          </div>

          <div className="flex flex-col gap-6 border-l-2 border-white/20 pl-8 ml-8">
            {timelineData.map((step, index) => (
              <motion.div 
                key={step.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative bg-[#141313] p-6 rounded-2xl border border-white/10 group hover:border-white/30 transition-colors"
              >
                <div className="absolute -left-[34px] top-1/2 w-[32px] h-[2px] bg-white/20 group-hover:bg-white/50 transition-colors"></div>
                <div className="absolute -left-[41px] top-1/2 -translate-y-1/2 w-[14px] h-[14px] rounded-full bg-[#050505] border-2 border-white/50"></div>
                
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-xs text-[#a1a1aa] mb-1 uppercase tracking-wider">Step {index + 1}</div>
                    <div className="text-lg font-medium">{step.title}</div>
                    <div className="text-sm text-[#71717a] mt-2">{step.description}</div>
                  </div>
                  <button className="px-4 py-2 rounded bg-white/10 hover:bg-white/20 text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                    Revert to here
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Timeline;
