"use client";

import { motion } from "framer-motion";
import { Sparkles, Check } from "lucide-react";

export default function ProductConcept() {
  const floatingIdeas = [
    { text: "Lead qualification triage", tag: "Internal Tool", delay: 0 },
    { text: "Stripe payout reconciler", tag: "Finance", delay: 0.1 },
    { text: "Incident severity router", tag: "DevOps", delay: 0.2 },
    { text: "Client feedback portal", tag: "Micro-SaaS", delay: 0.15 },
    { text: "Contract expiration radar", tag: "Legal", delay: 0.25 },
  ];

  return (
    <section id="concept" className="relative py-28 sm:py-36 z-10 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Editorial Philosophy */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-200/60 dark:bg-slate-800/60 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              <Sparkles className="w-3.5 h-3.5 text-orange-500" />
              <span>The Small Software Thesis</span>
            </div>

            <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-slate-900 dark:text-white leading-tight">
              AI can generate an app. We make it ready to use.
            </h2>

            <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed">
              Small software should be as easy to deploy and share as a Google Doc.
            </p>

            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-3">
                <div className="p-1 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 mt-1">
                  <Check className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                    Prompt-to-App
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Describe what you need. Get a working app.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 mt-1">
                  <Check className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                    Instant AWS Deployment
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    From prompt to live app.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Floating App Ideas Mosaic */}
          <div className="lg:col-span-5 relative">
            <div className="relative p-6 rounded-3xl bg-white/60 dark:bg-slate-900/60 backdrop-blur-xl border border-white/80 dark:border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Live Idea Ingestion
                </span>
                <span className="text-xs font-mono text-emerald-500">Autonomous Ready</span>
              </div>

              {floatingIdeas.map((idea, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idea.delay, duration: 0.5 }}
                  className="group flex items-center justify-between p-3.5 rounded-2xl bg-white/90 dark:bg-slate-800/80 border border-slate-200/70 dark:border-slate-700 shadow-sm hover:shadow-md hover:border-slate-400 transition-all duration-300"
                  data-cursor-expand
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-slate-900 dark:bg-white group-hover:scale-125 transition-transform" />
                    <span className="text-xs font-medium text-slate-800 dark:text-slate-200">
                      {idea.text}
                    </span>
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400">
                    {idea.tag}
                  </span>
                </motion.div>
              ))}

              <div className="pt-3 text-center">
                <span className="text-[11px] text-slate-400">
                  Every concept provisions isolated serverless AWS primitives
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
