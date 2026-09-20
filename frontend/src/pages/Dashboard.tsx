import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Users, MoreVertical, X, Edit2 } from 'lucide-react';
import { Scene3D } from '../components/Scene3D';
import { Logo } from '../components/imagica/Logo';
import {
  apiListApps,
  apiDeleteApp,
  apiUpdateApp,
  apiListCollaborators,
  apiRemoveCollaborator,
  apiUpdateCollaboratorRole,
  apiInvite,
} from '../api/client';

export default function Dashboard() {
  const navigate = useNavigate();
  const [apps, setApps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [activeApp, setActiveApp] = useState<any | null>(null);
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [accessModalOpen, setAccessModalOpen] = useState(false);
  
  // Specific states for modals
  const [newTitle, setNewTitle] = useState('');
  const [collaborators, setCollaborators] = useState<any[]>([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('viewer');
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

  useEffect(() => {
    const user = localStorage.getItem('bb_user') || sessionStorage.getItem('bb_user');
    if (!user) {
      navigate('/login');
      return;
    }
    loadApps(user);
    
    // Close menus on outside click
    const handleClick = () => setMenuOpenId(null);
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [navigate]);

  const loadApps = async (user: string) => {
    setLoading(true);
    try {
      const res = await apiListApps(user);
      setApps(res.apps || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleRename = async () => {
    if (!activeApp || !newTitle.trim()) return;
    try {
      await apiUpdateApp(activeApp.app_id, newTitle);
      setApps(apps.map(a => a.app_id === activeApp.app_id ? { ...a, title: newTitle } : a));
      setRenameModalOpen(false);
    } catch(e) {
      console.error(e);
    }
  };

  const handleDelete = async () => {
    if (!activeApp) return;
    try {
      await apiDeleteApp(activeApp.app_id);
      setApps(apps.filter(a => a.app_id !== activeApp.app_id));
      setDeleteModalOpen(false);
    } catch(e) {
      console.error(e);
    }
  };

  const openAccessModal = async (app: any) => {
    setActiveApp(app);
    setAccessModalOpen(true);
    try {
      const res = await apiListCollaborators(app.app_id);
      setCollaborators(res.collaborators || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleInvite = async () => {
    if (!activeApp || !inviteEmail) return;
    try {
      await apiInvite(activeApp.app_id, inviteEmail, inviteRole);
      const res = await apiListCollaborators(activeApp.app_id);
      setCollaborators(res.collaborators || []);
      setInviteEmail('');
    } catch (e) {
      console.error(e);
    }
  };

  const handleRemoveCollaborator = async (email: string) => {
    if (!activeApp) return;
    try {
      await apiRemoveCollaborator(activeApp.app_id, email);
      setCollaborators(collaborators.filter(c => c.email !== email));
    } catch (e) {
      console.error(e);
    }
  };

  const handleRoleChange = async (email: string, role: string) => {
    if (!activeApp) return;
    try {
      await apiUpdateCollaboratorRole(activeApp.app_id, email, role);
      setCollaborators(collaborators.map(c => c.email === email ? { ...c, role } : c));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen bg-[#f8f9fa] text-[#111] font-sans selection:bg-black selection:text-white pt-24 pb-12 px-4 sm:px-10 relative overflow-hidden z-[100]"
    >
      <Scene3D />
      
      <nav className="fixed top-0 left-0 w-full z-40 flex items-center justify-between px-10 py-5 bg-white/40 backdrop-blur-xl border-b border-white/50">
        <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
          <Logo />
          <span className="text-[14px] font-semibold tracking-[-0.02em] text-[#111] bg-white/50 px-2 py-0.5 rounded backdrop-blur-sm">
            SmallOps
          </span>
        </button>
        <button
          onClick={() => navigate('/create')}
          className="px-5 py-2 rounded-full bg-white text-[13px] font-medium text-[#111] shadow-sm border border-white/80 hover:shadow-md transition-all duration-200"
        >
          New Project
        </button>
      </nav>

      <div className="max-w-6xl mx-auto mt-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-[#111]">Projects</h1>
        </div>

        {loading ? (
          <div className="flex items-center gap-3 text-sm text-[#555] relative z-10">
            <div className="w-4 h-4 border-2 border-[#555] border-t-transparent rounded-full animate-spin" />
            Loading projects...
          </div>
        ) : apps.length === 0 ? (
          <div className="p-12 text-center rounded-3xl bg-white/60 backdrop-blur-2xl border border-white/50 shadow-xl relative z-10">
            <p className="text-gray-600 mb-6 font-medium">You don't have any projects yet.</p>
            <button onClick={() => navigate('/create')} className="px-5 py-2 rounded-full bg-[#111] text-white text-[13px] font-medium hover:bg-[#333] transition-colors">
              Create your first app
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
            {apps.map(app => (
              <div key={app.app_id} className="group p-6 rounded-3xl bg-white/60 backdrop-blur-2xl border border-white/80 shadow-lg shadow-black/5 hover:shadow-xl hover:shadow-black/10 hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between min-h-[160px]">
                <div>
                  <h3 className="font-semibold text-[17px] text-[#111] mb-1.5 truncate drop-shadow-sm">{app.title || "Untitled App"}</h3>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider bg-white text-gray-600 border border-gray-100 shadow-sm">{app.status}</span>
                    <span className="text-[10px] text-gray-400 font-mono">{app.app_id.substring(0, 8)}</span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 justify-between">
                  <button 
                    onClick={() => navigate(`/apps/${app.app_id}`)}
                    className="text-[13px] font-medium text-[#111] hover:underline"
                  >
                    Open Workspace &rarr;
                  </button>

                  <div className="relative">
                    <button 
                      className="p-1.5 rounded-md hover:bg-black/5 text-[#555] transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        setMenuOpenId(menuOpenId === app.app_id ? null : app.app_id);
                      }}
                    >
                      <MoreVertical className="w-4 h-4" />
                    </button>
                    
                    <AnimatePresence>
                      {menuOpenId === app.app_id && (
                        <motion.div 
                          initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }}
                          className="absolute right-0 bottom-full mb-2 w-48 rounded-xl bg-white shadow-xl border border-black/5 py-1 z-10 overflow-hidden text-[13px]"
                        >
                          <button 
                            onClick={(e) => { e.stopPropagation(); setActiveApp(app); setNewTitle(app.title || ''); setRenameModalOpen(true); setMenuOpenId(null); }}
                            className="w-full text-left px-4 py-2 hover:bg-black/5 flex items-center gap-2"
                          ><Edit2 className="w-3.5 h-3.5" /> Rename</button>
                          <button 
                            onClick={(e) => { e.stopPropagation(); openAccessModal(app); setMenuOpenId(null); }}
                            className="w-full text-left px-4 py-2 hover:bg-black/5 flex items-center gap-2"
                          ><Users className="w-3.5 h-3.5" /> Manage Access</button>
                          <div className="h-px bg-black/5 my-1" />
                          <button 
                            onClick={(e) => { e.stopPropagation(); setActiveApp(app); setDeleteModalOpen(true); setMenuOpenId(null); }}
                            className="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 flex items-center gap-2"
                          ><Trash2 className="w-3.5 h-3.5" /> Delete Project</button>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rename Modal */}
      <AnimatePresence>
        {renameModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Rename Project</h3>
              <input 
                type="text" 
                value={newTitle} 
                onChange={(e) => setNewTitle(e.target.value)} 
                className="w-full px-4 py-2.5 rounded-xl bg-black/5 border border-transparent focus:border-black/20 focus:outline-none mb-6 text-[14px]"
                autoFocus
                onKeyDown={(e) => e.key === 'Enter' && handleRename()}
              />
              <div className="flex items-center justify-end gap-3">
                <button onClick={() => setRenameModalOpen(false)} className="px-4 py-2 rounded-xl hover:bg-black/5 text-[13px] font-medium">Cancel</button>
                <button onClick={handleRename} className="px-4 py-2 rounded-xl bg-[#111] text-white text-[13px] font-medium">Save Changes</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Delete Modal */}
      <AnimatePresence>
        {deleteModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-lg font-semibold mb-2">Delete Project?</h3>
              <p className="text-[14px] text-[#555] mb-6">Are you sure you want to delete <strong>{activeApp?.title}</strong>? This action cannot be undone.</p>
              <div className="flex items-center justify-end gap-3">
                <button onClick={() => setDeleteModalOpen(false)} className="px-4 py-2 rounded-xl hover:bg-black/5 text-[13px] font-medium">Cancel</button>
                <button onClick={handleDelete} className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-[13px] font-medium">Delete</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Access Modal */}
      <AnimatePresence>
        {accessModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="w-full max-w-lg bg-white rounded-2xl shadow-xl flex flex-col max-h-[80vh]">
              <div className="flex items-center justify-between p-6 border-b border-black/5 shrink-0">
                <h3 className="text-lg font-semibold">Share your app</h3>
                <button onClick={() => setAccessModalOpen(false)} className="p-1 hover:bg-black/5 rounded-md"><X className="w-5 h-5" /></button>
              </div>
              
              <div className="p-6 overflow-y-auto">
                <p className="text-[13px] text-gray-500 mb-4">
                  Invite people to use your app without requiring them to manage cloud infrastructure.
                </p>
                <div className="flex gap-2 mb-6">
                  <input 
                    type="email" 
                    placeholder="Enter an email address to invite a collaborator." 
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-black/5 border border-transparent focus:border-black/20 focus:outline-none text-[14px]"
                  />
                  <select 
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="px-3 py-2.5 rounded-xl bg-black/5 border border-transparent focus:outline-none text-[13px] font-medium"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="editor">Editor</option>
                  </select>
                  <button onClick={handleInvite} className="px-4 py-2 rounded-xl bg-[#111] text-white text-[13px] font-medium shrink-0">Send Invite</button>
                </div>

                <h4 className="text-xs font-semibold text-[#888] uppercase tracking-wider mb-3">Collaborators</h4>
                <div className="space-y-1">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-black/5">
                    <div className="flex flex-col">
                      <span className="text-[13px] font-semibold">{activeApp?.owner_id}</span>
                      <span className="text-[11px] text-[#666]">Owner</span>
                    </div>
                  </div>
                  
                  {collaborators.map(c => (
                    <div key={c.email} className="flex items-center justify-between p-3 rounded-xl hover:bg-black/5 group transition-colors">
                      <div className="flex flex-col">
                        <span className="text-[13px] font-medium">{c.email}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <select 
                          value={c.role}
                          onChange={(e) => handleRoleChange(c.email, e.target.value)}
                          className="px-2 py-1 rounded-md bg-transparent hover:bg-white border border-transparent hover:border-black/10 focus:outline-none text-[12px] font-medium"
                        >
                          <option value="viewer">Viewer</option>
                          <option value="editor">Editor</option>
                        </select>
                        <button 
                          onClick={() => handleRemoveCollaborator(c.email)}
                          className="p-1.5 rounded-md text-[#999] hover:text-red-600 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
