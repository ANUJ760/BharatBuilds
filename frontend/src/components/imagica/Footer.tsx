"use client";

import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Logo } from "./Logo";

export default function Footer() {
  const navigate = useNavigate();
  return (
    <footer className="imagica-section imagica-section--solid flex-col py-24" style={{ minHeight: "auto" }}>
      <div className="max-w-4xl mx-auto text-center w-full">
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }}>
          <div className="flex items-center justify-center gap-3 mb-8">
            <Logo />
            <span className="text-[18px] font-semibold tracking-[-0.02em] text-[#111]">SmallOps</span>
          </div>
          <h3 className="text-[clamp(28px,4vw,48px)] font-bold tracking-[-0.03em] text-[#111] leading-[1.08] mb-6">
            Ready to build?
          </h3>
          <p className="text-[15px] text-[#999] mb-10 max-w-lg mx-auto leading-relaxed">
            Deploy your first SmallOps in under 60 seconds. Just describe what you need.
          </p>
          <a 
            href="/create" 
            onClick={(e) => {
              e.preventDefault();
              window.dispatchEvent(new CustomEvent('burst-auth'));
              setTimeout(() => {
                navigate("/create");
              }, 900);
            }}
            className="inline-block px-8 py-3.5 rounded-full bg-[#111] text-white text-[14px] font-medium hover:bg-[#333] transition-colors shadow-lg"
          >
            Get Started Free
          </a>
        </motion.div>

        <div className="mt-24 pt-8 border-t border-[#ddd] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-[12px] text-[#bbb]">SmallOps</p>
          <div className="flex items-center gap-6">
            <span className="text-[12px] text-[#aaa]">Built for Bharat Builds Tour 2026</span>
            <span className="text-[12px] text-[#aaa]">Built on AWS</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
