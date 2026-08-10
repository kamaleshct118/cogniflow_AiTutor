import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function MorphingCore() {
  const meshRef = useRef<THREE.Mesh>(null);
  const particlesRef = useRef<THREE.Points>(null);
  const pCount = 200;

  const particlePositions = useMemo(() => {
    const arr = new Float32Array(pCount * 3);
    for (let i = 0; i < pCount; i++) {
      const r = 1.5 + Math.random() * 1;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, []);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (meshRef.current) {
      meshRef.current.rotation.x = t * 0.5;
      meshRef.current.rotation.y = t * 0.7;
      const scale = 1 + Math.sin(t * 2) * 0.08;
      meshRef.current.scale.set(scale, scale, scale);
    }
    if (particlesRef.current) {
      particlesRef.current.rotation.y = -t * 0.3;
      particlesRef.current.rotation.z = t * 0.2;
      const pos = particlesRef.current.geometry.attributes.position;
      for (let i = 0; i < pCount; i++) {
        const baseR = 1.5 + Math.sin(t * 1.5 + i * 0.1) * 0.3;
        const idx = i * 3;
        const len = Math.sqrt(pos.array[idx] ** 2 + pos.array[idx + 1] ** 2 + pos.array[idx + 2] ** 2);
        const factor = baseR / len;
        pos.array[idx] *= factor;
        pos.array[idx + 1] *= factor;
        pos.array[idx + 2] *= factor;
      }
      pos.needsUpdate = true;
    }
  });

  return (
    <>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[1, 2]} />
        <meshStandardMaterial
          color="#FFB020"
          emissive="#F97316"
          emissiveIntensity={0.4}
          wireframe
          transparent
          opacity={0.8}
        />
      </mesh>
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={pCount}
            array={particlePositions}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.05}
          color="#8B5CF6"
          transparent
          opacity={0.7}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </>
  );
}

interface MesmerizingLoaderProps {
  size?: number;
}

export default function MesmerizingLoader({ size = 120 }: MesmerizingLoaderProps) {
  return (
    <div style={{ width: size, height: size }} className="pointer-events-none">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[5, 5, 5]} intensity={0.8} color="#FFB020" />
        <pointLight position={[-5, -5, 5]} intensity={0.5} color="#8B5CF6" />
        <MorphingCore />
      </Canvas>
    </div>
  );
}
