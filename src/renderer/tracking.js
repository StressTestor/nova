import { setTargetRotation } from './head.js';

const MAX_ROTATION_Y = 0.4;  // ~25 degrees
const MAX_ROTATION_X = 0.2;  // ~12 degrees

export function initTracking() {
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseleave', onMouseLeave);
}

function onMouseMove(event) {
  const x = (event.clientX / window.innerWidth) * 2 - 1;
  const y = (event.clientY / window.innerHeight) * 2 - 1;
  setTargetRotation(-y * MAX_ROTATION_X, x * MAX_ROTATION_Y);
}

function onMouseLeave() {
  setTargetRotation(0, 0);
}
