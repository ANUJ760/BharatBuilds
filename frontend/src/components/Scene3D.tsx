import { Canvas, useFrame } from '@react-three/fiber'
import { Float, MeshDistortMaterial, Environment, ContactShadows } from '@react-three/drei'
import { useRef } from 'react'
import * as THREE from 'three'

function AnimatedSphere({
  position,
  scale = 1,
  speed = 1,
  distort = 0.3,
  color = '#ffffff',
  scrollFactor = 0.001
}: {
  position: [number, number, number]
  scale?: number
  speed?: number
  distort?: number
  color?: string
  scrollFactor?: number
}) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame(() => {
    if (meshRef.current) {
      // Rotate based on scroll
      const scroll = window.scrollY
      meshRef.current.rotation.y = scroll * scrollFactor
      meshRef.current.position.y = position[1] + (scroll * scrollFactor * 0.5)
    }
  })

  return (
    <Float speed={speed} rotationIntensity={0.4} floatIntensity={1.5}>
      <mesh ref={meshRef} position={position} scale={scale}>
        <sphereGeometry args={[1, 64, 64]} />
        <MeshDistortMaterial
          color={color}
          roughness={0.08}
          metalness={0.1}
          distort={distort}
          speed={2}
        />
      </mesh>
    </Float>
  )
}

export function Scene3D(_props?: { scrollY?: any }) {
  return (
    <div className="absolute inset-0" style={{ pointerEvents: 'none' }}>
      <Canvas
        camera={{ position: [0, 0.5, 8], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.8} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <directionalLight position={[-3, 3, -3]} intensity={0.3} color="#e8e0ff" />

        {/* Main central sphere */}
        <AnimatedSphere position={[0, 0.3, 0]} scale={1.6} speed={1.2} distort={0.25} color="#f5f5f5" scrollFactor={0.002} />

        {/* Orbiting smaller spheres */}
        <AnimatedSphere position={[-2.8, 1, -2]} scale={0.65} speed={1.8} distort={0.35} color="#ffffff" scrollFactor={-0.003} />
        <AnimatedSphere position={[3, -0.3, -1.5]} scale={0.5} speed={2.2} distort={0.4} color="#f0f0f8" scrollFactor={0.004} />
        <AnimatedSphere position={[1.5, 1.8, -2.5]} scale={0.3} speed={2.5} distort={0.3} color="#fafafa" scrollFactor={-0.0015} />
        <AnimatedSphere position={[-1.5, -1, -0.8]} scale={0.4} speed={1.6} distort={0.35} color="#f8f8ff" scrollFactor={0.005} />

        <ContactShadows
          position={[0, -2.5, 0]}
          opacity={0.2}
          scale={12}
          blur={2.5}
          far={4}
        />

        <Environment preset="studio" />
      </Canvas>
    </div>
  )
}
