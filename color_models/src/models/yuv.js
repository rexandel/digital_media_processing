import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

function yuvToRgb(y, u, v) {
  const r = y + 1.402 * v;
  const g = y - 0.344136 * u - 0.714136 * v;
  const b = y + 1.772 * u;
  return { r, g, b };
}

export default function buildYUVModel(content, geo, mat, sampleCount, spacing) {
  const matrices = [];
  const colors = [];
  const dummy = new THREE.Object3D();

  for (let yI = 0; yI < sampleCount; yI++) {
    for (let uI = 0; uI < sampleCount; uI++) {
      for (let vI = 0; vI < sampleCount; vI++) {
        const Y = yI * spacing;
        const U = uI * spacing - 0.5;
        const V = vI * spacing - 0.5;

        var rgb = yuvToRgb(Y, U, V);
        if (
          rgb.r < 0 ||
          rgb.r > 1 ||
          rgb.g < 0 ||
          rgb.g > 1 ||
          rgb.b < 0 ||
          rgb.b > 1
        ) {
          continue;
        }

        rgb = linearToSrgb(rgb);
        dummy.position.set(U + 0.5, V + 0.5, Y);
        dummy.updateMatrix();
        matrices.push(dummy.matrix.clone());
        colors.push(rgb.r, rgb.g, rgb.b);
      }
    }
  }

  const mesh = new THREE.InstancedMesh(geo, mat, matrices.length);
  mesh.instanceColor = new THREE.InstancedBufferAttribute(
    new Float32Array(colors),
    3
  );
  matrices.forEach((m, idx) => mesh.setMatrixAt(idx, m));
  content.add(mesh);

  // === YUV axes ===
  const max = 1.05;

  // U axis
  {
    const p0 = new THREE.Vector3(0, 0.5, 0);
    const p1 = new THREE.Vector3(max, 0.5, 0);
    const geom = new THREE.BufferGeometry().setFromPoints([p0, p1]);
    content.add(
      new THREE.Line(geom, new THREE.LineBasicMaterial({ color: 0xff0000 }))
    );
    const uLabel = createLabel("U", "#ff0000");
    uLabel.position.set(max + 0.05, 0.5, 0);
    content.add(uLabel);
  }

  // V axis
  {
    const p0 = new THREE.Vector3(0.5, 0, 0);
    const p1 = new THREE.Vector3(0.5, max, 0);
    const geom = new THREE.BufferGeometry().setFromPoints([p0, p1]);
    content.add(
      new THREE.Line(geom, new THREE.LineBasicMaterial({ color: 0x00ff00 }))
    );
    const vLabel = createLabel("V", "#00ff00");
    vLabel.position.set(0.5, max + 0.05, 0);
    content.add(vLabel);
  }

  // Y axis (through center of UV plane)
  {
    const p0 = new THREE.Vector3(0.5, 0.5, 0);
    const p1 = new THREE.Vector3(0.5, 0.5, max);
    const geom = new THREE.BufferGeometry().setFromPoints([p0, p1]);
    content.add(
      new THREE.Line(geom, new THREE.LineBasicMaterial({ color: 0x0000ff }))
    );
    const yLabel = createLabel("Y", "#0000ff");
    yLabel.position.set(0.5, 0.5, max + 0.05);
    content.add(yLabel);
  }
}
