"use client";

import { motion } from "framer-motion";

export default function MissionSection() {
  return (
    <section id="mission" className="imagica-section imagica-section--solid flex-col py-32">
      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <motion.div initial={{ opacity: 0, x: -28 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }}>
          <h2 className="text-[clamp(32px,4.5vw,56px)] font-bold tracking-[-0.03em] text-[#111] leading-[1.12]">
            Build small software without the cloud complexity.
          </h2>
          <p className="text-[clamp(24px,3.5vw,44px)] font-normal tracking-[-0.02em] text-[#888] leading-[1.2] mt-1">
            Describe what you need. Let the agent build, deploy, authenticate and share it.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 28 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8, delay: 0.12 }}>
          <div className="preview-panel p-6">
            <div className="bg-white/70 rounded-xl border border-[#eee] p-4 shadow-sm w-full min-h-[280px]">
              <div className="flex items-center gap-3 mb-4 text-[11px] text-[#999]">
                <span className="px-2 py-1 rounded bg-[#f0f0f0]">TravelPlanner</span>
              </div>
              <div className="flex gap-3">
                <div className="flex-1 space-y-3">
                  <div className="text-[11px] text-[#999]">User Input</div>
                  <div className="bg-white rounded-lg border border-[#eee] p-3">
                    <div className="text-[10px] text-[#bbb]">Which travel destination is best if I want...</div>
                  </div>
                  <div className="bg-white rounded-lg border border-[#eee] p-3">
                    <div className="text-[10px] text-[#bbb]">Create AI which will recommend best travel destinations</div>
                    <button className="mt-2 px-3 py-1 rounded-full bg-[#4488ff] text-white text-[9px]">Use</button>
                  </div>
                </div>
                <div className="w-[130px] shrink-0">
                  <div className="bg-gradient-to-b from-[#8b2252] to-[#cc4477] rounded-2xl p-3 text-white shadow-lg">
                    <div className="text-[10px] font-semibold mb-1">Welcome</div>
                    <div className="text-[8px] opacity-80 mb-2">to Travel Planner</div>
                    <div className="text-[7px] opacity-70 mb-2">This AI trip planning app organizes your travel itinerary.</div>
                    <div className="grid grid-cols-2 gap-1.5 mb-2">
                      <div className="rounded-lg bg-white/20 h-[28px]" />
                      <div className="rounded-lg bg-white/20 h-[28px]" />
                    </div>
                    <div className="text-[8px] opacity-80">Ask me</div>
                    <div className="w-5 h-5 rounded-full bg-white/30 mx-auto mt-1" />
                  </div>
                </div>
              </div>
              <div className="flex justify-end mt-3">
                <button className="px-4 py-1.5 rounded-full bg-[#111] text-white text-[11px] font-medium">Build Your App</button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
