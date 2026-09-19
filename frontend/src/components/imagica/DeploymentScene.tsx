"use client";

import { motion } from "framer-motion";

export default function DeploymentScene() {
  return (
    <section className="imagica-section imagica-section--solid flex-col py-32">
      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <motion.div initial={{ opacity: 0, x: -28 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }}>
          <h2 className="text-[clamp(30px,4.5vw,52px)] font-bold tracking-[-0.03em] text-[#111] leading-[1.12]">
            Submit your app to
            <br /><span className="text-[#111]">the Cloud</span>
          </h2>
          <p className="text-[clamp(22px,3vw,40px)] font-normal tracking-[-0.02em] text-[#888] leading-[1.2] mt-1">
            and start serving millions
            <br />of user requests
          </p>
          <p className="text-[15px] text-[#999] mt-6 max-w-md leading-relaxed">
            Turn your app into a beautiful morphing interface that finds users instead of the other way around.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 28 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8, delay: 0.12 }} className="flex justify-center">
          <div className="phone w-[300px]">
            {/* Status bar */}
            <div className="flex items-center justify-between px-5 pt-3 pb-1">
              <span className="text-[12px] font-semibold text-[#333]">9:41</span>
              <div className="flex items-center gap-1.5">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2"><path d="M2 20h.01M7 20v-4M12 20v-8M17 20V8M22 20V4"/></svg>
                <svg width="18" height="12" viewBox="0 0 28 14" fill="none"><rect x="0.5" y="0.5" width="23" height="13" rx="3" stroke="#333"/><rect x="2" y="2" width="18" height="10" rx="1.5" fill="#333"/><rect x="25" y="4" width="2.5" height="6" rx="1" fill="#333"/></svg>
              </div>
            </div>
            <div className="flex items-center justify-between px-5 py-2">
              <span className="text-[11px] px-2 py-1 rounded-full bg-[#e8ffe8] text-[#2a7a2a] flex items-center gap-1">⊕ $25</span>
              <div className="w-8 h-8 rounded-full bg-[#ddd]" />
              <div className="w-6 h-6 rounded-full bg-[#f0f0f0] text-[9px] flex items-center justify-center text-[#999]">1</div>
            </div>
            <div className="h-[180px] bg-gradient-to-b from-[#e8e8e8] to-[#f2f2f2] flex items-center justify-center relative overflow-hidden">
              <div className="w-24 h-24 rounded-full bg-gradient-to-b from-white to-[#ddd] shadow-xl" />
              <p className="absolute right-4 bottom-8 text-[10px] text-[#aaa] tracking-wider">HOLD TO SPEAK</p>
              <div className="absolute right-6 bottom-3 w-7 h-7 rounded-full bg-[#333] flex items-center justify-center">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="white"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3zM19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/></svg>
              </div>
            </div>
            <div className="px-5 py-4 border-t border-[#eee]">
              <p className="text-[16px] text-[#ccc] font-light mb-4">Tap to type</p>
              {[
                ["🍔", "Order food delivery"],
                ["🛒", "Buy something"],
                ["✈️", "Book a flight ✦"],
                ["🚗", "Get a ride ✦"],
              ].map(([icon, label]) => (
                <div key={label} className="flex items-center gap-3 py-2.5 border-b border-[#f0f0f0] last:border-0">
                  <span className="text-[14px]">{icon}</span>
                  <span className="text-[13px] text-[#555]">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
