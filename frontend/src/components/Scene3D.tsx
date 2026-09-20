import { Canvas, useFrame } from '@react-three/fiber'
import { MeshDistortMaterial, Environment, ContactShadows } from '@react-three/drei'
import { useRef, useState, useEffect, useMemo } from 'react'
import * as THREE from 'three'

/**
 * Expanding ripple rings beneath the central sphere — like
 * a water droplet sitting on a still surface.
 */
function RippleFloor() {
  const rings = [0, 1, 2];
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (groupRef.current) {
      groupRef.current.children.forEach((child, i) => {
        const phase = (t * 0.4 + i / rings.length) % 1.0;
        child.scale.setScalar(1 + phase * 6);
        const mat = (child as THREE.Mesh).material as THREE.MeshBasicMaterial;
        mat.opacity = (1 - phase) * 0.12;
      });
    }
  });

  return (
    <group ref={groupRef} position={[0, -2.4, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      {rings.map((i) => (
        <mesh key={i}>
          <ringGeometry args={[0.95, 1.0, 64]} />
          <meshBasicMaterial color="#999999" transparent opacity={0.12} side={THREE.DoubleSide} />
        </mesh>
      ))}
    </group>
  );
}

/**
 * A single liquid sphere.
 *
 * Key design decisions for "liquid, not balloon":
 *  – Scale NEVER changes on hover. The sphere stays the same size.
 *  – Hover increases `distort` (surface deformation) and `speed`
 *    (how fast the deformation morphs), which looks like poking water.
 *  – A slow continuous rotation gives an organic, alive feeling
 *    even when idle.
 *  – `isMain` spheres additionally listen for the `burst-auth`
 *    transition event.
 */
function LiquidSphere({
  position,
  scale = 1,
  baseDistort = 0.35,
  color = '#e8e8e8',
  floatSpeed = 1,
  floatIntensity = 1.5,
  isMain = false,
}: {
  position: [number, number, number]
  scale?: number
  baseDistort?: number
  color?: string
  floatSpeed?: number
  floatIntensity?: number
  isMain?: boolean
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  const matRef  = useRef<any>(null)
  const [hovered, setHovered] = useState(false)
  const [shrinking, setShrinking] = useState(false)

  // Unique per-instance phase offset so spheres don't all bob in sync
  const phaseOffset = useMemo(() => Math.random() * Math.PI * 2, [])

  // Transition listener (only on main sphere)
  useEffect(() => {
    if (!isMain) return
    const handler = () => setShrinking(true)
    window.addEventListener('burst-auth', handler)
    return () => window.removeEventListener('burst-auth', handler)
  }, [isMain])

  useFrame(({ clock }, delta) => {
    if (!meshRef.current || !matRef.current) return
    const t = clock.elapsedTime

    // ── Continuous organic float (replaces Float helper for finer control) ──
    const floatY = Math.sin(t * floatSpeed + phaseOffset) * floatIntensity * 0.15
    const floatX = Math.cos(t * floatSpeed * 0.7 + phaseOffset) * floatIntensity * 0.06
    meshRef.current.position.x = position[0] + floatX
    meshRef.current.position.y = position[1] + floatY
    meshRef.current.position.z = position[2]

    // Slow continuous rotation — makes the surface distortion feel alive
    meshRef.current.rotation.x += delta * 0.15
    meshRef.current.rotation.y += delta * 0.2

    // ── Shrink for page-transition (droplet evaporates) ──
    if (shrinking) {
      meshRef.current.scale.lerp(new THREE.Vector3(0, 0, 0), 5 * delta)
    }
    // Scale stays constant — NO size change on hover

    // ── Liquid hover: only distort & speed change ──
    const targetDistort = hovered
      ? (isMain ? baseDistort * 3.5 : baseDistort * 2.8)   // big wobble
      : baseDistort                                         // idle wobble
    const targetSpeed = hovered ? 10 : 4

    matRef.current.distort = THREE.MathUtils.lerp(matRef.current.distort, targetDistort, 0.08)
    matRef.current.speed   = THREE.MathUtils.lerp(matRef.current.speed,   targetSpeed,   0.08)
  })

  return (
    <mesh
      ref={meshRef}
      position={position}
      scale={scale}
      onPointerOver={() => setHovered(true)}
      onPointerOut ={() => setHovered(false)}
    >
      <sphereGeometry args={[1, 128, 128]} />
      <MeshDistortMaterial
        ref={matRef}
        color={color}
        roughness={0.0}
        metalness={0.05}
        clearcoat={1}
        clearcoatRoughness={0.05}
        envMapIntensity={1.2}
        distort={baseDistort}
        speed={4}
      />
    </mesh>
  )
}

export function Scene3D(_props?: { scrollY?: any }) {
  return (
    <div className="absolute inset-0 z-0">
      <Canvas
        camera={{ position: [0, 0.5, 8], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={1.0} />
        <directionalLight position={[5, 5, 5]}   intensity={1.4} />
        <directionalLight position={[-4, 3, -3]}  intensity={0.6} color="#ffffff" />
        <directionalLight position={[0, -3, 5]}   intensity={0.3} color="#f0f0f0" />

        {/* Rippling water surface underneath */}
        <RippleFloor />

        {/* ─── Main central liquid blob ─── */}
        <LiquidSphere
          position={[0, 0.3, 0]}
          scale={1.6}
          baseDistort={0.4}
          color="#e8e8e8"
          floatSpeed={0.8}
          floatIntensity={2.0}
          isMain
        />

        {/* ─── Satellite liquid drops ─── */}
        <LiquidSphere position={[-2.8,  1.0, -2.0]} scale={0.6}  baseDistort={0.45} color="#dcdcdc" floatSpeed={1.2} floatIntensity={2.5} />
        <LiquidSphere position={[ 3.0, -0.3, -1.5]} scale={0.45} baseDistort={0.5}  color="#e0e0e0" floatSpeed={1.5} floatIntensity={2.0} />
        <LiquidSphere position={[ 1.5,  1.8, -2.5]} scale={0.3}  baseDistort={0.4}  color="#d8d8d8" floatSpeed={1.8} floatIntensity={3.0} />
        <LiquidSphere position={[-1.5, -1.0, -0.8]} scale={0.4}  baseDistort={0.45} color="#e5e5e5" floatSpeed={1.3} floatIntensity={2.2} />
        <LiquidSphere position={[-3.5, -2.0, -3.0]} scale={0.35} baseDistort={0.4}  color="#dadada" floatSpeed={1.6} floatIntensity={2.8} />
        <LiquidSphere position={[ 3.5,  2.0, -1.0]} scale={0.3}  baseDistort={0.5}  color="#e2e2e2" floatSpeed={1.1} floatIntensity={2.4} />

        <ContactShadows position={[0, -2.5, 0]} opacity={0.25} scale={15} blur={3.5} far={5} />

        <Environment preset="studio" />
      </Canvas>
    </div>
  )
}
