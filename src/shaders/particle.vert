uniform float uTime;
uniform float uSpeed;

attribute float aLifecycle;
attribute float aSize;

varying float vAlpha;

void main() {
  vec3 pos = position;

  // Rising motion
  float life = fract(aLifecycle + uTime * 0.1 * uSpeed);
  pos.y += life * 3.0;

  // Sine drift
  pos.x += sin(life * 6.28 + position.x * 10.0) * 0.15;
  pos.z += cos(life * 6.28 + position.z * 10.0) * 0.1;

  // Fade in and out
  vAlpha = sin(life * 3.14159) * 0.6;

  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  gl_PointSize = aSize * (200.0 / -mvPosition.z);
  gl_Position = projectionMatrix * mvPosition;
}
