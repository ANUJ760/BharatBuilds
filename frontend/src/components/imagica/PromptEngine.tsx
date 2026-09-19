import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { apiCreateApp } from "../../api/client";

const INDUSTRIES = ["Legal Services", "Science", "Education", "Product Design", "Corporate"];
const PROMPTS: Record<string, string> = {
  "Legal Services": "A contract review tool that highlights risk clauses and suggests amendments",
  Science: "A lab experiment tracker that logs results and generates analysis reports",
  Education: "A student progress dashboard with quiz generation and grade tracking",
  "Product Design": "An investing app that provides insights on stocks with an interface for trading",
  Corporate: "A team standup aggregator that summarizes blockers and sends Slack digests",
};

export default function PromptEngine() {
  const [stage, setStage] = useState<"industry" | "prompt" | "generating" | "done">("industry");
  const [selectedIndustry, setSelectedIndustry] = useState("");
  const [typed, setTyped] = useState("");
  const [target, setTarget] = useState("");

  const pickIndustry = (ind: string) => {
    setSelectedIndustry(ind);
    setTarget(PROMPTS[ind] ?? PROMPTS["Product Design"]);
    setTyped("");
    setTimeout(() => setStage("prompt"), 400);
  };

  // Typewriter
  useEffect(() => {
    if (stage !== "prompt" || !target) return;
    if (typed.length >= target.length) {
      const t = setTimeout(() => setStage("generating"), 1200);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setTyped(target.slice(0, typed.length + 1)), 30 + Math.random() * 25);
    return () => clearTimeout(t);
  }, [stage, typed, target]);

  // Generation timer and API call
  useEffect(() => {
    if (stage !== "generating") return;

    let mounted = true;
    const create = async () => {
      try {
        const ownerId = localStorage.getItem('bb_user') || 'anonymous';
        // In a real app we might want to ensure the token exists here
        const res = await apiCreateApp(target, ownerId, `${selectedIndustry} App`);
        
        if (mounted) {
          // Wait at least 2s for visual effect
          setTimeout(() => setStage("done"), 2000);
        }
      } catch (err) {
        console.error("Failed to create app:", err);
        if (mounted) {
          // Fallback if API is offline
          setTimeout(() => setStage("done"), 2000);
        }
      }
    };
    
    create();
    
    return () => { mounted = false; };
  }, [stage, target, selectedIndustry]);

  return (
    <section id="product" className="imagica-section imagica-section--solid flex-col">
      <div className="w-full max-w-3xl mx-auto">
        <AnimatePresence mode="wait">
          {/* ── Stage 1: Industry selection ── */}
          {stage === "industry" && (
            <motion.div
              key="s1"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.45 }}
              className="flex flex-col gap-8"
            >
              <h2 className="text-[clamp(22px,3.2vw,36px)] font-normal tracking-[-0.02em] text-[#555]">
                What industry do you want to transform?
              </h2>
              <div className="w-full pb-4 border-b border-[#d8d8d8]">
                <span className="text-[clamp(26px,4vw,42px)] font-light text-[#ccc] tracking-[-0.02em]">
                  Enter your industry
                </span>
              </div>
              <div className="flex flex-wrap gap-3">
                {INDUSTRIES.map((i) => (
                  <button key={i} onClick={() => pickIndustry(i)} className="pill">{i}</button>
                ))}
              </div>
            </motion.div>
          )}

          {/* ── Stage 2: Prompt typing ── */}
          {stage === "prompt" && (
            <motion.div
              key="s2"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.45 }}
              className="flex flex-col gap-5"
            >
              <p className="text-[15px] text-[#999]">What do you want your app to do?</p>
              <div className="flex items-center gap-4">
                <p className="flex-1 text-[clamp(20px,2.8vw,30px)] font-medium text-[#222] tracking-[-0.01em] leading-[1.35] pb-4 border-b border-[#d8d8d8]">
                  {typed}
                  <span className="inline-block w-[2px] h-[0.9em] bg-[#222] ml-0.5 animate-pulse" />
                </p>
                <button onClick={() => setStage("generating")} className="arrow-btn shrink-0">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 18l6-6-6-6" />
                  </svg>
                </button>
              </div>
            </motion.div>
          )}

          {/* ── Stage 3: Generating ── */}
          {stage === "generating" && (
            <motion.div
              key="s3"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ duration: 0.5 }}
            >
              <div className="browser max-w-2xl mx-auto">
                <div className="browser__bar">
                  <div className="browser__dots">
                    <div className="browser__dot browser__dot--r" />
                    <div className="browser__dot browser__dot--y" />
                    <div className="browser__dot browser__dot--g" />
                  </div>
                  <div className="browser__url">🔒 app.smallsoftware.cloud</div>
                </div>
                <div className="browser__body py-24">
                  <div className="spinner mb-6" />
                  <p className="text-[15px] text-[#999]">Creating a new app for you...</p>
                </div>
              </div>
            </motion.div>
          )}

          {/* ── Stage 4: Done ── */}
          {stage === "done" && (
            <motion.div
              key="s4"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="browser max-w-2xl mx-auto">
                <div className="browser__bar">
                  <div className="browser__dots">
                    <div className="browser__dot browser__dot--r" />
                    <div className="browser__dot browser__dot--y" />
                    <div className="browser__dot browser__dot--g" />
                  </div>
                  <div className="browser__url">🔒 app.smallsoftware.cloud</div>
                </div>
                <div className="browser__body p-8 items-start">
                  <div className="w-full space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-[#eee]">
                      <span className="text-[14px] font-semibold text-[#222]">{selectedIndustry} App</span>
                      <span className="text-[11px] px-2 py-1 rounded-full bg-[#e8ffe8] text-[#2a7a2a]">● Live</span>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      {[["Users", "24"], ["API Calls", "1.2K"], ["Uptime", "100%"]].map(([label, val]) => (
                        <div key={label} className="p-3 rounded-xl bg-white/80 border border-[#eee]">
                          <div className="text-[10px] text-[#999] mb-1">{label}</div>
                          <div className="text-[18px] font-semibold text-[#222]">{val}</div>
                        </div>
                      ))}
                    </div>
                    <div className="p-3 rounded-xl bg-white/80 border border-[#eee] text-[12px] text-[#666]">{target}</div>
                  </div>
                </div>
              </div>
              <div className="text-center mt-8">
                <button onClick={() => { setStage("industry"); setSelectedIndustry(""); setTyped(""); }} className="text-[13px] text-[#999] hover:text-[#555] transition-colors">
                  Try another →
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
