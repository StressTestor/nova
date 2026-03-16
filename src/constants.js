// NOVA color palette — single source of truth
// Used by shaders (as uniforms), CSS (as custom properties), and JS
export const COLORS = {
  primary: { hex: '#0D8BFF', rgb: [13 / 255, 139 / 255, 255 / 255] },
  accent: { hex: '#33AAFF', rgb: [51 / 255, 170 / 255, 255 / 255] },
  dim: { hex: '#1A6AAA', rgb: [26 / 255, 106 / 255, 170 / 255] },
  bgStart: { hex: '#050A18' },
  bgEnd: { hex: '#000005' },
};

// Animation state names — shared between Rust events and JS
export const STATES = {
  MATERIALIZING: 'materializing',
  IDLE: 'idle',
  THINKING: 'thinking',
  SPEAKING: 'speaking',
  GLITCH: 'glitch',
  POWERING_DOWN: 'powering_down',
  SLEEPING: 'sleeping',
};

// Shader parameters per state
export const STATE_PARAMS = {
  [STATES.MATERIALIZING]: {
    opacity: 0.0,
    scanlineIntensity: 1.0,
    glitch: 0.3,
    particleSpeed: 3.0,
    wireframePulse: 2.0,
  },
  [STATES.IDLE]: {
    opacity: 0.75,
    scanlineIntensity: 0.5,
    glitch: 0.0,
    particleSpeed: 1.0,
    wireframePulse: 1.0,
  },
  [STATES.THINKING]: {
    opacity: 0.7,
    scanlineIntensity: 0.8,
    glitch: 0.0,
    particleSpeed: 2.0,
    wireframePulse: 2.0,
  },
  [STATES.SPEAKING]: {
    opacity: 0.9,
    scanlineIntensity: 0.2,
    glitch: 0.0,
    particleSpeed: 1.2,
    wireframePulse: 0.5,
  },
  [STATES.GLITCH]: {
    opacity: 0.6,
    scanlineIntensity: 1.0,
    glitch: 1.0,
    particleSpeed: 5.0,
    wireframePulse: 4.0,
  },
  [STATES.POWERING_DOWN]: {
    opacity: 0.0,
    scanlineIntensity: 1.5,
    glitch: 0.5,
    particleSpeed: 0.2,
    wireframePulse: 0.3,
  },
};
