import * as THREE from 'three';

let renderer, scene, camera;
let animationFrameId = null;
let updateCallbacks = [];

export function initScene(canvas) {
  renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
  });
  renderer.setClearColor(0x000000, 0);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(
    35,
    window.innerWidth / window.innerHeight,
    0.1,
    100
  );
  camera.position.set(0, 0.2, 4.2);
  camera.lookAt(0, 0, 0);

  const ambient = new THREE.AmbientLight(0x0D8BFF, 0.3);
  scene.add(ambient);

  window.addEventListener('resize', onResize);
  document.addEventListener('visibilitychange', onVisibilityChange);

  return { renderer, scene, camera };
}

export function addToScene(object) {
  scene.add(object);
}

export function registerUpdate(callback) {
  updateCallbacks.push(callback);
}

export function startRenderLoop() {
  const clock = new THREE.Clock();

  function animate() {
    animationFrameId = requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();
    const delta = clock.getDelta();

    for (const cb of updateCallbacks) {
      cb(elapsed, delta);
    }

    renderer.render(scene, camera);
  }

  animate();
}

export function stopRenderLoop() {
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }
}

export function getCamera() {
  return camera;
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function onVisibilityChange() {
  if (document.hidden) {
    stopRenderLoop();
  } else {
    startRenderLoop();
  }
}

export function dispose() {
  stopRenderLoop();
  window.removeEventListener('resize', onResize);
  document.removeEventListener('visibilitychange', onVisibilityChange);
  renderer.dispose();
}
