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

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-[#f8f9fa] text-[#111]">Loading...</div>;

  return (
    <motion.div 
      initial={{ y: "25vh", opacity: 0 }} 
      animate={{ y: 0, opacity: 1 }} 
      transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="flex w-full h-screen bg-[#f3f4f6] text-[#111] font-sans selection:bg-black selection:text-white overflow-hidden"
    >
      {/* Activity Bar (VS Code style far-left) */}
      <div className="w-[48px] h-full bg-[#f8f9fa] border-r border-[#e5e7eb] flex flex-col items-center py-4 gap-4 flex-shrink-0 z-20">
        <Link to="/" className="text-gray-400 hover:text-black transition-colors mb-4">
          <span className="material-symbols-outlined text-[24px]">view_in_ar</span>
        </Link>
        <button className="text-black bg-black/5 p-2 rounded-xl">
          <span className="material-symbols-outlined text-[20px]">chat</span>
        </button>
        <Link to={`/apps/${id}/timeline`} className="text-gray-400 hover:text-black hover:bg-black/5 p-2 rounded-xl transition-colors">
          <span className="material-symbols-outlined text-[20px]">account_tree</span>
        </Link>
        <button className="text-gray-400 hover:text-black hover:bg-black/5 p-2 rounded-xl transition-colors mt-auto mb-2">
          <span className="material-symbols-outlined text-[20px]">settings</span>
        </button>
      </div>

      {/* Sidebar (Chat / Prompt) */}
      <div className="w-[320px] h-full bg-[#f8f9fa] border-r border-[#e5e7eb] flex flex-col flex-shrink-0 z-10">
        <div className="h-[40px] px-4 flex items-center justify-between font-medium text-[11px] uppercase tracking-wider text-gray-500 border-b border-[#e5e7eb]">
          <span>Your App</span>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto space-y-4 font-sans text-[13px]">
          <div className="bg-white border border-[#e5e7eb] rounded-xl p-3 shadow-sm">
            <div className="flex items-center gap-1.5 text-black font-semibold mb-1 text-[11px] uppercase tracking-wider">
              <span className="material-symbols-outlined text-[14px]">psychology</span>
              Original Prompt
            </div>
            <p className="text-gray-700 leading-relaxed">
              {appData?.prompt || 'Loading...'}
            </p>
          </div>

          <div className="bg-green-50/50 border border-green-100 rounded-xl p-3 shadow-sm">
            <div className="flex items-center gap-1.5 text-green-700 font-semibold mb-1 text-[11px] uppercase tracking-wider">
              <span className="material-symbols-outlined text-[14px]">check_circle</span>
              Live
            </div>
            <p className="text-green-800">
              What would you like to change?
            </p>
          </div>
        </div>

        {/* Chat Input */}
        <div className="p-3 bg-white border-t border-[#e5e7eb]">
          <div className="flex items-end bg-[#f3f4f6] border border-[#e5e7eb] rounded-xl overflow-hidden focus-within:border-black focus-within:ring-1 focus-within:ring-black transition-all p-1 mb-2">
            <textarea 
              placeholder="e.g. change button color..." 
              className="flex-1 bg-transparent px-2 py-1.5 text-[13px] resize-none max-h-[100px] min-h-[36px] focus:outline-none placeholder:text-gray-500"
              disabled={status === 'building' || status === 'pending'}
            />
            <button 
              disabled={status === 'building' || status === 'pending'}
              className="px-3 py-1.5 bg-black text-white text-[12px] font-medium rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              Update App
            </button>
          </div>
          <p className="text-[11px] text-gray-400 px-1">Describe a change and the agent will update the existing app.</p>
        </div>
      </div>

      {/* Main Viewport (Browser Preview) */}
      <div className="flex-1 h-full flex flex-col bg-[#ffffff] relative z-0">
        
        {/* Editor Tabs / URL Bar */}
        <div className="h-[40px] px-2 flex items-center bg-[#f8f9fa] border-b border-[#e5e7eb] gap-2">
          {/* Tab */}
          <div className="h-full px-4 flex items-center gap-2 bg-white border-t-2 border-t-black border-x border-x-[#e5e7eb] text-[12px] font-medium text-black -mb-px">
            <span className="material-symbols-outlined text-[14px] text-blue-500">public</span>
            Browser Preview
          </div>

          <div className="flex-1" />

          {/* URL Bar */}
          <div className="flex items-center gap-2 px-3 py-1 bg-white border border-[#e5e7eb] rounded-md shadow-sm max-w-[400px] w-full text-[12px] font-mono text-gray-600">
            <span className="material-symbols-outlined text-[14px] text-gray-400">lock</span>
            <span className="flex-1 truncate">{liveUrl || `https://${id?.slice(0,6) || 'app'}.acfs.live`}</span>
            <button onClick={handleCopy} className="hover:text-black transition-colors flex items-center">
              <span className="material-symbols-outlined text-[14px]">{copied ? 'check' : 'content_copy'}</span>
            </button>
          </div>

          <div className="flex-1" />
          
          <div className="flex items-center gap-3 pr-2">
            <div className="flex items-center gap-1.5 text-[11px] font-mono font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded border border-green-200">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500" />
              </span>
              LIVE
            </div>
            <button className="px-3 py-1 rounded bg-black text-white text-[11px] font-semibold hover:bg-gray-800 transition-colors">
              Share
            </button>
          </div>
        </div>

        {/* Iframe / Sandbox Container */}
        <div className="flex-1 w-full bg-[#f3f4f6] flex items-center justify-center p-4">
          <div className="w-full h-full max-w-[1200px] mx-auto bg-white rounded-xl border border-[#e5e7eb] shadow-xl overflow-hidden flex items-center justify-center">
            {status === 'pending' || status === 'building' ? (
              <div className="flex flex-col items-center gap-4 text-gray-500">
                <div className="w-6 h-6 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <p className="text-[13px] font-medium">Deploying MicroVM...</p>
              </div>
            ) : status === 'failed' ? (
              <div className="flex flex-col items-center gap-3 text-red-500">
                <span className="material-symbols-outlined text-3xl">error</span>
                <p className="text-[13px] font-medium">Deployment failed</p>
              </div>
            ) : liveUrl ? (
              <iframe src={liveUrl} className="w-full h-full border-none bg-white" title="Live App" />
            ) : (
              <div className="text-center space-y-4">
                <div className="w-12 h-12 bg-black rounded-xl mx-auto flex items-center justify-center shadow-lg">
                  <span className="material-symbols-outlined text-white text-2xl">widgets</span>
                </div>
                <div>
                  <h2 className="text-[15px] font-semibold tracking-tight text-[#111]">{appData?.title || 'Your Micro-App'}</h2>
                  <p className="text-[13px] text-gray-500 mt-1 max-w-xs mx-auto">This area securely renders your code in an isolated environment.</p>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </motion.div>
  );
};

export default AppView;
