import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

function hsvToRgb(h, s, v) {
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);

  switch (i % 6) {
    case 0:
      return { r: v, g: t, b: p };
    case 1:
      return { r: q, g: v, b: p };
    case 2:
      return { r: p, g: v, b: t };
    case 3:
      return { r: p, g: q, b: v };
    case 4:
      return { r: t, g: p, b: v };
    default:
      return { r: v, g: p, b: q };
  }
}

export default function buildHSVModel(
  content,
  sphereGeometry,
  sphereMaterial,
  sampleCount,
  spacing
) {
  const count = sampleCount * sampleCount * sampleCount;
  const mesh = new THREE.InstancedMesh(sphereGeometry, sphereMaterial, count);
  mesh.instanceColor = new THREE.InstancedBufferAttribute(
    new Float32Array(count * 3),
    3
  );

  const dummy = new THREE.Object3D();
  let i = 0;
  for (let hI = 0; hI < sampleCount; hI++) {
    for (let sI = 0; sI < sampleCount; sI++) {
      for (let vI = 0; vI < sampleCount; vI++) {
        const h = hI * spacing;
        const s = sI * spacing;
        const v = vI * spacing;

        const ang = h * Math.PI * 2;
        const r2 = s * 0.5;
        const x = 0.5 + Math.cos(ang) * r2;
        const y = 0.5 + Math.sin(ang) * r2;
        const z = v;

        var rgb = hsvToRgb(h, s, v);
        if (
          rgb.r < 0 ||
          rgb.r > 1 ||
          rgb.g < 0 ||
          rgb.g > 1 ||
          rgb.b < 0 ||
          rgb.b > 1
        )
          continue;
        rgb = linearToSrgb(rgb);
        dummy.position.set(x, y, z);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        mesh.instanceColor.setXYZ(i, rgb.r, rgb.g, rgb.b);
        i++;
      }
    }
  }
  content.add(mesh);

  // === HSV axes ===
  const origin = new THREE.Vector3(0.5, 0.5, 0);
  const maxRadius = 0.5;

  // Hue: circular line in X/Y plane
  {
    const segments = 64;
    const points = [];
    for (let j = 0; j <= segments; j++) {
      const a = (j / segments) * Math.PI * 2;
      const x = origin.x + Math.cos(a) * (maxRadius + 0.05);
      const y = origin.y + Math.sin(a) * (maxRadius + 0.05);
      points.push(new THREE.Vector3(x, y, origin.z));
    }
    const geom = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(
      geom,
      new THREE.LineBasicMaterial({ color: 0xff0000 })
    );
    content.add(line);
    const hLabel = createLabel("H", "#ff0000");
    hLabel.position.set(origin.x, origin.y - maxRadius - 0.05, origin.z);
    content.add(hLabel);
  }

  // Saturation: radial line from center
  {
    const end = new THREE.Vector3(
      origin.x + maxRadius + 0.05,
      origin.y,
      origin.z
    );
    const geom = new THREE.BufferGeometry().setFromPoints([origin, end]);
    const sLine = new THREE.Line(
      geom,
      new THREE.LineBasicMaterial({ color: 0x00ff00 })
    );
    content.add(sLine);
    const sLabel = createLabel("S", "#00ff00");
    sLabel.position.copy(end).add(new THREE.Vector3(0.05, 0, 0));
    content.add(sLabel);
  }

  // Value: vertical line
  {
    const end = new THREE.Vector3(origin.x, origin.y, 1.05);
    const geom = new THREE.BufferGeometry().setFromPoints([origin, end]);
    const vLine = new THREE.Line(
      geom,
      new THREE.LineBasicMaterial({ color: 0x0000ff })
    );
    content.add(vLine);
    const vLabel = createLabel("V", "#0000ff");
    vLabel.position.copy(end).add(new THREE.Vector3(0, 0, 0.05));
    content.add(vLabel);
  }
}
