"use client";

import { motion } from "framer-motion";

export default function RealWorldActions() {
  return (
    <section className="imagica-section imagica-section--solid flex-col py-32">
      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <motion.div initial={{ opacity: 0, x: -28 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }}>
          <h2 className="text-[clamp(32px,4.5vw,56px)] font-bold tracking-[-0.03em] text-[#111] leading-[1.12]">
            Build apps that act in
            <br />the real world
          </h2>
          <p className="text-[clamp(24px,3.5vw,44px)] font-normal tracking-[-0.02em] text-[#888] leading-[1.2] mt-1">
            with 4 million functions
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 28 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8, delay: 0.12 }}>
          <div className="preview-panel p-6">
            <div className="relative h-[300px] flex items-center justify-center">
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 500 250">
                <line x1="80" y1="125" x2="200" y2="125" stroke="#ddd" strokeWidth="1.5" />
                <line x1="300" y1="125" x2="420" y2="125" stroke="#ddd" strokeWidth="1.5" />
                <polygon points="195,121 205,125 195,129" fill="#ccc" />
                <polygon points="415,121 425,125 415,129" fill="#ccc" />
              </svg>
              <div className="absolute left-[20px] top-1/2 -translate-y-1/2 bg-white rounded-xl border border-[#e8e8e8] shadow-sm p-3 w-[120px]">
                <div className="text-[10px] text-[#999] mb-1">Input</div>
                <div className="text-[12px] text-[#333] font-medium">Find a restaurant that Jerry</div>
              </div>
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl border border-[#e8e8e8] shadow-sm p-4 w-[140px] text-center">
                <div className="text-[10px] text-[#999] mb-1">AI Processing</div>
                <div className="w-full h-[40px] rounded-lg bg-[#f5f5f5] border border-[#eee]" />
              </div>
              <div className="absolute right-[20px] top-1/2 -translate-y-1/2 bg-white rounded-xl border border-[#e8e8e8] shadow-sm p-3 w-[120px]">
                <div className="text-[10px] text-[#999] mb-1">Output</div>
                <div className="text-[12px] text-[#333] font-medium">Result →</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
