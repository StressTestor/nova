uniform float uTime;

varying vec3 vPosition;
varying float vFresnel;

void main() {
  vPosition = position;
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  gl_Position = projectionMatrix * mvPosition;

  // Fresnel for edge-weighted wireframe
  vec3 viewDir = normalize(-mvPosition.xyz);
  vec3 norm = normalize(normalMatrix * normal);
  vFresnel = 1.0 - abs(dot(viewDir, norm));
}
