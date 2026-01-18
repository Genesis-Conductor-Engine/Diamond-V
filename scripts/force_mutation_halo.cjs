// scripts/force_mutation_halo.cjs
// Builder Protocol: Inject a visual mutation into the Observatory
const fs = require('fs');
const path = require('path');

// --- CONFIGURATION ---
const MUTATION_DIR = path.join(__dirname, '../yennefer-observatory/src/components/mutations');
const TARGET_FILE = path.join(MUTATION_DIR, 'HaloMutation.jsx');

// --- THE MUTATION CODE (Simulated AI Output) ---
const AI_GENERATED_CODE = `import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

// A self-assembling mutation: A glowing energy halo around the core.
// It accepts 'coherence' as a prop, allowing its brightness to react to system state.
export default function HaloMutation({ coherence = 100 }) {
  const ref = useRef()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    // Slow, hypnotic rotation off-axis
    ref.current.rotation.x = t * 0.2
    ref.current.rotation.y = t * 0.1
    // "Breathing" scale effect
    const scale = 1.2 + Math.sin(t * 0.8) * 0.05
    ref.current.scale.set(scale, scale, scale)
  })

  // Calculate intensity based on passed coherence prop
  const intensity = (coherence || 100) / 50

  return (
    <mesh ref={ref}>
      {/* A large, thin ring */}
      <torusGeometry args={[4, 0.05, 16, 100]} />
      <meshStandardMaterial
        color="#33ff00"
        emissive="#33ff00"
        emissiveIntensity={intensity}
        transparent
        opacity={0.8}
      />
    </mesh>
  )
}
`;

// --- EXECUTION ---
console.log("🧬 BUILDER PROTOCOL INITIATED: Forcing Mutation 'Halo'...");

try {
    if (!fs.existsSync(MUTATION_DIR)){
        console.log(`Creating directory: ${MUTATION_DIR}`);
        fs.mkdirSync(MUTATION_DIR, { recursive: true });
    }

    fs.writeFileSync(TARGET_FILE, AI_GENERATED_CODE);

    console.log(`✅ MUTATION COMPLETE.`);
    console.log(`📂 Component injected: ${TARGET_FILE}`);
    console.log(`\n👀 The Observatory will hot-reload with the new Halo structure.`);

} catch (error) {
    console.error("❌ MUTATION FAILED:", error.message);
}
