import { Scene3D } from '../components/Scene3D';
import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();
  const featuresRef = useRef<HTMLElement>(null);
  const timelineRef = useRef<HTMLElement>(null);
  const { scrollY } = useScroll();
  
  // Hero section parallax
  const heroY = useTransform(scrollY, [0, 500], [0, 100]);
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0]);
  
  const scrollTo = (ref: React.RefObject<HTMLElement>) => {
    if (ref.current) {
      window.scrollTo({ top: ref.current.offsetTop, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white text-black font-sans selection:bg-black selection:text-white overflow-x-hidden">
      {/* Fixed Background 3D Scene */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <Scene3D scrollY={scrollY} />
      </div>

      {/* Navigation - Glassmorphism */}
      <nav className="fixed top-0 w-full z-50 px-8 py-6 flex justify-between items-center bg-white/40 backdrop-blur-xl border-b border-white/50">
        <div className="text-xl tracking-tighter font-medium flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-black"></div>
          Small Software Cloud
        </div>
        <div className="flex gap-8 text-sm font-medium tracking-wide">
          <button onClick={() => scrollTo(featuresRef)} className="hover:opacity-60 transition-opacity">Features</button>
          <button onClick={() => scrollTo(timelineRef)} className="hover:opacity-60 transition-opacity">Decision Graph</button>
        </div>
        <button 
          onClick={() => navigate('/create')}
          className="px-6 py-2.5 bg-black text-white rounded-full text-sm font-medium hover:scale-105 transition-transform"
        >
          Launch App
        </button>
      </nav>

      {/* Content Layer */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-screen flex flex-col items-center justify-center text-center px-4 pt-20">
          <motion.h1 
            style={{ y: heroY, opacity: heroOpacity }}
            className="text-[5.5rem] leading-[0.9] font-medium tracking-tighter max-w-5xl"
          >
            A cloud for small software.
          </motion.h1>
          <motion.p 
            style={{ y: heroY, opacity: heroOpacity }}
            className="mt-8 text-xl text-gray-500 max-w-2xl font-light"
          >
            Turn a plain-language prompt into a live, authenticated, shareable web app in under a minute. 
            Deployed instantly on real AWS infrastructure.
          </motion.p>
          <motion.div 
            style={{ y: heroY, opacity: heroOpacity }}
            className="mt-16 flex gap-4"
          >
            <button 
              onClick={() => navigate('/create')}
              className="px-8 py-4 bg-black text-white rounded-full font-medium hover:bg-gray-900 transition-colors"
            >
              Start Generating
            </button>
          </motion.div>
        </section>

        {/* Features Section */}
        <section ref={featuresRef} className="min-h-screen py-32 px-8 max-w-7xl mx-auto flex flex-col justify-center">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-24 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              <h2 className="text-5xl font-medium tracking-tighter mb-8">Clarify, then build.</h2>
              <p className="text-lg text-gray-500 font-light mb-8">
                If your request is ambiguous, the agent asks up to 3 targeted questions before writing code. No open-ended back-and-forth. Once resolved, the build proceeds without interruption.
              </p>
              <ul className="space-y-6">
                {[
                  'Agentic reasoning via Amazon Bedrock',
                  'Instant isolated AWS Fargate deployment',
                  'Zero-config Auth & Sharing out of the box'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-4 text-lg font-medium">
                    <div className="w-2 h-2 rounded-full bg-black"></div>
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
            
            {/* Feature Cards - Glassmorphic */}
            <div className="grid gap-6">
              {[
                {
                  icon: 'lock',
                  title: 'Zero-Config Auth',
                  desc: 'Every generated app is wrapped in Cognito authentication instantly. Invite viewers or editors via email with zero code changes.'
                },
                {
                  icon: 'cloud_sync',
                  title: 'Live Editing',
                  desc: 'Ask the agent to add a summary view or a new field. The app edits itself and redeploys to the same live URL.'
                },
                {
                  icon: 'speed',
                  title: 'Instant AWS Deploy',
                  desc: 'We bypass the complexity of big software. Your micro-app is containerized and live on a public URL in 10-20 seconds.'
                }
              ].map((feature, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.6, delay: i * 0.15, ease: "easeOut" }}
                  className="p-8 rounded-3xl bg-white/40 backdrop-blur-xl border border-white/60 shadow-[0_8px_32px_rgba(0,0,0,0.04)]"
                >
                  <div className="w-12 h-12 rounded-full bg-black/5 mb-6 flex items-center justify-center">
                    <span className="material-symbols-outlined text-xl">{feature.icon}</span>
                  </div>
                  <h3 className="text-xl font-medium mb-2">{feature.title}</h3>
                  <p className="text-gray-500">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* High Contrast Dark Mode Section - The Decision Timeline */}
        <section ref={timelineRef} className="min-h-screen bg-[#050505] text-white py-32 px-8 mt-24 relative overflow-hidden flex flex-col justify-center">
          {/* Subtle glow effect behind */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-white/5 rounded-full blur-[120px] pointer-events-none"></div>
          
          <div className="max-w-7xl mx-auto relative z-10 grid grid-cols-1 md:grid-cols-2 gap-24 items-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-6xl font-medium tracking-tighter mb-8 text-[#e5e2e1]">The Decision Timeline.</h2>
              <p className="text-xl text-[#a1a1aa] font-light mb-8">
                Trust requires transparency. Every agent action — plan, tool call, generated code, retry, and deploy — is logged as a visual node in a tree.
              </p>
            </motion.div>

            <motion.div 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              variants={{
                visible: { transition: { staggerChildren: 0.3 } },
                hidden: {}
              }}
              className="flex flex-col gap-6 border-l border-white/10 pl-8 relative before:content-[''] before:absolute before:left-[-1px] before:top-0 before:w-[2px] before:h-1/3 before:bg-white/40"
            >
              {[
                { step: 1, title: 'Clarify Ambiguity', desc: 'Asked user for required fields', style: 'bg-[#141313]', text: 'text-white' },
                { step: 2, title: 'Generate Code', desc: 'Written 142 lines of React', style: 'bg-[#141313]', text: 'text-white' },
                { step: 3, title: 'Deploy to Fargate', desc: 'Live URL generated in 12s', style: 'bg-[#141313] border-[#4edea3]/30 shadow-[0_0_15px_-3px_rgba(78,222,163,0.1)]', text: 'text-[#4edea3]' }
              ].map((item, i) => (
                <motion.div 
                  key={i}
                  variants={{
                    hidden: { opacity: 0, x: 30 },
                    visible: { opacity: 1, x: 0, transition: { type: "spring", stiffness: 100 } }
                  }}
                  className={`p-6 rounded-2xl border border-white/10 relative ${item.style}`}
                >
                  <div className={`absolute -left-[33px] top-1/2 w-[32px] h-[2px] ${item.step === 3 ? 'bg-[#4edea3]/30' : 'bg-white/10'}`}></div>
                  <div className={`text-xs ${item.step === 3 ? 'text-[#4edea3]' : 'text-[#a1a1aa]'} mb-2 uppercase tracking-wider`}>Step {item.step}</div>
                  <div className={`text-lg font-medium ${item.text}`}>{item.title}</div>
                  <div className="text-sm text-[#71717a] mt-1">{item.desc}</div>
                </motion.div>
              ))}
              
              <motion.div 
                variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: { delay: 1 } } }}
                className="mt-4 pt-4 border-t border-white/10"
              >
                <p className="text-sm text-[#71717a]">
                  Made a mistake? Click any node to instantly <span className="text-white font-medium">Revert to here</span>, rolling the live app back.
                </p>
              </motion.div>
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  );
}
