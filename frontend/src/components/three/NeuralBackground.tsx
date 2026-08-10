import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function Particles({ isSepia }: { isSepia: boolean }) {
  const pointsRef = useRef<THREE.Points>(null);
  const count = 600;

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 20;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 20;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    return arr;
  }, []);

  useFrame((state) => {
    if (!pointsRef.current) return;
    const t = state.clock.elapsedTime;
    pointsRef.current.rotation.y = t * 0.03;
    pointsRef.current.rotation.x = Math.sin(t * 0.05) * 0.1;
    const pos = pointsRef.current.geometry.attributes.position;
    for (let i = 0; i < count; i++) {
      const y = pos.array[i * 3 + 1];
      pos.array[i * 3 + 1] = y + Math.sin(t + i * 0.01) * 0.002;
    }
    pos.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.04}
        color={isSepia ? '#A39076' : '#FFD040'}
        transparent
        opacity={isSepia ? 0.18 : 0.28}
        sizeAttenuation
        blending={isSepia ? THREE.NormalBlending : THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

function NeuralLines({ isSepia }: { isSepia: boolean }) {
  const linesRef = useRef<THREE.Group>(null);
  const nodeCount = 12;
  const nodes = useMemo(
    () =>
      Array.from({ length: nodeCount }, () => ({
        x: (Math.random() - 0.5) * 14,
        y: (Math.random() - 0.5) * 14,
        z: (Math.random() - 0.5) * 6,
      })),
    [],
  );

  const lines = useMemo(() => {
    const result: [THREE.Vector3, THREE.Vector3][] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dist = Math.sqrt(
          (nodes[i].x - nodes[j].x) ** 2 +
            (nodes[i].y - nodes[j].y) ** 2 +
            (nodes[i].z - nodes[j].z) ** 2,
        );
        if (dist < 5) {
          result.push([
            new THREE.Vector3(nodes[i].x, nodes[i].y, nodes[i].z),
            new THREE.Vector3(nodes[j].x, nodes[j].y, nodes[j].z),
          ]);
        }
      }
    }
    return result;
  }, [nodes]);

  useFrame((state) => {
    if (linesRef.current) {
      linesRef.current.rotation.y = state.clock.elapsedTime * 0.02;
    }
  });

  const lineColor = isSepia ? '#C4B49E' : '#8B5CF6';

  return (
    <group ref={linesRef}>
      {lines.map((line, i) => {
        const geom = new THREE.BufferGeometry().setFromPoints(line);
        return (
          <primitive
            key={i}
            object={
              new THREE.LineSegments(
                geom,
                new THREE.LineBasicMaterial({
                  color: lineColor,
                  transparent: true,
                  opacity: isSepia ? 0.08 : 0.12,
                  blending: isSepia ? THREE.NormalBlending : THREE.AdditiveBlending,
                }),
              )
            }
          />
        );
      })}
      {nodes.map((node, i) => (
        <mesh key={i} position={[node.x, node.y, node.z]}>
          <sphereGeometry args={[0.05, 12, 12]} />
          <meshBasicMaterial
            color={lineColor}
            transparent
            opacity={isSepia ? 0.15 : 0.22}
          />
        </mesh>
      ))}
    </group>
  );
}

export default function NeuralBackground() {
  const [isSepia, setIsSepia] = useState(false);

  useEffect(() => {
    const checkTheme = () => {
      setIsSepia(document.body.classList.contains('sepia'));
    };
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="fixed inset-0 -z-10 pointer-events-none opacity-90">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <Particles isSepia={isSepia} />
        <NeuralLines isSepia={isSepia} />
      </Canvas>
    </div>
  );
}

