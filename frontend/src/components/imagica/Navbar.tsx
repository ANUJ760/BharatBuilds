"use client";

import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const links = [
    { name: "Product", href: "#product" },
    { name: "How it works", href: "#how-it-works" },
    { name: "Features", href: "#features" },
    { name: "Mission", href: "#mission" },
  ];

  const isAuthenticated = !!(localStorage.getItem('bb_token') || sessionStorage.getItem('bb_token'));

  const handleNavClick = (e: React.MouseEvent, path: string) => {
    e.preventDefault();
    // Trigger burst animation in 3D canvas
    window.dispatchEvent(new CustomEvent('burst-auth'));
    // Wait for pour animation to mostly finish, then navigate
    setTimeout(() => {
      navigate(path);
    }, 900); // Navigate slightly before pour finishes to allow destination page to rise up
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-10 py-5">
      {/* Logo — matching the circle-dot + text from video */}
      <a href="#" className="flex items-center gap-2.5">
        <div className="relative w-7 h-7 rounded-full border-[2px] border-[#111] flex items-center justify-center">
          <div className="w-1.5 h-1.5 rounded-full bg-[#111] absolute -left-1 top-1/2 -translate-y-1/2" />
        </div>
        <span className="text-[15px] font-semibold tracking-[-0.02em] text-[#111]">
          Small Software Cloud
        </span>
      </a>

      {/* Center nav links */}
      <div className="hidden md:flex items-center gap-8">
        {links.map((link) => (
          <a
            key={link.name}
            href={link.href}
            className="text-[14px] font-normal text-[#555] hover:text-[#111] transition-colors duration-200"
          >
            {link.name}
          </a>
        ))}
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-3">
        {isAuthenticated && (
          <a
            href="/dashboard"
            onClick={(e) => handleNavClick(e, "/dashboard")}
            className="px-5 py-2 rounded-full bg-transparent text-[13px] font-medium text-[#111] border border-black/10 hover:bg-black/5 transition-all duration-200 hidden md:block"
          >
            Dashboard
          </a>
        )}
        <a
          href={isAuthenticated ? "/create" : "/login"}
          onClick={(e) => handleNavClick(e, isAuthenticated ? "/create" : "/login")}
          className="px-5 py-2 rounded-full bg-white text-[13px] font-medium text-[#111] shadow-sm border border-white/80 hover:shadow-md transition-all duration-200"
        >
          {isAuthenticated ? "Launch App" : "Sign In"}
        </a>
      </div>
    </nav>
  );
}
