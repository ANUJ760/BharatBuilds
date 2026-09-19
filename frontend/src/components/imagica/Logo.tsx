import { Cloud } from 'lucide-react';

export const Logo = () => (
  <div className="relative w-7 h-7 bg-[#111] rounded-[8px] flex items-center justify-center shadow-inner">
    <Cloud className="w-[18px] h-[18px] text-white" strokeWidth={2.5} />
    <div className="w-1.5 h-1.5 rounded-full bg-[#00d2ff] absolute mt-[2px]" style={{ boxShadow: '0 0 6px rgba(0, 210, 255, 0.6)' }} />
  </div>
);
