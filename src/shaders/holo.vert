uniform float uTime;
uniform float uGlitch;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying float vFresnel;

void main() {
  vec3 pos = position;

  // Subtle holographic wobble
  float wobble = sin(pos.y * 3.0 + uTime * 1.5) * 0.003;
  wobble += sin(pos.x * 5.0 + uTime * 2.0) * 0.002;
  pos += normal * wobble;

  // Glitch displacement — horizontal tear
  if (uGlitch > 0.0) {
    float glitchLine = step(0.98, fract(pos.y * 20.0 + uTime * 50.0));
    pos.x += glitchLine * uGlitch * 0.15 * sign(sin(uTime * 100.0));
    float vertJitter = step(0.95, fract(sin(uTime * 200.0) * 43758.5453));
    pos.y += vertJitter * uGlitch * 0.05;
  }

  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mvPosition;

  vNormal = normalize(normalMatrix * normal);
  vPosition = pos;
  vUv = uv;

  // Fresnel calculation
  vec3 viewDir = normalize(-mvPosition.xyz);
  vFresnel = 1.0 - abs(dot(viewDir, vNormal));
}
