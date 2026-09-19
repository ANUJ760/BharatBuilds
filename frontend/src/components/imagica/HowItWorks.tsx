"use client";

import { motion } from "framer-motion";

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="imagica-section imagica-section--solid flex-col py-32">
      <div className="max-w-6xl mx-auto w-full">
        <motion.h2
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="text-center text-[clamp(36px,5.5vw,68px)] font-bold tracking-[-0.03em] text-[#111] leading-[1.08] mb-4"
        >
          Create any AI by
          <br />
          describing it
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, delay: 0.12 }}
          className="text-center text-[16px] text-[#888] mb-16"
        >
          From idea to product at the speed of thought.
        </motion.p>

        {/* Workspace mockup */}
        <motion.div
          initial={{ opacity: 0, y: 36 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.85, delay: 0.18 }}
          className="max-w-4xl mx-auto"
        >
          <div className="browser">
            <div className="browser__bar">
              <div className="browser__dots">
                <div className="browser__dot browser__dot--r" />
                <div className="browser__dot browser__dot--y" />
                <div className="browser__dot browser__dot--g" />
              </div>
              <div className="flex items-center gap-4 flex-1 justify-center">
                <span className="text-[12px] text-[#999] px-3 py-1 rounded-md bg-[#f0f0f0]">Test Project 01</span>
                <span className="text-[12px] text-[#666] px-3 py-1 rounded-md bg-white border border-[#e0e0e0]">Test Project 02</span>
              </div>
              <div className="flex items-center gap-4 text-[11px] text-[#999]">
                <span>Property</span>
                <span>Functions</span>
                <span>Variables</span>
                <span>Publish</span>
              </div>
            </div>
            <div className="browser__body min-h-[350px] relative bg-gradient-to-b from-[#f8f8ff] to-[#f4f4f8]">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="bg-white rounded-xl shadow-sm border border-[#eee] p-4 w-[200px]">
                  <div className="text-[12px] font-medium text-[#333] mb-2">Text</div>
                  <div className="text-[11px] text-[#aaa] mb-3">Enter your text here...</div>
                  <div className="w-full h-[60px] rounded-lg bg-[#f8f8f8] border border-[#eee]" />
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-3 flex items-center justify-between bg-white/80 backdrop-blur border-t border-[#eee]">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-[#4488ff] border-2 border-white shadow-sm" />
                  {[1,2,3,4].map(i=><div key={i} className="w-5 h-5 rounded bg-[#eee]" />)}
                </div>
                <button className="px-4 py-1.5 rounded-full bg-[#4488ff] text-white text-[11px] font-medium">Test AI</button>
                <span className="text-[11px] text-[#999]">100%</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
