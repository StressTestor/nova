uniform vec3 uColor;

varying float vAlpha;

void main() {
  // Radial falloff for point sprite
  float dist = length(gl_PointCoord - vec2(0.5));
  if (dist > 0.5) discard;

  float falloff = 1.0 - dist * 2.0;
  falloff = pow(falloff, 2.0);

  gl_FragColor = vec4(uColor, vAlpha * falloff);
}
