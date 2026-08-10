import { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useSpring, animated } from '@react-spring/web';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';

function GapOrb({ hovered }: { hovered: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const pCount = 60;
  const particlePositions = useRef(
    new Float32Array(pCount * 3),
  );

  for (let i = 0; i < pCount; i++) {
    const r = 1 + Math.random() * 0.5;
    const theta = Math.random() * Math.PI * 2;
    particlePositions.current[i * 3] = r * Math.cos(theta);
    particlePositions.current[i * 3 + 1] = (Math.random() - 0.5) * 2;
    particlePositions.current[i * 3 + 2] = r * Math.sin(theta);
  }

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (meshRef.current) {
      meshRef.current.rotation.y = t * 0.8;
      meshRef.current.rotation.x = t * 0.4;
      const s = hovered ? 1.15 + Math.sin(t * 4) * 0.05 : 1;
      meshRef.current.scale.set(s, s, s);
    }
    if (ringRef.current) {
      ringRef.current.rotation.z = t * 1.2;
      ringRef.current.rotation.x = t * 0.6;
    }
  });

  return (
    <>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[0.8, 1]} />
        <meshStandardMaterial
          color="#F97316"
          emissive="#F97316"
          emissiveIntensity={hovered ? 0.6 : 0.3}
          wireframe
          transparent
          opacity={0.9}
        />
      </mesh>
      <mesh ref={ringRef}>
        <torusGeometry args={[1.1, 0.03, 8, 64]} />
        <meshBasicMaterial
          color="#FFB020"
          transparent
          opacity={hovered ? 0.8 : 0.4}
        />
      </mesh>
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={pCount}
            array={particlePositions.current}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.06}
          color="#FFB020"
          transparent
          opacity={hovered ? 0.9 : 0.5}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </>
  );
}

export default function Sticky3DGapButton() {
  const [hovered, setHovered] = useState(false);
  const runGapAnalysis = useSyntapseStore((s) => s.runGapAnalysis);
  const isGapAnalyzing = useSyntapseStore((s) => s.isGapAnalyzing);
  const isDragging = useRef(false);

  const springs = useSpring({
    scale: hovered ? 1.08 : 1,
    config: { tension: 300, friction: 20 },
  });

  return (
    <motion.div
      drag
      dragMomentum={false}
      dragElastic={0.1}
      whileDrag={{ scale: 1.15, cursor: 'grabbing' }}
      onDragStart={() => {
        isDragging.current = true;
      }}
      onDragEnd={() => {
        setTimeout(() => {
          isDragging.current = false;
        }, 100);
      }}
      className="fixed top-1/2 right-6 -translate-y-1/2 z-50 group cursor-grab touch-none"
    >
      <animated.div
        style={springs}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onClick={() => {
          if (isDragging.current) return;
          runGapAnalysis();
        }}
      >
        <div className="relative">
          <div
            className={`absolute inset-0 rounded-full blur-xl transition-opacity duration-300 ${
              hovered ? 'opacity-60' : 'opacity-30'
            }`}
            style={{ backgroundColor: 'var(--accent-terracotta)' }}
          />
          <div 
            className="relative w-16 h-16 rounded-full shadow-xl flex items-center justify-center transition-all duration-300"
            style={{
              background: 'var(--surface-1)',
            }}
          >
            <Canvas
              camera={{ position: [0, 0, 4], fov: 50 }}
              gl={{ antialias: true, alpha: true }}
            >
              <ambientLight intensity={0.4} />
              <pointLight position={[3, 3, 3]} intensity={0.6} color="#FFB020" />
              <pointLight position={[-3, -3, 3]} intensity={0.4} color="#8B5CF6" />
              <GapOrb hovered={hovered} />
            </Canvas>
          </div>
          <div
            className={`absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-lg px-2.5 py-1 text-[11px] font-medium border shadow-lg transition-all duration-200 ${
              hovered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1'
            }`}
            style={{
              background: 'var(--surface-1)',
              borderColor: 'var(--surface-border)',
              color: 'var(--text-primary)',
            }}
          >
            <Zap className="inline w-3 h-3 mr-1 text-terracotta-c" />
            {isGapAnalyzing ? 'Analyzing…' : 'Gap Analysis'}
          </div>
        </div>
      </animated.div>
    </motion.div>
  );
}
