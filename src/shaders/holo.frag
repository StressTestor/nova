uniform float uTime;
uniform float uOpacity;
uniform float uScanlineIntensity;
uniform float uGlitch;
uniform vec3 uColor;
uniform vec3 uAccentColor;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying float vFresnel;

float random(vec2 st) {
  return fract(sin(dot(st, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
  // Base color with Fresnel edge glow
  float fresnelGlow = pow(vFresnel, 2.5) * 1.5;
  vec3 color = mix(uColor, uAccentColor, fresnelGlow);

  // Scanlines — horizontal lines scrolling vertically
  float scanline = sin(vPosition.y * 120.0 - uTime * 2.0) * 0.5 + 0.5;
  scanline = pow(scanline, 8.0) * uScanlineIntensity * 0.3;

  // Data band sweeps — bright horizontal bands
  float dataBand = smoothstep(0.98, 1.0,
    sin(vPosition.y * 2.0 - uTime * 3.0 + sin(uTime * 0.5) * 5.0));
  dataBand *= 0.6;

  // Horizontal interference lines
  float interference = step(0.995, sin(vPosition.y * 80.0 + uTime * 15.0));
  interference *= 0.2;

  // Flickering
  float flicker = 0.95 + 0.05 * sin(uTime * 30.0) * sin(uTime * 7.0);

  // Glitch color shift
  vec3 glitchColor = color;
  if (uGlitch > 0.0) {
    float shift = random(vec2(floor(uTime * 20.0), floor(vPosition.y * 10.0)));
    if (shift > 0.8) {
      glitchColor = vec3(1.0, 0.3, 0.3);
    }
  }

  // Combine
  vec3 finalColor = glitchColor;
  finalColor += fresnelGlow * uAccentColor * 0.5;
  finalColor += scanline * uAccentColor;
  finalColor += dataBand * vec3(1.0);
  finalColor += interference * vec3(1.0);
  finalColor *= flicker;

  // Opacity: base + Fresnel boost
  // Higher base fill (0.55) gives the face more solid presence
  // Fresnel still brightens edges for the holographic rim glow
  float alpha = uOpacity * (0.55 + fresnelGlow * 0.45);
  alpha += scanline * 0.1;
  alpha += dataBand * 0.3;

  gl_FragColor = vec4(finalColor, alpha);
}
