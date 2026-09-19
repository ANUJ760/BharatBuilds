import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { apiGetApp } from '../api/client';
import { useDeployStatus } from '../hooks/useDeployStatus';

export const AppView = () => {
  const { id } = useParams();
  const [appData, setAppData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const { status, liveUrl } = useDeployStatus(id);

  useEffect(() => {
    if (id) {
      apiGetApp(id)
        .then(data => {
          setAppData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          // Fallback demo data
          setAppData({ title: 'E-Waste Tracker', prompt: 'Build an e-waste drop-off tracker...', status: 'active' });
          setLoading(false);
        });
    }
  }, [id]);

  const handleCopy = () => {
    if (liveUrl) {
      navigator.clipboard.writeText(liveUrl);
    } else {
      navigator.clipboard.writeText(`https://${id}.acfs.live`);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-[#e8e8e8] text-[#111]">Loading...</div>;

  return (
    <div className="flex flex-col w-full min-h-screen bg-[#e8e8e8] text-[#111] font-sans selection:bg-black selection:text-white">
      {/* Workspace Control Bar - Light Glassmorphism */}
      <section className="sticky top-0 z-40 w-full bg-[#e8e8e8]/80 backdrop-blur-xl border-b border-black/5 shadow-sm">
        <div className="max-w-[1440px] mx-auto px-4 lg:px-12 py-3 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-[#555] hover:text-black transition-colors flex items-center">
              <span className="material-symbols-outlined">home</span>
            </Link>
            <div className="h-8 w-px bg-gray-200"></div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-base font-semibold tracking-tight">{appData?.title || 'Generated App'}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider bg-gray-100 text-gray-500 border border-gray-200">Micro-App</span>
              </div>
              <span className="text-xs text-gray-400 font-mono">ID: {id}</span>
            </div>

            <button
              onClick={handleCopy}
              className="group relative flex items-center gap-2 px-3 py-1 rounded-md bg-gray-100 hover:bg-gray-200 border border-gray-200 text-gray-600 transition-all cursor-pointer"
            >
              <span className="material-symbols-outlined text-[15px]">link</span>
              <span className="font-mono text-xs">{`https://${id?.slice(0,6) || 'app'}.acfs.live`}</span>
              <span className="material-symbols-outlined text-[13px] text-gray-400 group-hover:text-black ml-0.5">
                {copied ? 'check' : 'content_copy'}
              </span>
            </button>

            <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-green-50 border border-green-200 text-green-600">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
              </span>
              <span className="font-mono text-xs tracking-wide font-medium">LIVE • 14ms edge</span>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Link
              to={`/apps/${id}/timeline`}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-black text-xs font-mono transition-colors"
            >
              <span className="material-symbols-outlined text-[15px]">account_tree</span>
              <span>View Timeline</span>
            </Link>
            <button className="flex items-center gap-2 px-4 py-1.5 rounded bg-black hover:bg-gray-900 text-white text-xs font-semibold transition-all">
              <span className="material-symbols-outlined text-[15px] font-bold">person_add</span>
              <span>Invite & Share</span>
            </button>
          </div>
        </div>
      </section>

      {/* Main Workspace */}
      <div className="w-full max-w-[1440px] mx-auto px-4 lg:px-12 py-6 flex-1">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-stretch min-h-[calc(100vh-140px)]">
          
          {/* Live Edit Chat (Left Col) */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="xl:col-span-4 flex flex-col bg-white border border-black/5 rounded-2xl shadow-xl overflow-hidden min-h-[600px]"
          >
            <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-black animate-pulse" />
                <span className="font-mono text-xs font-semibold tracking-wider text-black uppercase">Live Edit Chat</span>
              </div>
            </div>

            <div className="flex-1 p-4 space-y-4 overflow-y-auto font-mono text-xs bg-white flex flex-col">
              <div className="flex-1 space-y-4">
                <div className="p-3 rounded-lg bg-gray-50 border border-gray-100 space-y-1.5">
                  <div className="flex items-center justify-between text-gray-500 text-[11px]">
                    <span className="flex items-center gap-1.5 text-black font-semibold">
                      <span className="material-symbols-outlined text-[14px]">psychology</span>
                      <span>01. ORIGINAL PROMPT</span>
                    </span>
                  </div>
                  <p className="text-gray-800 text-[12px] leading-relaxed">
                    “{appData?.prompt || 'Loading...' }”
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-green-50 border border-green-100 space-y-1.5">
                  <div className="flex items-center justify-between text-green-600 text-[11px]">
                    <span className="flex items-center gap-1.5 font-bold">
                      <span className="material-symbols-outlined text-[14px]">check_circle</span>
                      <span>SYSTEM</span>
                    </span>
                  </div>
                  <p className="text-green-800 text-[12px]">App is live. What would you like to change?</p>
                </div>
              </div>

              {/* Chat Input */}
              <div className="mt-auto pt-4 border-t border-gray-100">
                <div className="flex items-center bg-gray-50 border border-gray-200 rounded-xl overflow-hidden focus-within:border-black focus-within:ring-1 focus-within:ring-black transition-all">
                  <input 
                    type="text" 
                    placeholder="E.g. change the button color to red..." 
                    className="flex-1 bg-transparent px-4 py-3 text-sm focus:outline-none"
                    disabled={status === 'building' || status === 'pending'}
                  />
                  <button 
                    disabled={status === 'building' || status === 'pending'}
                    className="px-4 py-3 text-gray-400 hover:text-black transition-colors disabled:opacity-50 flex items-center justify-center"
                  >
                    <span className="material-symbols-outlined">send</span>
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Live Micro-App Sandbox (Right Col) */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="xl:col-span-8 flex flex-col bg-white border border-black/5 rounded-2xl shadow-xl overflow-hidden relative"
          >
            <div className="px-5 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <span className="text-xs font-mono text-gray-500">Sandbox Viewport</span>
              </div>
            </div>

            <div className="flex-1 w-full h-full bg-gray-50 relative flex items-center justify-center">
              {status === 'pending' || status === 'building' ? (
                <div className="flex flex-col items-center gap-4">
                  <div className="w-8 h-8 border-4 border-black/20 border-t-black rounded-full animate-spin" />
                  <p className="text-sm font-medium tracking-tight">Deploying your application...</p>
                </div>
              ) : status === 'failed' ? (
                <div className="flex flex-col items-center gap-4 text-red-500">
                  <span className="material-symbols-outlined text-4xl">error</span>
                  <p className="text-sm font-medium">Deployment failed</p>
                </div>
              ) : liveUrl ? (
                <iframe src={liveUrl} className="w-full h-full min-h-[600px] border-none" title="Live App" />
              ) : (
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-black rounded-2xl mx-auto flex items-center justify-center">
                    <span className="material-symbols-outlined text-white text-3xl">widgets</span>
                  </div>
                  <h2 className="text-2xl font-semibold tracking-tight">{appData?.title || 'Your Micro-App'}</h2>
                  <p className="text-gray-500 max-w-sm mx-auto">This area renders the deployed code securely within an iframe connected to your live AWS endpoint.</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
export default AppView;
