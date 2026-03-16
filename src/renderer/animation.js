import { STATES, STATE_PARAMS } from '../constants.js';
import { getHoloMaterial, getWireMaterial } from './head.js';
import { getParticleMaterial } from './particles.js';
import { registerUpdate } from './scene.js';

let currentState = STATES.MATERIALIZING;
let currentParams = { ...STATE_PARAMS[STATES.MATERIALIZING] };
let targetParams = { ...STATE_PARAMS[STATES.MATERIALIZING] };
let materializeProgress = 0;

const LERP_SPEED = 3.0;

export function getCurrentState() {
  return currentState;
}

export function setState(newState) {
  if (newState === currentState) return;
  console.log('NOVA state: ' + currentState + ' -> ' + newState);
  currentState = newState;

  if (STATE_PARAMS[newState]) {
    targetParams = { ...STATE_PARAMS[newState] };
  }

  if (newState === STATES.MATERIALIZING) {
    materializeProgress = 0;
  }
}

export function initAnimation() {
  setState(STATES.MATERIALIZING);

  registerUpdate((elapsed, delta) => {
    // Lerp current params toward target
    for (const key of Object.keys(targetParams)) {
      const diff = targetParams[key] - currentParams[key];
      currentParams[key] += diff * LERP_SPEED * delta;
    }

    // Materialization: animate opacity from 0 to idle over 2 seconds
    if (currentState === STATES.MATERIALIZING) {
      materializeProgress += delta / 2.0;
      if (materializeProgress >= 1.0) {
        setState(STATES.IDLE);
      } else {
        currentParams.opacity = materializeProgress * STATE_PARAMS[STATES.IDLE].opacity;
        currentParams.glitch = (1.0 - materializeProgress) * 0.3;
      }
    }

    applyToShaders();
  });
}

function applyToShaders() {
  const holo = getHoloMaterial();
  if (holo && holo.uniforms) {
    holo.uniforms.uOpacity.value = currentParams.opacity;
    holo.uniforms.uScanlineIntensity.value = currentParams.scanlineIntensity;
    holo.uniforms.uGlitch.value = currentParams.glitch;
  }

  const wire = getWireMaterial();
  if (wire && wire.uniforms) {
    wire.uniforms.uPulseSpeed.value = currentParams.wireframePulse;
  }

  const particle = getParticleMaterial();
  if (particle && particle.uniforms) {
    particle.uniforms.uSpeed.value = currentParams.particleSpeed;
  }
}

export function triggerGlitch(durationMs) {
  durationMs = durationMs || 800;
  const prevState = currentState;
  setState(STATES.GLITCH);
  setTimeout(function() {
    if (currentState === STATES.GLITCH) {
      setState(prevState === STATES.GLITCH ? STATES.IDLE : prevState);
    }
  }, durationMs);
}
