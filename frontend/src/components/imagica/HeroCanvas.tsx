"use client";

import React, { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HeroCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xe8e8e8);

    const camera = new THREE.PerspectiveCamera(
      40,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );
    camera.position.set(0, 2.5, 8);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Lighting — soft studio setup matching video
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 2.0);
    keyLight.position.set(5, 10, 7);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.camera.near = 0.1;
    keyLight.shadow.camera.far = 50;
    keyLight.shadow.camera.left = -10;
    keyLight.shadow.camera.right = 10;
    keyLight.shadow.camera.top = 10;
    keyLight.shadow.camera.bottom = -10;
    keyLight.shadow.bias = -0.0001;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xeef2ff, 1.2);
    fillLight.position.set(-5, 3, 5);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xfff0e8, 0.8);
    rimLight.position.set(0, -2, -5);
    scene.add(rimLight);

    // Main glossy white sphere — central hero object
    const sphereGeo = new THREE.SphereGeometry(1.6, 128, 128);
    const sphereMat = new THREE.MeshPhysicalMaterial({
      color: 0xf5f5f5,
      roughness: 0.08,
      metalness: 0.02,
      clearcoat: 1.0,
      clearcoatRoughness: 0.05,
      reflectivity: 0.9,
      envMapIntensity: 1.0,
      transparent: true,
    });
    const mainSphere = new THREE.Mesh(sphereGeo, sphereMat);
    mainSphere.position.set(0, 0.8, 0);
    mainSphere.castShadow = true;
    scene.add(mainSphere);

    // Extra bubbles (colliding, still, hoverable)
    const bubbles: THREE.Mesh[] = [];
    for (let i = 0; i < 4; i++) {
      // Clone material so we can adjust it per-bubble if we want
      const bMat = sphereMat.clone();
      const bMesh = new THREE.Mesh(sphereGeo, bMat);
      
      const isStill = i === 0; // Make one bubble still
      
      bMesh.position.set(
        (Math.random() - 0.5) * 6, 
        0.5 + Math.random() * 2, 
        -1 - Math.random() * 3
      );
      
      bMesh.userData = {
        velocity: isStill ? new THREE.Vector3(0,0,0) : new THREE.Vector3((Math.random() - 0.5) * 0.02, (Math.random() - 0.5) * 0.02, (Math.random() - 0.5) * 0.02),
        baseScale: 0.3 + Math.random() * 0.3,
        hoverScale: 1.0,
        isStill
      };
      
      bMesh.scale.setScalar(bMesh.userData.baseScale);
      bMesh.castShadow = true;
      scene.add(bMesh);
      bubbles.push(bMesh);
    }

    // Water ripple plane — concentric circles emanating from sphere
    const rippleGeo = new THREE.PlaneGeometry(30, 30, 256, 256);
    const rippleMat = new THREE.MeshPhysicalMaterial({
      color: 0xe2e2e2,
      roughness: 0.15,
      metalness: 0.05,
      clearcoat: 0.5,
      clearcoatRoughness: 0.2,
    });
    const ripplePlane = new THREE.Mesh(rippleGeo, rippleMat);
    ripplePlane.rotation.x = -Math.PI / 2;
    ripplePlane.position.y = -0.8;
    ripplePlane.receiveShadow = true;
    scene.add(ripplePlane);

    // Animate water ripples on the plane geometry
    const originalPositions = rippleGeo.attributes.position.array.slice();

    // Mouse tracking & Raycasting
    let mouseX = 0;
    let mouseY = 0;
    let targetMouseX = 0;
    let targetMouseY = 0;
    let scrollY = 0;
    let targetScrollY = 0;
    
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-100, -100);

    const onMouseMove = (e: MouseEvent) => {
      targetMouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      targetMouseY = -(e.clientY / window.innerHeight - 0.5) * 2;
      
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
    };

    const onScroll = () => {
      targetScrollY = window.scrollY;
    };

    const onResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    
    // Burst animation state
    let isBursting = false;
    let burstProgress = 0;
    const onBurst = () => { isBursting = true; };
    window.addEventListener("burst-auth", onBurst);

    const clock = new THREE.Clock();
    let animId: number;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      // Smooth mouse
      mouseX += (targetMouseX - mouseX) * 0.03;
      mouseY += (targetMouseY - mouseY) * 0.03;

      // Smooth scroll
      scrollY += (targetScrollY - scrollY) * 0.05;
      const scrollNorm = Math.min(scrollY / (window.innerHeight * 0.8), 1.0);

      // Animate water ripple displacement
      const positions = rippleGeo.attributes.position.array as Float32Array;
      for (let i = 0; i < positions.length; i += 3) {
        const ox = originalPositions[i];
        const oz = originalPositions[i + 2];
        const dist = Math.sqrt(ox * ox + oz * oz);
        // Concentric waves from center
        const wave1 = Math.sin(dist * 1.8 - t * 1.5) * 0.12 * Math.max(0, 1 - dist * 0.06);
        const wave2 = Math.sin(dist * 2.5 - t * 2.0 + 1.0) * 0.06 * Math.max(0, 1 - dist * 0.08);
        positions[i + 1] = wave1 + wave2;
      }
      rippleGeo.attributes.position.needsUpdate = true;
      rippleGeo.computeVertexNormals();

      // Sphere subtle animation
      mainSphere.position.y = 0.8 + Math.sin(t * 0.8) * 0.06;
      mainSphere.rotation.y = t * 0.05;

      // Camera responds to mouse subtly
      if (!isBursting) {
        camera.position.x = mouseX * 0.6;
        camera.position.y = 2.5 + mouseY * 0.3;
        camera.lookAt(0, 0 - scrollNorm * 1.5, 0);

        // On scroll, sphere moves down
        mainSphere.position.y = 0.8 + Math.sin(t * 0.8) * 0.06 - scrollNorm * 3;
        mainSphere.position.z = 0;
        mainSphere.scale.setScalar(1);
      } else {
        // Burst animation taking over
        burstProgress += 0.05;
        mainSphere.position.z += 0.4;
        mainSphere.scale.setScalar(1 + burstProgress * 6);
        (mainSphere.material as THREE.MeshPhysicalMaterial).opacity = 1 - burstProgress * 0.1;
      }
      
      ripplePlane.position.y = -0.8 - scrollNorm * 2;

      // Update bubbles (floating, hover, collision)
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(bubbles);
      const hoveredBubble = intersects.length > 0 ? intersects[0].object : null;

      bubbles.forEach(b => {
        // Hover scaling
        if (hoveredBubble === b) {
          b.userData.hoverScale += (1.4 - b.userData.hoverScale) * 0.15;
          (b.material as THREE.MeshPhysicalMaterial).emissive = new THREE.Color(0x222222);
        } else {
          b.userData.hoverScale += (1.0 - b.userData.hoverScale) * 0.1;
          (b.material as THREE.MeshPhysicalMaterial).emissive = new THREE.Color(0x000000);
        }
        b.scale.setScalar(b.userData.baseScale * b.userData.hoverScale);
        
        // Floating & boundaries
        if (!b.userData.isStill) {
          b.position.add(b.userData.velocity);
          if (b.position.x > 4 || b.position.x < -4) b.userData.velocity.x *= -1;
          if (b.position.y > 3 || b.position.y < 0) b.userData.velocity.y *= -1;
          if (b.position.z > 1 || b.position.z < -5) b.userData.velocity.z *= -1;
        } else {
          // Still bubble just bobs gently
          b.position.y += Math.sin(t * 1.2 + b.id) * 0.002;
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("burst-auth", onBurst);
      renderer.dispose();
      sphereGeo.dispose();
      sphereMat.dispose();
      rippleGeo.dispose();
      rippleMat.dispose();
    };
  }, []);

  return (
    <div className="three-canvas-wrap">
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
}
