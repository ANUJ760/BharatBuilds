import { Canvas, useFrame } from '@react-three/fiber'
import { Float, MeshDistortMaterial, Environment, ContactShadows } from '@react-three/drei'
import { useRef, useState, useEffect } from 'react'
import * as THREE from 'three'

function AnimatedSphere({
  position,
  scale = 1,
  speed = 1,
  distort = 0.3,
  color = '#ffffff',
  scrollFactor = 0.001,
  isMain = false
}: {
  position: [number, number, number]
  scale?: number
  speed?: number
  distort?: number
  color?: string
  scrollFactor?: number
  isMain?: boolean
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  const materialRef = useRef<any>(null)
  const [hovered, setHovered] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)

  useEffect(() => {
    if (isMain) {
      const handleBurst = () => {
        setIsTransitioning(true)
      }
      window.addEventListener('burst-auth', handleBurst)
      return () => window.removeEventListener('burst-auth', handleBurst)
    }
  }, [isMain])

  useFrame((_state, delta) => {
    if (meshRef.current) {
      // Rotate and float based on scroll
      const scroll = window.scrollY
      meshRef.current.rotation.y = scroll * scrollFactor
      meshRef.current.position.y = position[1] + (scroll * scrollFactor * 0.5)

      // Shrink effect for transition
      if (isTransitioning) {
        meshRef.current.scale.lerp(new THREE.Vector3(0, 0, 0), 6 * delta)
      } else {
        meshRef.current.scale.lerp(new THREE.Vector3(scale, scale, scale), 5 * delta)
      }
    }

    // Liquid hover effect
    if (materialRef.current) {
      const targetDistort = hovered ? distort * 3.0 : distort * 1.5
      const targetSpeed = hovered ? 8 : 3
      
      materialRef.current.distort = THREE.MathUtils.lerp(
        materialRef.current.distort,
        targetDistort,
        0.1
      )
      materialRef.current.speed = THREE.MathUtils.lerp(
        materialRef.current.speed,
        targetSpeed,
        0.1
      )
    }
  })

  return (
    <Float speed={speed * 1.5} rotationIntensity={1.2} floatIntensity={isTransitioning ? 0 : 3.5}>
      <mesh 
        ref={meshRef} 
        position={position} 
        scale={scale}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[1, 64, 64]} />
        <MeshDistortMaterial
          ref={materialRef}
          color={color}
          roughness={0.05}
          metalness={0.15}
          distort={distort * 1.5}
          speed={3}
        />
      </mesh>
    </Float>
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
        <ambientLight intensity={0.9} />
        <directionalLight position={[5, 5, 5]} intensity={1.2} />
        <directionalLight position={[-3, 3, -3]} intensity={0.5} color="#ffffff" />

        {/* Main central sphere */}
        <AnimatedSphere position={[0, 0.3, 0]} scale={1.6} speed={1.5} distort={0.3} color="#ffffff" scrollFactor={0.003} isMain={true} />

        {/* Orbiting smaller spheres */}
        <AnimatedSphere position={[-2.8, 1, -2]} scale={0.65} speed={2.0} distort={0.4} color="#f5f5f5" scrollFactor={-0.004} />
        <AnimatedSphere position={[3, -0.3, -1.5]} scale={0.5} speed={2.5} distort={0.45} color="#fafafa" scrollFactor={0.005} />
        <AnimatedSphere position={[1.5, 1.8, -2.5]} scale={0.3} speed={2.8} distort={0.35} color="#f0f0f0" scrollFactor={-0.002} />
        <AnimatedSphere position={[-1.5, -1, -0.8]} scale={0.4} speed={1.8} distort={0.4} color="#f8f8f8" scrollFactor={0.006} />
        
        {/* Extra orbiting spheres for more dynamics */}
        <AnimatedSphere position={[-3.5, -2, -3]} scale={0.45} speed={2.2} distort={0.3} color="#ffffff" scrollFactor={0.004} />
        <AnimatedSphere position={[3.5, 2, -1]} scale={0.35} speed={1.9} distort={0.5} color="#f5f5f5" scrollFactor={-0.005} />

        <ContactShadows
          position={[0, -2.5, 0]}
          opacity={0.3}
          scale={15}
          blur={3}
          far={5}
        />

        <Environment preset="studio" />
      </Canvas>
    </div>
  )
}
