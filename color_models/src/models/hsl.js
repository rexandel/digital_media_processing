import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

function hslToRgb(h, s, l) {
  let r, g, b;
  if (s === 0) {
    r = g = b = l;
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };
    r = hue2rgb(p, q, h + 1 / 3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1 / 3);
  }
  return { r, g, b };
}

export default function buildHSLModel(content, geo, mat, sampleCount, spacing) {
  const count = sampleCount * sampleCount * sampleCount;
  const mesh = new THREE.InstancedMesh(geo, mat, count);
  mesh.instanceColor = new THREE.InstancedBufferAttribute(
    new Float32Array(count * 3),
    3
  );

  const dummy = new THREE.Object3D();
  let i = 0;
  for (let hI = 0; hI < sampleCount; hI++) {
    for (let sI = 0; sI < sampleCount; sI++) {
      for (let lI = 0; lI < sampleCount; lI++) {
        const h = hI * spacing;
        const s = sI * spacing;
        const l = lI * spacing;

        const angle = h * Math.PI * 2;
        const radius = s * 0.5;
        const x = 0.5 + Math.cos(angle) * radius;
        const y = 0.5 + Math.sin(angle) * radius;
        const z = l;

        var rgb = hslToRgb(h, s, l);
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

  // === HSL axes (same layout and padding as your HSV) ===
  const origin = new THREE.Vector3(0.5, 0.5, 0);
  const maxRadius = 0.5;

  // Hue circle
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

  // Saturation radial axis
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

  // Lightness vertical axis
  {
    const end = new THREE.Vector3(origin.x, origin.y, 1.05);
    const geom = new THREE.BufferGeometry().setFromPoints([origin, end]);
    const lLine = new THREE.Line(
      geom,
      new THREE.LineBasicMaterial({ color: 0x0000ff })
    );
    content.add(lLine);
    const lLabel = createLabel("L", "#0000ff");
    lLabel.position.copy(end).add(new THREE.Vector3(0, 0, 0.05));
    content.add(lLabel);
  }
}
