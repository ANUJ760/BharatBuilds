"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Lock,
  TrendingUp,
  ShieldCheck,
  Zap,
  Database,
} from "lucide-react";

export default function AppShowcase() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "decision" | "api">("dashboard");

  const transactions = [
    { id: "TX-8921", target: "Quant Sector Hedge", score: "+18.4%", risk: "Low", status: "Executed" },
    { id: "TX-8922", target: "Treasury Yield Arbitrage", score: "+4.2%", risk: "Minimal", status: "Executed" },
    { id: "TX-8923", target: "Semiconductor Mean Reversion", score: "-1.1%", risk: "Medium", status: "Rebalanced" },
    { id: "TX-8924", target: "FX EUR/USD Momentum", score: "+9.8%", risk: "Low", status: "Executed" },
  ];

  return (
    <section id="showcase" className="relative py-24 sm:py-32 z-10 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12 sm:mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-200/60 dark:bg-slate-800/60 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            <span>Realistic Generated Output</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-slate-950 dark:text-white">
            Describe it. Generate it. Ship it.
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300">
            Real software running in real environments. Built with high-fidelity components,
            authenticated backend APIs, and AWS multi-region durability.
          </p>
        </div>

        {/* Premium Browser Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="rounded-3xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl shadow-slate-900/10 overflow-hidden"
        >
          {/* Browser Chrome Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-100/90 dark:bg-slate-950 border-b border-slate-200/80 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-400" />
              <span className="w-3 h-3 rounded-full bg-amber-400" />
              <span className="w-3 h-3 rounded-full bg-emerald-400" />
            </div>

            {/* URL Bar */}
            <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-600 dark:text-slate-300 max-w-md w-full mx-4 shadow-sm justify-center">
              <Lock className="w-3.5 h-3.5 text-emerald-500" />
              <span className="truncate">https://alphayield.app.bharatbuilds.aws</span>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
              <span className="hidden sm:inline-block w-2 h-2 rounded-full bg-emerald-500" />
              <span className="hidden sm:inline">AWS ap-south-1</span>
            </div>
          </div>

          {/* Browser Interior App Content */}
          <div className="p-5 sm:p-8 bg-slate-50/50 dark:bg-slate-950/50 space-y-6">
            {/* App Nav inside mockup */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-900 dark:bg-white flex items-center justify-center text-white dark:text-slate-950 font-bold text-xs shadow">
                  AY
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    AlphaYield Terminal
                  </h3>
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>Cognito Identity Pool Verified</span>
                  </div>
                </div>
              </div>

              {/* View Switcher Tabs */}
              <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-200/60 dark:bg-slate-800/80 text-xs font-medium">
                <button
                  onClick={() => setActiveTab("dashboard")}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    activeTab === "dashboard"
                      ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                  data-cursor-expand
                >
                  Live Workspace
                </button>
                <button
                  onClick={() => setActiveTab("decision")}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    activeTab === "decision"
                      ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                  data-cursor-expand
                >
                  Decision Trail
                </button>
                <button
                  onClick={() => setActiveTab("api")}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    activeTab === "api"
                      ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                  data-cursor-expand
                >
                  Cloud Endpoints
                </button>
              </div>
            </div>

            {/* Metrics Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-[11px] font-medium text-slate-400 uppercase">Capital Under Risk</span>
                <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">$1.84M</div>
                <div className="flex items-center gap-1 text-[11px] text-emerald-500 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>+12.4% vs index</span>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-[11px] font-medium text-slate-400 uppercase">Lambda P99 Latency</span>
                <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">16.2 ms</div>
                <div className="flex items-center gap-1 text-[11px] text-emerald-500 mt-1">
                  <Zap className="w-3 h-3" />
                  <span>Edge warmed</span>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-[11px] font-medium text-slate-400 uppercase">DynamoDB Read/Write</span>
                <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">0 Errors</div>
                <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-1">
                  <Database className="w-3 h-3" />
                  <span>On-demand capacity</span>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-[11px] font-medium text-slate-400 uppercase">Cognito Auth</span>
                <div className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">Enforced</div>
                <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-1">
                  <ShieldCheck className="w-3 h-3" />
                  <span>JWT RS256</span>
                </div>
              </div>
            </div>

            {/* Main Interactive Table / Decision View */}
            {activeTab === "dashboard" && (
              <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 overflow-hidden shadow-sm">
                <div className="flex items-center justify-between p-3.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                    Live Sector Portfolio Allocations
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-slate-400">Sync: 1s polling</span>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400">
                        <th className="p-3 font-medium">Position ID</th>
                        <th className="p-3 font-medium">Asset / Strategy</th>
                        <th className="p-3 font-medium">Performance</th>
                        <th className="p-3 font-medium">Risk Score</th>
                        <th className="p-3 font-medium">State</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {transactions.map((tx) => (
                        <tr key={tx.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                          <td className="p-3 font-mono text-slate-500">{tx.id}</td>
                          <td className="p-3 font-medium text-slate-800 dark:text-slate-200">{tx.target}</td>
                          <td className="p-3 text-emerald-600 font-semibold">{tx.score}</td>
                          <td className="p-3 text-slate-600 dark:text-slate-400">{tx.risk}</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                              {tx.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === "decision" && (
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-3">
                <h4 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Autonomous Agent Reasoning Audit
                </h4>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 text-xs space-y-1">
                  <span className="font-semibold text-slate-900 dark:text-white">Decision: Selected DynamoDB Partition Key `tenant_id`</span>
                  <p className="text-slate-500">
                    Reason: Multi-tenant safety requires composite partition keys with `created_at` sort key to enable sub-10ms queries.
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 text-xs space-y-1">
                  <span className="font-semibold text-slate-900 dark:text-white">Decision: Attached AWS Cognito User Pool Authorizer</span>
                  <p className="text-slate-500">
                    Reason: User prompt specified financial data; unauthenticated public routes were rejected by security policy.
                  </p>
                </div>
              </div>
            )}

            {activeTab === "api" && (
              <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 font-mono text-xs space-y-2">
                <div className="p-2.5 rounded-xl bg-slate-950 text-emerald-400">
                  POST https://api.alphayield.app.bharatbuilds.aws/v1/rebalance
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950 text-blue-400">
                  GET https://api.alphayield.app.bharatbuilds.aws/v1/positions?tenant_id=BB-2026
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
