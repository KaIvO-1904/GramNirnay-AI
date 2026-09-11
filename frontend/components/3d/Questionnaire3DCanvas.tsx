'use client';
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface Questionnaire3DCanvasProps {
  stepIndex?: number;
  category?: string;
  className?: string;
}

const THEME_COLORS: Record<string, { primary: number; emissive: number; accent: number }> = {
  poultry: { primary: 0x3b82f6, emissive: 0x1d4ed8, accent: 0x60a5fa },
  cloth: { primary: 0x10b981, emissive: 0x047857, accent: 0x34d399 },
  dairy: { primary: 0xf59e0b, emissive: 0xb45309, accent: 0xfbbf24 },
  kirana: { primary: 0x06b6d4, emissive: 0x0e7490, accent: 0x22d3ee },
  agro_inputs: { primary: 0x6366f1, emissive: 0x4338ca, accent: 0x818cf8 },
  goat: { primary: 0xa855f7, emissive: 0x7e22ce, accent: 0xc084fc },
  general: { primary: 0x3b82f6, emissive: 0x1e40af, accent: 0x93c5fd },
};

export default function Questionnaire3DCanvas({
  stepIndex = 0,
  category = 'general',
  className = '',
}: Questionnaire3DCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth || 140;
    const height = container.clientHeight || 140;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.z = 9;

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    const theme = THEME_COLORS[category] || THEME_COLORS.general;

    // 1. Central Core Geometry (Dodecahedron with wireframe lattice)
    const coreGeo = new THREE.DodecahedronGeometry(1.9, 0);
    const coreMat = new THREE.MeshStandardMaterial({
      color: theme.primary,
      emissive: theme.emissive,
      emissiveIntensity: 0.5,
      roughness: 0.2,
      metalness: 0.8,
      wireframe: true,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    group.add(coreMesh);

    // Inner Glowing Core
    const innerGeo = new THREE.IcosahedronGeometry(1.2, 1);
    const innerMat = new THREE.MeshStandardMaterial({
      color: theme.accent,
      emissive: theme.primary,
      emissiveIntensity: 0.6,
      roughness: 0.4,
      metalness: 0.2,
      transparent: true,
      opacity: 0.85,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    group.add(innerMesh);

    // 2. Torus Orbital Ring
    const ringGeo = new THREE.TorusGeometry(2.8, 0.035, 16, 64);
    const ringMat = new THREE.MeshStandardMaterial({
      color: theme.accent,
      emissive: theme.primary,
      emissiveIntensity: 0.4,
      roughness: 0.1,
      metalness: 0.9,
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 3;
    group.add(ringMesh);

    // 3. Floating Micro-Nodes
    const nodeCount = 8;
    const nodeGeo = new THREE.OctahedronGeometry(0.2, 0);
    const nodeMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: theme.accent,
      emissiveIntensity: 0.9,
      roughness: 0.1,
      metalness: 0.9,
    });
    const nodes: THREE.Mesh[] = [];

    for (let i = 0; i < nodeCount; i++) {
      const node = new THREE.Mesh(nodeGeo, nodeMat);
      const angle = (i / nodeCount) * Math.PI * 2;
      node.position.set(Math.cos(angle) * 2.8, Math.sin(angle) * 0.8, Math.sin(angle) * 2.2);
      group.add(node);
      nodes.push(node);
    }

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(theme.accent, 2.5, 20);
    pointLight.position.set(4, 4, 6);
    scene.add(pointLight);

    // Mouse Parallax
    let mouseX = 0;
    let mouseY = 0;
    const onMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / width - 0.5) * 2;
      mouseY = ((e.clientY - rect.top) / height - 0.5) * 2;
    };
    window.addEventListener('mousemove', onMouseMove);

    // Animation Loop
    let reqId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      reqId = requestAnimationFrame(animate);
      const time = clock.getElapsedTime();

      coreMesh.rotation.x = time * 0.35;
      coreMesh.rotation.y = time * 0.45;

      innerMesh.rotation.x = -time * 0.25;
      innerMesh.rotation.y = -time * 0.3;

      ringMesh.rotation.z = time * 0.4;
      ringMesh.rotation.x = Math.PI / 3 + Math.sin(time * 0.5) * 0.15;

      // Pulse nodes
      nodes.forEach((node, idx) => {
        const angle = (idx / nodeCount) * Math.PI * 2 + time * 0.4;
        node.position.x = Math.cos(angle) * 2.8;
        node.position.z = Math.sin(angle) * 2.8;
        node.position.y = Math.sin(time * 1.5 + idx) * 0.4;
        node.rotation.x = time * 2;
      });

      // Smooth mouse follow
      group.rotation.y += (mouseX * 0.4 - group.rotation.y) * 0.05;
      group.rotation.x += (-mouseY * 0.4 - group.rotation.x) * 0.05;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth || 140;
      const h = container.clientHeight || 140;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(reqId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [category]);

  return (
    <div
      ref={containerRef}
      className={`relative flex items-center justify-center pointer-events-auto ${className}`}
      style={{ width: '120px', height: '120px' }}
    />
  );
}
