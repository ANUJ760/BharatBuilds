"use client";

import { useEffect, useRef } from "react";
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

    // Lighting — soft studio setup
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
    const sphereGeo = new THREE.SphereGeometry(1.6, 64, 64);
    const sphereMat = new THREE.MeshPhysicalMaterial({
      color: 0xf0f0f0,
      roughness: 0.02,
      metalness: 0.02,
      clearcoat: 1.0,
      clearcoatRoughness: 0.03,
      reflectivity: 0.95,
      envMapIntensity: 1.0,
      transparent: true,
    });
    const mainSphere = new THREE.Mesh(sphereGeo, sphereMat);
    mainSphere.position.set(0, 0.8, 0);
    mainSphere.castShadow = true;
    scene.add(mainSphere);

    // Store original vertices for liquid distortion effect
    const mainOriginalPositions = (sphereGeo.attributes.position.array as Float32Array).slice();
    let mainDistortAmount = 0; // current distort strength
    let mainDistortTarget = 0; // target distort strength

    // Extra bubbles — ALL greyish-white, NO blue
    const bubbleGeos: THREE.SphereGeometry[] = [];
    const bubbles: THREE.Mesh[] = [];
    for (let i = 0; i < 8; i++) {
      const bGeo = new THREE.SphereGeometry(1, 32, 32);
      bubbleGeos.push(bGeo);

      const bMat = new THREE.MeshPhysicalMaterial({
        color: new THREE.Color().setHSL(0, 0, 0.88 + Math.random() * 0.1), // greyish-white
        roughness: 0.02,
        metalness: 0.02,
        clearcoat: 1.0,
        clearcoatRoughness: 0.03,
        reflectivity: 0.9,
        envMapIntensity: 1.0,
      });

      const bMesh = new THREE.Mesh(bGeo, bMat);

      bMesh.position.set(
        (Math.random() - 0.5) * 12,
        0.5 + Math.random() * 4,
        -1 - Math.random() * 6
      );

      const baseScale = 0.15 + Math.random() * 0.4;
      bMesh.userData = {
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.06,
          (Math.random() - 0.5) * 0.06,
          (Math.random() - 0.5) * 0.04
        ),
        baseScale,
        originalPositions: (bGeo.attributes.position.array as Float32Array).slice(),
        distortAmount: 0,
        distortTarget: 0,
        isDragging: false,
      };

      bMesh.scale.setScalar(baseScale);
      bMesh.castShadow = true;
      scene.add(bMesh);
      bubbles.push(bMesh);
    }

    // Water ripple plane
    const rippleGeo = new THREE.PlaneGeometry(30, 30, 128, 128);
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

    const originalPositions = rippleGeo.attributes.position.array.slice();

    // Mouse tracking & Raycasting
    let mouseX = 0;
    let mouseY = 0;
    let targetMouseX = 0;
    let targetMouseY = 0;
    let scrollY = 0;
    let targetScrollY = 0;
    let isMouseDown = false;
    let draggedBubble: THREE.Mesh | null = null;
    const dragPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
    const dragIntersection = new THREE.Vector3();

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-100, -100);

    const onMouseMove = (e: MouseEvent) => {
      targetMouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      targetMouseY = -(e.clientY / window.innerHeight - 0.5) * 2;

      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

      // If dragging a bubble, move it along the drag plane
      if (isMouseDown && draggedBubble) {
        raycaster.setFromCamera(mouse, camera);
        raycaster.ray.intersectPlane(dragPlane, dragIntersection);
        draggedBubble.position.x = dragIntersection.x;
        draggedBubble.position.y = dragIntersection.y;
        draggedBubble.userData.velocity.set(0, 0, 0); // stop momentum while dragging
      }
    };

    const onMouseDown = (e: MouseEvent) => {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(bubbles);
      if (hits.length > 0) {
        isMouseDown = true;
        draggedBubble = hits[0].object as THREE.Mesh;
        draggedBubble.userData.isDragging = true;
        // Set drag plane at the bubble's z-depth
        dragPlane.setFromNormalAndCoplanarPoint(
          new THREE.Vector3(0, 0, 1),
          draggedBubble.position
        );
        canvas.style.cursor = 'grabbing';
      }
    };

    const onMouseUp = () => {
      if (draggedBubble) {
        draggedBubble.userData.isDragging = false;
        // Give it a small random velocity after releasing
        draggedBubble.userData.velocity.set(
          (Math.random() - 0.5) * 0.03,
          (Math.random() - 0.5) * 0.03,
          0
        );
        draggedBubble = null;
      }
      isMouseDown = false;
      canvas.style.cursor = 'default';
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
    window.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mouseup", onMouseUp);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);

    // Burst animation state
    let isBursting = false;
    let burstProgress = 0;
    const onBurst = () => {
      isBursting = true;
    };
    window.addEventListener("burst-auth", onBurst);

    const clock = new THREE.Clock();
    let animId: number;

    // Helper: apply liquid distort to a sphere geometry
    // Skip computation entirely when amount is negligible
    function applyLiquidDistort(
      geo: THREE.SphereGeometry,
      origPositions: Float32Array,
      amount: number,
      time: number,
      seed: number
    ) {
      if (amount < 0.005) return; // skip when barely visible
      const pos = geo.attributes.position.array as Float32Array;
      for (let i = 0; i < pos.length; i += 3) {
        const ox = origPositions[i];
        const oy = origPositions[i + 1];
        const oz = origPositions[i + 2];
        const dist = Math.sqrt(ox * ox + oy * oy + oz * oz);
        if (dist === 0) continue;
        const nx = ox / dist;
        const ny = oy / dist;
        const nz = oz / dist;
        // Simplified noise for performance
        const noise =
          Math.sin(nx * 4.0 + time * 3.0 + seed) * 0.5 +
          Math.sin(ny * 5.0 - time * 2.5 + seed * 0.7) * 0.5;
        const displacement = noise * amount;
        pos[i]     = ox + nx * displacement;
        pos[i + 1] = oy + ny * displacement;
        pos[i + 2] = oz + nz * displacement;
      }
      geo.attributes.position.needsUpdate = true;
      geo.computeVertexNormals();
    }

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      // Smooth mouse
      mouseX += (targetMouseX - mouseX) * 0.03;
      mouseY += (targetMouseY - mouseY) * 0.03;

      // Smooth scroll
      scrollY += (targetScrollY - scrollY) * 0.05;
      const scrollNorm = Math.min(scrollY / (window.innerHeight * 0.8), 1.0);

      // ── Water ripple displacement ──
      const positions = rippleGeo.attributes.position.array as Float32Array;
      for (let i = 0; i < positions.length; i += 3) {
        const ox = originalPositions[i];
        const oz = originalPositions[i + 2];
        const dist = Math.sqrt(ox * ox + oz * oz);
        const wave1 = Math.sin(dist * 1.8 - t * 1.5) * 0.12 * Math.max(0, 1 - dist * 0.06);
        const wave2 = Math.sin(dist * 2.5 - t * 2.0 + 1.0) * 0.06 * Math.max(0, 1 - dist * 0.08);
        positions[i + 1] = wave1 + wave2;
      }
      rippleGeo.attributes.position.needsUpdate = true;
      rippleGeo.computeVertexNormals();

      // ── Main sphere: liquid distortion on hover ──
      raycaster.setFromCamera(mouse, camera);
      const mainHits = raycaster.intersectObject(mainSphere);
      mainDistortTarget = mainHits.length > 0 ? 0.15 : 0.03; // idle wobble vs hover wobble
      mainDistortAmount += (mainDistortTarget - mainDistortAmount) * 0.06;
      applyLiquidDistort(sphereGeo, mainOriginalPositions, mainDistortAmount, t, 0);

      // Sphere subtle animation
      mainSphere.rotation.y = t * 0.08;

      // Camera responds to mouse subtly
      if (!isBursting) {
        camera.position.x = mouseX * 0.6;
        camera.position.y = 2.5 + mouseY * 0.3;
        camera.lookAt(0, 0 - scrollNorm * 1.5, 0);
        mainSphere.position.y = 0.8 + Math.sin(t * 0.8) * 0.06 - scrollNorm * 3;
        mainSphere.position.z = 0;
        mainSphere.scale.setScalar(1);
      } else {
        burstProgress += 0.03;
        const shrinkScale = Math.max(0, 1 - burstProgress * 1.5);
        mainSphere.scale.setScalar(shrinkScale);
        mainSphere.rotation.y += 0.1;
      }

      ripplePlane.position.y = -0.8 - scrollNorm * 2;

      // ── Bubbles: liquid distortion + drag + float ──
      const bubbleHits = raycaster.intersectObjects(bubbles);
      const hoveredBubble = bubbleHits.length > 0 ? bubbleHits[0].object : null;

      bubbles.forEach((b, idx) => {
        const ud = b.userData;
        const bGeo = b.geometry as THREE.SphereGeometry;

        // Liquid distortion on hover (not size change!)
        if (hoveredBubble === b || ud.isDragging) {
          ud.distortTarget = 0.12;
        } else {
          ud.distortTarget = 0.02; // subtle idle wobble
        }
        ud.distortAmount += (ud.distortTarget - ud.distortAmount) * 0.08;
        applyLiquidDistort(bGeo, ud.originalPositions, ud.distortAmount, t, idx * 10);

        // Scale stays constant — no size change on hover
        b.scale.setScalar(ud.baseScale);

        // Floating & boundaries (skip if dragging)
        if (!ud.isDragging) {
          b.position.add(ud.velocity);
          if (b.position.x > 6 || b.position.x < -6) ud.velocity.x *= -1;
          if (b.position.y > 5 || b.position.y < 0) ud.velocity.y *= -1;
          if (b.position.z > 2 || b.position.z < -8) ud.velocity.z *= -1;
        }

        // Change cursor on hover
        if (hoveredBubble === b && !isMouseDown) {
          canvas.style.cursor = 'grab';
        }
      });

      if (!hoveredBubble && !isMouseDown) {
        canvas.style.cursor = 'default';
      }

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("burst-auth", onBurst);
      renderer.dispose();
      sphereGeo.dispose();
      sphereMat.dispose();
      rippleGeo.dispose();
      rippleMat.dispose();
      bubbleGeos.forEach(g => g.dispose());
    };
  }, []);

  return (
    <div className="three-canvas-wrap">
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
}
