// Fallback shader — used when main holo shader fails to compile
// Simple Fresnel glow, no scanlines or data bands

varying vec3 vNormal;
varying vec3 vPosition;
varying float vFresnel;

void main() {
  vec3 color = vec3(0.05, 0.55, 1.0);
  float glow = pow(vFresnel, 2.0);
  vec3 finalColor = color + glow * vec3(0.2, 0.67, 1.0);
  float alpha = 0.5 + glow * 0.4;
  gl_FragColor = vec4(finalColor, alpha);
}
