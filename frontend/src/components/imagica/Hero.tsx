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
          className="text-[13px] uppercase tracking-[0.2em] text-[#999] font-normal"
        >
          Deploy a live app from a prompt in under 60 seconds
        </motion.p>

        {/* Big heading — very light color so it sits over the 3D sphere */}
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.2 }}
          className="text-[clamp(36px,6vw,72px)] font-normal leading-[1.08] tracking-[-0.035em] text-[#c0c0c0]"
        >
          A new way to think and create
          <br />
          with computers
        </motion.h1>

        {/* Spacer to push CTA below the sphere */}
        <div className="h-[35vh]" />

        {/* CTA */}
        <motion.a
          href="#product"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.6 }}
          className="text-[14px] text-[#aaa] hover:text-[#777] transition-colors"
        >
          Get early access
        </motion.a>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.9 }}
          className="text-[13px] text-[#bbb] mt-8"
        >
          Explore Product
        </motion.p>
      </div>
    </section>
  );
}
