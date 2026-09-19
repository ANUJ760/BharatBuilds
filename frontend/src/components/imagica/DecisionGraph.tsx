"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  GitCommit,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Database,
  Shield,
  Cpu,
  Layers,
  Sparkles,
} from "lucide-react";

interface DecisionNode {
  id: string;
  step: string;
  title: string;
  selectedOption: string;
  rejectedOption: string;
  confidence: number;
  icon: React.ElementType;
  rationale: string;
  policy: string;
}

export default function DecisionGraph() {
  const decisions: DecisionNode[] = [
    {
      id: "storage",
      step: "01 / Persistence Engine",
      title: "Storage Engine Selection",
      selectedOption: "Amazon DynamoDB (On-Demand Single-Table)",
      rejectedOption: "Amazon RDS Aurora Postgres",
      confidence: 98.4,
      icon: Database,
      rationale:
        "Prompt required instantaneous spin-up under 60 seconds with zero idle cost. Aurora Serverless has a 25-45s cold start for VPC ENI attachment; DynamoDB provides sub-10ms key-value latency and scale-to-zero pricing.",
      policy: `{
  "Effect": "Allow",
  "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query"],
  "Resource": "arn:aws:dynamodb:ap-south-1:*:table/AlphaYield-*"
}`,
    },
    {
      id: "auth",
      step: "02 / Security Perimeter",
      title: "Authentication & Authorization Tier",
      selectedOption: "AWS Cognito User Pool + JWT Authorizer",
      rejectedOption: "Custom API Keys / Unauthenticated Routes",
      confidence: 99.2,
      icon: Shield,
      rationale:
        "Prompt contains sensitive business data. Public endpoints rejected by automated security gate. Configured Amazon Cognito User Pool with RS256 token verification on all mutation endpoints.",
      policy: `{
  "Type": "AWS::ApiGateway::Authorizer",
  "Properties": {
    "Type": "COGNITO_USER_POOLS",
    "ProviderARNs": ["arn:aws:cognito-idp:ap-south-1:*:userpool/*"]
  }
}`,
    },
    {
      id: "compute",
      step: "03 / Compute Architecture",
      title: "Runtime Execution Sizing",
      selectedOption: "AWS Lambda (1024MB ARM64 Graviton3)",
      rejectedOption: "AWS Lambda (x86_64 512MB)",
      confidence: 94.6,
      icon: Cpu,
      rationale:
        "Graviton3 ARM64 provides 20% lower cost and 34% faster cold-starts for Node.js 20. 1024MB allocates 0.6 vCPU proportionally, cutting P99 latency to 16ms.",
      policy: `{
  "Architecture": "arm64",
  "MemorySize": 1024,
  "Timeout": 15,
  "Runtime": "nodejs20.x"
}`,
    },
    {
      id: "cdn",
      step: "04 / Edge Distribution",
      title: "Edge Caching & SSL Termination",
      selectedOption: "Amazon CloudFront + S3 Origin",
      rejectedOption: "Direct API Gateway Custom Domain",
      confidence: 96.8,
      icon: Layers,
      rationale:
        "Global edge caching with HTTP/3 support ensures international teams experience sub-80ms initial load. Automatic TLS 1.3 certificates provisioned via AWS Certificate Manager.",
      policy: `{
  "CachePolicy": "Managed-CachingOptimized",
  "ViewerProtocolPolicy": "redirect-to-https",
  "HttpVersion": "http2and3"
}`,
    },
  ];

  const [selectedDecision, setSelectedDecision] = useState<DecisionNode>(decisions[0]);

  return (
    <section id="decision-graph" className="relative py-28 sm:py-36 z-10 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-200/60 dark:bg-slate-800/60 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            <span>Deterministic Transparency</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-slate-950 dark:text-white">
            Software that reasons about what happens next.
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300">
            A full visual record of every decision the agent made along the way.
            Inspect tradeoffs, chosen primitives, and security policies.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Decision Timeline Nodes */}
          <div className="lg:col-span-5 space-y-3">
            {decisions.map((node) => {
              const Icon = node.icon;
              const isCurrent = selectedDecision.id === node.id;

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedDecision(node)}
                  className={`p-5 rounded-2xl cursor-pointer transition-all duration-300 border ${
                    isCurrent
                      ? "bg-white dark:bg-slate-800 shadow-xl border-slate-900/20 dark:border-white/20 ring-2 ring-slate-900/5 dark:ring-white/10"
                      : "bg-white/60 dark:bg-slate-900/60 border-slate-200/60 dark:border-slate-800 hover:bg-white/90"
                  }`}
                  data-cursor-expand
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-mono text-slate-400 font-medium">
                      {node.step}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                      {node.confidence}% Confidence
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-xl ${
                        isCurrent
                          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-950"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                        {node.title}
                      </h4>
                      <p className="text-xs text-slate-500 line-clamp-1">
                        {node.selectedOption}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Decision Inspector Panel */}
          <div className="lg:col-span-7">
            <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xl space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <span className="text-xs font-mono text-slate-400">
                    Decision Inspector // {selectedDecision.step}
                  </span>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">
                    {selectedDecision.title}
                  </h3>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                  Autonomous Trail
                </span>
              </div>

              {/* Chosen vs Rejected Comparison */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-4 rounded-2xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-900 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-300">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Selected Solution</span>
                  </div>
                  <div className="text-xs font-semibold text-slate-900 dark:text-white">
                    {selectedDecision.selectedOption}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-rose-700 dark:text-rose-300">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>Rejected Alternative</span>
                  </div>
                  <div className="text-xs font-semibold text-slate-900 dark:text-white">
                    {selectedDecision.rejectedOption}
                  </div>
                </div>
              </div>

              {/* Rationale explanation */}
              <div className="space-y-2">
                <h5 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Architectural Tradeoff Rationale
                </h5>
                <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-950 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
                  {selectedDecision.rationale}
                </p>
              </div>

              {/* Synthesized IAM/CDK Policy Snippet */}
              <div className="space-y-2">
                <h5 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Synthesized AWS CDK Definition
                </h5>
                <pre className="p-4 rounded-2xl bg-slate-950 text-slate-300 font-mono text-xs overflow-x-auto border border-slate-800 leading-relaxed">
                  <code>{selectedDecision.policy}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
