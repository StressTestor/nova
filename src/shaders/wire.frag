uniform float uTime;
uniform vec3 uColor;
uniform float uPulseSpeed;

varying vec3 vPosition;
varying float vFresnel;

void main() {
  float pulse = 0.12 + 0.08 * sin(uTime * uPulseSpeed);

  // Fresnel-weighted wireframe: strong at edges, faded on face-on surfaces
  // This lets facial features show through the holographic shader
  // while edges get the wireframe overlay
  float fresnelWeight = smoothstep(0.2, 0.8, vFresnel);
  float alpha = pulse * (0.3 + fresnelWeight * 0.7);

  gl_FragColor = vec4(uColor, alpha);
}
