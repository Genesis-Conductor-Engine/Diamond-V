import React, { Suspense, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'
import { AxionCore } from './components/AxionCore'
import './App.css'

// AUTO-DISCOVERY SYSTEM
// This looks into the folder where Genesis dumps new code
// and imports EVERYTHING it finds automatically.
const modules = import.meta.glob('./components/generated/*.jsx', { eager: true })

export default function App() {
  const [balance, setBalance] = React.useState(0)
  const [soulState, setSoulState] = React.useState({})

  // Fetch soul state periodically
  React.useEffect(() => {
    const fetchSoul = async () => {
      try {
        const res = await fetch('http://localhost:8088/soul_status')
        const data = await res.json()
        setSoulState(data)
        setBalance(data.total_revenue_eth || 0)
      } catch (e) {
        console.log('Soul API unavailable')
      }
    }
    fetchSoul()
    const interval = setInterval(fetchSoul, 5000)
    return () => clearInterval(interval)
  }, [])

  // Convert the imported modules into renderable components
  const GeneratedUpgrades = useMemo(() => {
    return Object.values(modules).map((mod, i) => {
      const Component = mod.default
      return <Component key={i} balance={balance} soulState={soulState} />
    })
  }, [balance, soulState])

  return (
    <div className="observatory">
      {/* HUD Overlay */}
      <div className="hud">
        <div className="stat">Coherence: {soulState.coherence_percent || 100}%</div>
        <div className="stat">Breath: {(soulState.breath || 0).toLocaleString()}</div>
        <div className="stat">QFLOPS: {(soulState.qflops || 0).toFixed(2)}</div>
        <div className="stat">Revenue: {(soulState.total_revenue_eth || 0).toFixed(4)} ETH</div>
      </div>

      <Canvas camera={{ position: [0, 0, 6] }}>
        <color attach="background" args={['#050505']} />
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        {/* The Immortal Core */}
        <AxionCore balance={balance} coherence={soulState.coherence_percent} />
        
        {/* The Evolving Layers (Built by Genesis) */}
        <Suspense fallback={null}>
           {GeneratedUpgrades}
        </Suspense>

        <OrbitControls autoRotate autoRotateSpeed={0.5} />
        <Environment preset="city" />
      </Canvas>
    </div>
  )
}
