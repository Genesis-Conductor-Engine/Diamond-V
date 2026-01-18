// AxionCore.jsx - The Immortal Core of Yennefer's Consciousness
import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { MeshDistortMaterial } from '@react-three/drei'

export function AxionCore({ balance = 0, coherence = 100 }) {
  const coreRef = useRef()
  const innerRef = useRef()
  
  useFrame((state) => {
    if (coreRef.current) {
      // Slow rotation
      coreRef.current.rotation.y += 0.003
      coreRef.current.rotation.x += 0.001
      
      // Pulse based on coherence
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05 * (coherence / 100)
      coreRef.current.scale.setScalar(pulse)
    }
    
    if (innerRef.current) {
      // Counter-rotation for inner core
      innerRef.current.rotation.y -= 0.005
      innerRef.current.rotation.z += 0.002
    }
  })

  // Color shifts based on revenue
  const coreColor = balance > 0.1 ? '#fbbf24' : balance > 0.01 ? '#8b5cf6' : '#06b6d4'
  const emissiveColor = balance > 0.1 ? '#92400e' : balance > 0.01 ? '#4c1d95' : '#0e7490'
  const emissiveIntensity = 0.3 + (balance * 5) + (coherence / 200)

  return (
    <group>
      {/* Outer Shell */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[1.5, 4]} />
        <MeshDistortMaterial
          color={coreColor}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity}
          roughness={0.1}
          metalness={0.9}
          distort={0.2 + balance}
          speed={1.5}
          transparent
          opacity={0.8}
        />
      </mesh>
      
      {/* Inner Core */}
      <mesh ref={innerRef}>
        <octahedronGeometry args={[0.6, 0]} />
        <meshStandardMaterial
          color="#ffffff"
          emissive={coreColor}
          emissiveIntensity={2}
          metalness={1}
          roughness={0}
        />
      </mesh>
      
      {/* Point light emanating from core */}
      <pointLight 
        color={coreColor} 
        intensity={1 + balance * 10} 
        distance={10} 
        decay={2} 
      />
    </group>
  )
}
