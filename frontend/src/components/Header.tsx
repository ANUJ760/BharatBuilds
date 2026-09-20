import React from 'react';

interface HeaderProps {
  currentTab: 'home' | 'workspace' | 'timeline';
  setCurrentTab: (tab: 'home' | 'workspace' | 'timeline') => void;
  globalState: 'clarifying' | 'building' | 'deployed';
  setGlobalState: (state: 'clarifying' | 'building' | 'deployed') => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  setCurrentTab,
  globalState,
  setGlobalState,
}) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#050505]/80 backdrop-blur-xl border-b border-white/[0.08]">
      <div className="h-16 w-full px-4 lg:px-12 max-w-[1440px] mx-auto flex items-center justify-between gap-4">
        {/* Logo & Title */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setCurrentTab('home')}
            className="flex items-center gap-2 group focus:outline-none text-left"
          >
            <img
              src="/logo.svg"
              alt="SmallOps Logo"
              className="h-8 w-auto object-contain transition-transform group-hover:scale-105"
            />
            <span className="font-semibold text-lg text-white tracking-tight">
              SmallOps
            </span>
          </button>
          <span className="hidden lg:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono tracking-wider uppercase bg-[#201f1f] text-primary border border-white/[0.08]">
            BB-26 / Tour Edition
          </span>
        </div>

        {/* Center Primary Nav */}
        <nav className="flex items-center gap-1 p-1 rounded-lg bg-[#0e0e0e] border border-white/[0.08]">
          <button
            onClick={() => setCurrentTab('home')}
            className={`px-4 py-1.5 rounded text-xs font-medium transition-all ${
              currentTab === 'home'
                ? 'bg-[#0D0D0F] text-primary shadow-[0_0_12px_-3px_rgba(6,182,212,0.35)]'
                : 'text-[#A1A1AA] hover:text-white hover:bg-[#0D0D0F]'
            }`}
          >
            Home
          </button>
          <button
            onClick={() => setCurrentTab('workspace')}
            className={`px-4 py-1.5 rounded text-xs font-medium transition-all ${
              currentTab === 'workspace'
                ? 'bg-[#0D0D0F] text-primary shadow-[0_0_12px_-3px_rgba(6,182,212,0.35)]'
                : 'text-[#A1A1AA] hover:text-white hover:bg-[#0D0D0F]'
            }`}
          >
            Workspace
          </button>
          <button
            onClick={() => setCurrentTab('timeline')}
            className={`px-4 py-1.5 rounded text-xs font-medium transition-all ${
              currentTab === 'timeline'
                ? 'bg-[#0D0D0F] text-primary shadow-[0_0_12px_-3px_rgba(6,182,212,0.35)]'
                : 'text-[#A1A1AA] hover:text-white hover:bg-[#0D0D0F]'
            }`}
          >
            Timeline
          </button>
        </nav>

        {/* Right Telemetry & Actions */}
        <div className="flex items-center gap-4">
          <div className="hidden xl:flex items-center gap-3 px-3 py-1 rounded bg-[#0e0e0e] border border-white/[0.08]">
            <div className="flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    globalState === 'deployed'
                      ? 'bg-[#4edea3]'
                      : globalState === 'building'
                      ? 'bg-primary'
                      : 'bg-[#ffb873]'
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    globalState === 'deployed'
                      ? 'bg-[#4edea3]'
                      : globalState === 'building'
                      ? 'bg-primary'
                      : 'bg-[#ffb873]'
                  }`}
                />
              </span>
              <span
                className={`text-[11px] uppercase tracking-wider font-mono font-medium ${
                  globalState === 'deployed'
                    ? 'text-[#4edea3]'
                    : globalState === 'building'
                    ? 'text-primary'
                    : 'text-[#ffb873]'
                }`}
              >
                {globalState}
              </span>
            </div>
            <div className="h-3 w-px bg-[#27272A]" />
            <div className="text-[11px] text-[#71717A] font-mono">lat: 24ms</div>
            <div className="h-3 w-px bg-[#27272A]" />
            <div className="text-[11px] text-[#71717A] font-mono">mem: 14MB</div>
          </div>

          <button
            onClick={() => {
              setGlobalState('building');
              setTimeout(() => setGlobalState('deployed'), 2000);
            }}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#0D0D0F] hover:bg-[#18181B] text-white border border-white/[0.08] text-xs font-medium transition-all"
            type="button"
          >
            <span className="material-symbols-outlined text-[16px] text-primary">bolt</span>
            <span>Deploy Run</span>
          </button>

          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center ring-1 ring-white/[0.12] text-[#003640]">
            <span className="material-symbols-outlined text-[18px]">person</span>
          </div>
        </div>
      </div>
    </header>
  );
};
