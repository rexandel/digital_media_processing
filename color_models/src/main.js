import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import setupScene from "./scene.js";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(
  70,
  window.innerWidth / window.innerHeight,
  0.01,
  10
);
camera.position.z = 2;

const scene = new THREE.Scene();

// Shared parameters for all models
const SAMPLE_COUNT = 32;
const SPACING = 1.0 / (SAMPLE_COUNT - 1);
const sphereGeometry = new THREE.SphereGeometry(0.02, 8, 8);
const sphereMaterial = new THREE.MeshBasicMaterial({ vertexColors: false });
const shared = [sphereGeometry, sphereMaterial, SAMPLE_COUNT, SPACING];

// read default from dropdown
const select = document.getElementById("colorModelSelect");
const loadModel = setupScene(renderer, scene, select.value, shared);

select.addEventListener("change", (e) => loadModel(e.target.value));

(function animate() {
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
})();
