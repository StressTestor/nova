// NOVA — Neural Operative Virtual Assistant
// Entry point — will initialize Three.js renderer and Tauri bridge

console.log('NOVA initializing...');

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('renderer');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  console.log('NOVA ready — renderer placeholder');
});
