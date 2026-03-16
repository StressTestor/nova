uniform float uTime;
uniform vec3 uColor;
uniform float uPulseSpeed;

varying vec3 vPosition;

void main() {
  float pulse = 0.15 + 0.1 * sin(uTime * uPulseSpeed);
  gl_FragColor = vec4(uColor, pulse);
}
