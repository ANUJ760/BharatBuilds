"use client";

import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="imagica-section imagica-section--transparent flex-col pt-32">
      <div className="max-w-4xl mx-auto flex flex-col items-center text-center gap-5">
        {/* Eyebrow */}
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="text-[13px] uppercase tracking-[0.2em] text-[#555] font-semibold"
        >
          BUILD AND DEPLOY SMALL SOFTWARE WITH AI
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.2 }}
          className="text-[clamp(36px,6vw,72px)] font-medium leading-[1.08] tracking-[-0.035em] text-[#111] z-10"
        >
          A cloud for small software
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.3 }}
          className="text-[18px] md:text-[22px] max-w-2xl text-[#333] font-medium z-10"
        >
          Turn a plain-language prompt into a live, authenticated, shareable web app in under a minute.
        </motion.p>

        <div className="h-[25vh]" />

        {/* CTA */}
        <motion.a
          href="/create"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.6 }}
          className="px-8 py-4 bg-[#111] text-white rounded-full text-[16px] font-medium hover:bg-black transition-colors z-10"
        >
          Build an App
        </motion.a>

        <motion.a
          href="#product"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.9 }}
          className="text-[15px] text-[#555] mt-4 hover:text-[#111] transition-colors font-medium z-10"
        >
          See How It Works
        </motion.a>
      </div>
    </section>
  );
}
