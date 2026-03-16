import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { COLORS } from '../constants.js';
import { addToScene, registerUpdate } from './scene.js';

import holoVert from '../shaders/holo.vert';
import holoFrag from '../shaders/holo.frag';
import fallbackFrag from '../shaders/fallback.frag';
import wireVert from '../shaders/wire.vert';
import wireFrag from '../shaders/wire.frag';

let headGroup;
let holoMaterial, wireMaterial;

let targetRotationY = 0;
let targetRotationX = 0;
let currentRotationY = 0;
let currentRotationX = 0;

export function setTargetRotation(x, y) {
  targetRotationX = x;
  targetRotationY = y;
}

export function getHoloMaterial() {
  return holoMaterial;
}

export function getWireMaterial() {
  return wireMaterial;
}

export async function loadHead() {
  headGroup = new THREE.Group();
  const loader = new GLTFLoader();

  try {
    const gltf = await loader.loadAsync('/src/assets/models/holo_head.glb');
    const model = gltf.scene.children[0];

    if (!model || !model.geometry) {
      console.error('NOVA: Invalid model, using fallback sphere');
      createFallbackHead();
    } else {
      const geometry = model.geometry;
      holoMaterial = createHoloMaterial();
      const headMesh = new THREE.Mesh(geometry, holoMaterial);
      headGroup.add(headMesh);

      wireMaterial = createWireMaterial();
      const wireMesh = new THREE.Mesh(geometry.clone(), wireMaterial);
      wireMesh.scale.set(1.003, 1.003, 1.003);
      headGroup.add(wireMesh);
    }
  } catch (err) {
    console.error('NOVA: Failed to load head model:', err);
    createFallbackHead();
  }

  addToScene(headGroup);

  registerUpdate((elapsed) => {
    if (!headGroup) return;

    // Lerp rotation toward target (mouse tracking)
    currentRotationY += (targetRotationY - currentRotationY) * 0.05;
    currentRotationX += (targetRotationX - currentRotationX) * 0.05;
    headGroup.rotation.y = currentRotationY;
    headGroup.rotation.x = currentRotationX;

    // Idle bob
    headGroup.position.y = Math.sin(elapsed * 0.8 * Math.PI * 2) * 0.03;

    // Update shader time uniforms
    if (holoMaterial) holoMaterial.uniforms.uTime.value = elapsed;
    if (wireMaterial) wireMaterial.uniforms.uTime.value = elapsed;
  });

  return headGroup;
}

function createHoloMaterial() {
  try {
    return new THREE.ShaderMaterial({
      vertexShader: holoVert,
      fragmentShader: holoFrag,
      uniforms: {
        uTime: { value: 0.0 },
        uOpacity: { value: 0.75 },
        uScanlineIntensity: { value: 0.5 },
        uGlitch: { value: 0.0 },
        uColor: { value: new THREE.Color(...COLORS.primary.rgb) },
        uAccentColor: { value: new THREE.Color(...COLORS.accent.rgb) },
      },
      transparent: true,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
  } catch (err) {
    console.warn('NOVA: Main shader failed, using fallback:', err);
    return createFallbackMaterial();
  }
}

function createFallbackMaterial() {
  return new THREE.ShaderMaterial({
    vertexShader: holoVert,
    fragmentShader: fallbackFrag,
    uniforms: {
      uTime: { value: 0.0 },
      uGlitch: { value: 0.0 },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
}

function createWireMaterial() {
  return new THREE.ShaderMaterial({
    vertexShader: wireVert,
    fragmentShader: wireFrag,
    uniforms: {
      uTime: { value: 0.0 },
      uColor: { value: new THREE.Color(...COLORS.primary.rgb) },
      uPulseSpeed: { value: 1.0 },
    },
    wireframe: true,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
}

function createFallbackHead() {
  const geo = new THREE.SphereGeometry(1, 32, 24);
  holoMaterial = createFallbackMaterial();
  headGroup.add(new THREE.Mesh(geo, holoMaterial));

  wireMaterial = createWireMaterial();
  const wireMesh = new THREE.Mesh(geo.clone(), wireMaterial);
  wireMesh.scale.set(1.003, 1.003, 1.003);
  headGroup.add(wireMesh);
}
