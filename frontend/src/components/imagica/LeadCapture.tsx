"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, CheckCircle2, Sparkles, Terminal, ExternalLink } from "lucide-react";

export default function LeadCapture() {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) return;

    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSubmitted(true);
    }, 900);
  };

  return (
    <section className="relative py-28 sm:py-36 bg-[#050508] text-white z-20 overflow-hidden">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs font-semibold uppercase tracking-wider text-purple-300">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          <span>Start Building Today</span>
        </div>

        <h2 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
          Unleash the power of <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-pink-400 to-purple-400">
            your imagination.
          </span>
        </h2>

        <p className="max-w-xl mx-auto text-base sm:text-lg text-slate-400 leading-relaxed">
          Join thousands of developers turning plain-language prompts into live,
          production AWS micro-applications in seconds.
        </p>

        {/* Lead Capture Form */}
        <div className="max-w-md mx-auto pt-4">
          <AnimatePresence mode="wait">
            {!isSubmitted ? (
              <motion.form
                key="form"
                onSubmit={handleSubmit}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="relative flex items-center p-1.5 rounded-full bg-white/10 backdrop-blur-2xl border border-white/20 shadow-2xl focus-within:border-purple-400/80 transition-colors"
              >
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your work email..."
                  required
                  className="w-full px-4 py-2.5 bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="shrink-0 inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-slate-950 text-xs font-semibold hover:bg-slate-100 transition-transform active:scale-95 disabled:opacity-50"
                  data-cursor-expand
                >
                  {isSubmitting ? (
                    <span className="w-4 h-4 rounded-full border-2 border-slate-950 border-t-transparent animate-spin" />
                  ) : (
                    <>
                      <span>Get Access</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </motion.form>
            ) : (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-5 rounded-3xl bg-white/10 backdrop-blur-2xl border border-emerald-500/30 flex items-center justify-center gap-3 text-emerald-300 text-sm font-medium shadow-xl"
              >
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                <span>You&apos;re on the priority list. Welcome to Small Software Cloud!</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Dual Secondary CTAs */}
        <div className="pt-6 flex flex-wrap items-center justify-center gap-4">
          <a
            href="http://localhost:5173"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/10 hover:bg-white/20 border border-white/15 text-white text-xs font-semibold transition-all hover:scale-105"
            data-cursor-expand
          >
            <span>Launch Live App Workspace</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <a
            href="#decision-graph"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <span>Inspect Decision Graph</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </section>
  );
}
