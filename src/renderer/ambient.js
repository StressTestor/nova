import * as THREE from 'three';
import { COLORS } from '../constants.js';
import { addToScene, registerUpdate } from './scene.js';

export function createAmbientElements() {
  const group = new THREE.Group();

  // Orbital ring 1
  const ring1Geo = new THREE.TorusGeometry(1.8, 0.01, 8, 64);
  const ring1Mat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(...COLORS.primary.rgb),
    transparent: true,
    opacity: 0.3,
    blending: THREE.AdditiveBlending,
  });
  const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
  ring1.rotation.x = Math.PI / 2;
  ring1.position.y = -1.5;
  group.add(ring1);

  // Orbital ring 2 (different size, tilted)
  const ring2Geo = new THREE.TorusGeometry(2.1, 0.008, 8, 64);
  const ring2Mat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(...COLORS.accent.rgb),
    transparent: true,
    opacity: 0.2,
    blending: THREE.AdditiveBlending,
  });
  const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
  ring2.rotation.x = Math.PI / 2;
  ring2.rotation.z = 0.1;
  ring2.position.y = -1.5;
  group.add(ring2);

  // Radial glow disc (projection platform)
  const discGeo = new THREE.CircleGeometry(2.0, 32);
  const discMat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(...COLORS.primary.rgb),
    transparent: true,
    opacity: 0.08,
    blending: THREE.AdditiveBlending,
    side: THREE.DoubleSide,
  });
  const disc = new THREE.Mesh(discGeo, discMat);
  disc.rotation.x = -Math.PI / 2;
  disc.position.y = -1.55;
  group.add(disc);

  addToScene(group);

  registerUpdate((elapsed) => {
    ring1.rotation.z = elapsed * 0.3;
    ring2.rotation.z = -elapsed * 0.2 + 0.1;
    discMat.opacity = 0.06 + 0.03 * Math.sin(elapsed * 2.0);
  });

  return group;
}
