import * as THREE from 'three';
import { COLORS } from '../constants.js';
import { addToScene, registerUpdate } from './scene.js';

import particleVert from '../shaders/particle.vert';
import particleFrag from '../shaders/particle.frag';

const PARTICLE_COUNT = 350;
let particleMaterial;

export function getParticleMaterial() {
  return particleMaterial;
}

export function createParticles() {
  const positions = new Float32Array(PARTICLE_COUNT * 3);
  const lifecycles = new Float32Array(PARTICLE_COUNT);
  const sizes = new Float32Array(PARTICLE_COUNT);

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const angle = Math.random() * Math.PI * 2;
    const radius = 0.8 + Math.random() * 1.2;
    positions[i * 3] = Math.cos(angle) * radius;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 3.0;
    positions[i * 3 + 2] = Math.sin(angle) * radius;

    lifecycles[i] = Math.random();
    sizes[i] = 1.0 + Math.random() * 3.0;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('aLifecycle', new THREE.BufferAttribute(lifecycles, 1));
  geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));

  particleMaterial = new THREE.ShaderMaterial({
    vertexShader: particleVert,
    fragmentShader: particleFrag,
    uniforms: {
      uTime: { value: 0.0 },
      uSpeed: { value: 1.0 },
      uColor: { value: new THREE.Color(...COLORS.primary.rgb) },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const points = new THREE.Points(geometry, particleMaterial);
  addToScene(points);

  registerUpdate((elapsed) => {
    particleMaterial.uniforms.uTime.value = elapsed;
  });

  return points;
}
