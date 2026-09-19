"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const FEATURES = [
  {
    id: "nocode",
    title: "No code",
    desc: "Build functional apps without writing a single line of code",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M9 9h6M9 12h4M9 15h5"/></svg>,
  },
  {
    id: "realtime",
    title: "Real-time data",
    desc: "Connect live data sources and APIs with zero configuration",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>,
  },
  {
    id: "multimodal",
    title: "Multimodal",
    desc: "Process text, images, voice, and structured data in a single flow",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M17.5 14v7M14 17.5h7"/></svg>,
  },
  {
    id: "speed",
    title: "Speed of execution",
    desc: "Deploy instantly on serverless infrastructure that scales automatically",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>,
  },
];

export default function FeatureSwitcher() {
  const [idx, setIdx] = useState(0);

  return (
    <section id="features" className="imagica-section imagica-section--solid flex-col py-32">
      <div className="max-w-6xl mx-auto w-full">
        <motion.h2
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="text-center text-[clamp(32px,5vw,60px)] font-bold tracking-[-0.03em] text-[#111] leading-[1.08] mb-16"
        >
          The simplest way to build an AI app
        </motion.h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-start">
          {/* Left tabs */}
          <div className="space-y-2">
            {FEATURES.map((f, i) => (
              <div key={f.id} onClick={() => setIdx(i)} className={`feat-card ${idx === i ? "feat-card--active" : ""}`}>
                <div className={`shrink-0 mt-0.5 transition-colors ${idx === i ? "text-[#333]" : "text-[#bbb]"}`}>{f.icon}</div>
                <div>
                  <div className={`text-[16px] font-medium transition-colors ${idx === i ? "text-[#111]" : "text-[#555]"}`}>{f.title}</div>
                  {idx === i && (
                    <motion.p initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="text-[13px] text-[#888] mt-1 leading-relaxed">
                      {f.desc}
                    </motion.p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Right preview */}
          <div className="preview-panel min-h-[400px] flex items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.div key={idx} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.3 }} className="p-8 w-full">
                <div className="bg-white/70 rounded-xl border border-[#eee] p-6 shadow-sm">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 rounded-full bg-[#eee]" />
                    <span className="text-[12px] text-[#999]">Use Input</span>
                  </div>
                  <div className="text-[13px] text-[#555] font-medium mb-2">Enter your text here...</div>
                  <div className="w-full h-[80px] rounded-lg bg-[#f8f8f8] border border-[#eee]" />
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}
