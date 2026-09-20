"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { Sparkles, Cpu, ShieldCheck } from "lucide-react";

export default function DarkVision() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Three.js Scene for Dark Bioluminescent Fluid Orbs
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050509, 0.05);

    const camera = new THREE.PerspectiveCamera(
      45,
      canvas.clientWidth / canvas.clientHeight,
      0.1,
      100
    );
    camera.position.set(0, 0, 6.5);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;

    // Lights
    const ambientLight = new THREE.AmbientLight(0x1a1a2e, 1.2);
    scene.add(ambientLight);

    const purpleLight = new THREE.PointLight(0xa855f7, 4.0, 15);
    purpleLight.position.set(3, 3, 2);
    scene.add(purpleLight);

    const blueLight = new THREE.PointLight(0x3b82f6, 4.0, 15);
    blueLight.position.set(-3, -2, 2);
    scene.add(blueLight);

    const emeraldRim = new THREE.PointLight(0x10b981, 2.5, 12);
    emeraldRim.position.set(0, 4, -2);
    scene.add(emeraldRim);

    // Bioluminescent Liquid Orb Mesh
    const sphereGeo = new THREE.SphereGeometry(1.6, 64, 64);
    const sphereMat = new THREE.MeshPhysicalMaterial({
      color: 0x0e0e18,
      emissive: 0x180b2a,
      emissiveIntensity: 0.5,
      roughness: 0.1,
      metalness: 0.9,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      transmission: 0.4,
      ior: 1.6,
    });
    const darkOrb = new THREE.Mesh(sphereGeo, sphereMat);
    scene.add(darkOrb);

    // Orbiting Satellite Beads
    const beads: THREE.Mesh[] = [];
    const beadColors = [0x60a5fa, 0xc084fc, 0x34d399, 0xf472b6];
    for (let i = 0; i < 6; i++) {
      const bGeo = new THREE.SphereGeometry(0.2 + (i % 3) * 0.1, 32, 32);
      const bMat = new THREE.MeshStandardMaterial({
        color: beadColors[i % beadColors.length],
        roughness: 0.2,
        metalness: 0.8,
      });
      const bMesh = new THREE.Mesh(bGeo, bMat);
      scene.add(bMesh);
      beads.push(bMesh);
    }

    // Particle Cloud
    const particleCount = 120;
    const pGeo = new THREE.BufferGeometry();
    const pPos = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      pPos[i] = (Math.random() - 0.5) * 12;
      pPos[i + 1] = (Math.random() - 0.5) * 8;
      pPos[i + 2] = (Math.random() - 0.5) * 6;
    }
    pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({
      size: 0.04,
      color: 0x93c5fd,
      transparent: true,
      opacity: 0.6,
    });
    const particleSystem = new THREE.Points(pGeo, pMat);
    scene.add(particleSystem);

    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const onMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      targetX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      targetY = -((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };

    window.addEventListener("mousemove", onMouseMove);

    const onResize = () => {
      if (!canvas) return;
      camera.aspect = canvas.clientWidth / canvas.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    };
    window.addEventListener("resize", onResize);

    let clock = new THREE.Clock();
    let animId: number;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      mouseX += (targetX - mouseX) * 0.05;
      mouseY += (targetY - mouseY) * 0.05;

      darkOrb.rotation.y = elapsed * 0.12;
      darkOrb.rotation.x = Math.sin(elapsed * 0.2) * 0.15;
      darkOrb.position.x = mouseX * 0.4;
      darkOrb.position.y = mouseY * 0.3;

      beads.forEach((bead, i) => {
        const angle = elapsed * 0.4 + (i * Math.PI) / 3;
        const radius = 2.4 + Math.sin(elapsed * 0.5 + i) * 0.3;
        bead.position.x = Math.cos(angle) * radius + mouseX * 0.5;
        bead.position.y = Math.sin(angle * 0.8) * 1.2 + mouseY * 0.3;
        bead.position.z = Math.sin(angle) * radius * 0.5;
      });

      particleSystem.rotation.y = elapsed * 0.03;

      purpleLight.position.x = 3 + mouseX * 2;
      blueLight.position.y = -2 + mouseY * 2;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
      sphereGeo.dispose();
      sphereMat.dispose();
      pGeo.dispose();
      pMat.dispose();
    };
  }, []);

  return (
    <section className="relative min-h-screen bg-[#050508] text-white py-28 sm:py-36 z-20 overflow-hidden flex items-center justify-center">
      {/* 3D WebGL Canvas Layer */}
      <div className="absolute inset-0 z-0 opacity-80 pointer-events-none">
        <canvas ref={canvasRef} className="w-full h-full block" />
      </div>

      {/* Atmospheric Glow */}
      <div className="absolute inset-0 radial-dark-glow pointer-events-none" />

      {/* Foreground Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs font-semibold uppercase tracking-wider text-slate-300">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          <span>Cinematic Autonomous Cloud</span>
        </div>

        <h2 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.08]">
          The future of software is <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400">
            ambient and autonomous.
          </span>
        </h2>

        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-400 leading-relaxed">
          No clusters to manage. No cold starts to fear. Zero manual IAM policy authoring.
          SmallOps continuously harmonizes state, compute, and security so you can focus on building.
        </p>

        <div className="pt-6 flex flex-wrap items-center justify-center gap-4">
          <div className="px-5 py-3 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 flex items-center gap-3">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-mono text-slate-300">
              AWS Graviton3 ARM64 Runtime
            </span>
          </div>
          <div className="px-5 py-3 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 flex items-center gap-3">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono text-slate-300">
              Cognito RS256 Auth Shield
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
