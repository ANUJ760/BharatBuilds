"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const FEATURES = [
  {
    id: "clarify",
    title: "Clarify-Then-Build",
    desc: "When a request needs clarification, the agent asks up to 3 targeted questions with suggested defaults, then builds without further interruption.",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>,
  },
  {
    id: "auth",
    title: "Authentication & Sharing",
    desc: "Every deployed app gets authentication and sharing out of the box. Invite collaborators with Viewer or Editor access.",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>,
  },
  {
    id: "timeline",
    title: "Decision Timeline",
    desc: "Plans, tool calls, generated code, retries and deployments are recorded in a visual Decision Timeline.",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 20v-6M6 20V10M18 20V4"></path></svg>,
  },
  {
    id: "backtrack",
    title: "Backtrack",
    desc: "Inspect any previous step and revert the live app to that exact code snapshot.",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 11l5-5-5-5M21 11H3M21 21v-4a4 4 0 0 0-4-4H3M3 17l5-5-5-5"></path></svg>,
  },
  {
    id: "live-edit",
    title: "Live Editing",
    desc: "Describe a change in chat. The agent edits the existing app and redeploys it to the same URL.",
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>,
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
