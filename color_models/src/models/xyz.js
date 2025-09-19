import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

function xyzToRgb(x, y, z) {
  let r = 3.2406 * x - 1.5372 * y - 0.4986 * z;
  let g = -0.9689 * x + 1.8758 * y + 0.0415 * z;
  let b = 0.0557 * x - 0.204 * y + 1.057 * z;
  return { r, g, b };
}

export default function buildXYZModel(content, geo, mat, sampleCount, spacing) {
  const matrices = [];
  const colors = [];
  const dummy = new THREE.Object3D();

  for (let xi = 0; xi < sampleCount; xi++) {
    for (let yi = 0; yi < sampleCount; yi++) {
      for (let zi = 0; zi < sampleCount; zi++) {
        const X = xi * spacing;
        const Y = yi * spacing;
        const Z = zi * spacing;
        var rgb = xyzToRgb(X, Y, Z);
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
        dummy.position.set(X, Y, Z);
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
  matrices.forEach((m, i) => mesh.setMatrixAt(i, m));
  content.add(mesh);

  // axes
  content.add(createAxis(new THREE.Vector3(1.05, 0, 0), 0xff0000)); // X
  content.add(createAxis(new THREE.Vector3(0, 1.05, 0), 0x00ff00)); // Y
  content.add(createAxis(new THREE.Vector3(0, 0, 1.05), 0x0000ff)); // Z

  const xl = createLabel("X", "#ff0000");
  const yl = createLabel("Y", "#00ff00");
  const zl = createLabel("Z", "#0000ff");
  xl.position.set(1.1, 0, 0);
  yl.position.set(0, 1.1, 0);
  zl.position.set(0, 0, 1.1);
  content.add(xl, yl, zl);
}
