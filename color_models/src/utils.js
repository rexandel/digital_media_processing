import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";

export function createAxis(dir, color) {
  const geometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    dir.clone(),
  ]);
  return new THREE.Line(geometry, new THREE.LineBasicMaterial({ color }));
}

export function createPivotGroup() {
  const pivot = new THREE.Group();
  const content = new THREE.Group();
  content.position.set(-0.5, -0.5, -0.5);
  pivot.add(content);
  return { pivot, contentGroup: content };
}

export function createLabel(text, color) {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  canvas.width = canvas.height = 64;

  ctx.fillStyle = color;
  ctx.font = "bold 32px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 32, 32);

  const texture = new THREE.CanvasTexture(canvas);
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: texture, transparent: true })
  );
  sprite.scale.set(0.2, 0.2, 0.2);
  return sprite;
}

export function linearToSrgb(rgb) {
  const convert = (v) =>
    v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);

  return {
    r: convert(rgb.r),
    g: convert(rgb.g),
    b: convert(rgb.b),
  };
}
