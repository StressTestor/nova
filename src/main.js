import { initScene, startRenderLoop } from './renderer/scene.js';
import { loadHead } from './renderer/head.js';
import { createParticles } from './renderer/particles.js';
import { createAmbientElements } from './renderer/ambient.js';
import { initAnimation } from './renderer/animation.js';
import { initTracking } from './renderer/tracking.js';

async function init() {
  console.log('NOVA initializing...');

  const canvas = document.getElementById('renderer');
  initScene(canvas);
  await loadHead();
  createParticles();
  createAmbientElements();
  initAnimation();
  initTracking();
  startRenderLoop();

  console.log('NOVA online.');
}

document.addEventListener('DOMContentLoaded', init);
