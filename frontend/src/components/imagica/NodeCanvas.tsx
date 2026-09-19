"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Bot, Cpu, Database, Shield, Zap, Sparkles, ArrowRight } from "lucide-react";

interface GraphNode {
  id: string;
  title: string;
  category: string;
  desc: string;
  icon: React.ElementType;
  badge: string;
  x: string;
  y: string;
}

export default function NodeCanvas() {
  const [activeNode, setActiveNode] = useState<string>("agent");

  const nodes: GraphNode[] = [
    {
      id: "input",
      title: "Plain Prompt",
      category: "Input Stream",
      desc: "Raw intent parsed via semantic tokenization without DSL or boilerplate.",
      icon: Sparkles,
      badge: "Natural Language",
      x: "10%",
      y: "35%",
    },
    {
      id: "agent",
      title: "Agentic Reasoning",
      category: "Decision Engine",
      desc: "Evaluates multi-tenant isolation, authorization tiers, and state persistence.",
      icon: Bot,
      badge: "Autonomous",
      x: "38%",
      y: "20%",
    },
    {
      id: "auth",
      title: "Cognito Auth",
      category: "Security",
      desc: "Auto-wires JWT verification, user pools, and role-based policies.",
      icon: Shield,
      badge: "AWS Cognito",
      x: "38%",
      y: "65%",
    },
    {
      id: "infra",
      title: "Serverless Synthesis",
      category: "AWS Runtime",
      desc: "Synthesizes AWS Lambda microservices + DynamoDB single-table schema.",
      icon: Cpu,
      badge: "Zero Cold Starts",
      x: "68%",
      y: "40%",
    },
    {
      id: "output",
      title: "Live CloudFront Edge",
      category: "Production",
      desc: "SSL terminated, custom domain mapped, and publicly shareable in <60s.",
      icon: Zap,
      badge: "Worldwide CDN",
      x: "90%",
      y: "40%",
    },
  ];

  return (
    <section className="relative py-28 sm:py-36 z-10 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-200/60 dark:bg-slate-800/60 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            <span>Spatial Decision Network</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-slate-950 dark:text-white">
            Create any app by describing it.
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300">
            A real-time spatial graph of the decision topology our autonomous cloud
            executes behind every generated application.
          </p>
        </div>

        {/* Spatial Node Map Container */}
        <div className="relative w-full rounded-3xl bg-white/70 dark:bg-slate-900/70 backdrop-blur-2xl border border-white/80 dark:border-slate-800 shadow-2xl p-6 sm:p-12 min-h-[440px] flex items-center justify-center overflow-hidden">
          {/* Subtle Grid Canvas Background */}
          <div className="absolute inset-0 bg-noise opacity-40 pointer-events-none" />

          {/* SVG Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="grad-pulse" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#ff5722" stopOpacity="0.4" />
                <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.4" />
              </linearGradient>
            </defs>

            {/* Connecting paths */}
            <path
              d="M 120 220 C 240 220, 240 140, 360 140"
              stroke="url(#grad-pulse)"
              strokeWidth="2"
              fill="none"
              strokeDasharray="6 6"
              className="animate-[pulse_3s_ease-in-out_infinite]"
            />
            <path
              d="M 120 220 C 240 220, 240 300, 360 300"
              stroke="url(#grad-pulse)"
              strokeWidth="2"
              fill="none"
              strokeDasharray="6 6"
            />
            <path
              d="M 440 140 C 560 140, 560 220, 680 220"
              stroke="url(#grad-pulse)"
              strokeWidth="2"
              fill="none"
              strokeDasharray="6 6"
            />
            <path
              d="M 440 300 C 560 300, 560 220, 680 220"
              stroke="url(#grad-pulse)"
              strokeWidth="2"
              fill="none"
              strokeDasharray="6 6"
            />
            <path
              d="M 760 220 C 840 220, 840 220, 920 220"
              stroke="url(#grad-pulse)"
              strokeWidth="2.5"
              fill="none"
            />
          </svg>

          {/* Responsive Node Cards Grid / Spatial presentation */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 w-full relative z-10">
            {nodes.map((node) => {
              const Icon = node.icon;
              const isSelected = activeNode === node.id;

              return (
                <motion.div
                  key={node.id}
                  whileHover={{ scale: 1.04, y: -4 }}
                  onClick={() => setActiveNode(node.id)}
                  className={`cursor-pointer rounded-2xl p-4 transition-all duration-300 ${
                    isSelected
                      ? "bg-white dark:bg-slate-800 shadow-xl border-2 border-slate-900 dark:border-white ring-4 ring-slate-900/5 dark:ring-white/10"
                      : "bg-white/80 dark:bg-slate-900/80 shadow-md border border-slate-200/80 dark:border-slate-800 hover:border-slate-400"
                  }`}
                  data-cursor-expand
                >
                  <div className="flex items-center justify-between mb-3">
                    <div
                      className={`p-2 rounded-xl ${
                        isSelected
                          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-950"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
                      {node.badge}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                    {node.title}
                  </h3>
                  <div className="text-[11px] font-mono text-slate-400 mb-2">
                    {node.category}
                  </div>
                  <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-snug">
                    {node.desc}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
