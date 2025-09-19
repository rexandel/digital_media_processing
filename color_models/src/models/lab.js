import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

// Lab → XYZ → RGB
function labToRgb(L, a, b) {
  // Lab → XYZ (D65)
  const fy = (L + 16) / 116;
  const fx = fy + a / 500;
  const fz = fy - b / 200;

  const xr = fx ** 3 > 0.008856 ? fx ** 3 : (116 * fx - 16) / 903.3;
  const yr = L > 0.008856 * 903.3 ? ((L + 16) / 116) ** 3 : L / 903.3;
  const zr = fz ** 3 > 0.008856 ? fz ** 3 : (116 * fz - 16) / 903.3;

  const X = xr * 0.95047;
  const Y = yr * 1.0;
  const Z = zr * 1.08883;

  // XYZ → linear RGB
  let r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z;
  let g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z;
  let b_ = 0.0557 * X - 0.204 * Y + 1.057 * Z;
  return { r, g, b: b_ };
}

export default function buildLabModel(content, geo, mat, sampleCount, spacing) {
  const matrices = [],
    colors = [];
  const dummy = new THREE.Object3D();

  for (let iL = 0; iL < sampleCount; iL++) {
    for (let ia = 0; ia < sampleCount; ia++) {
      for (let ib = 0; ib < sampleCount; ib++) {
        const L = iL * spacing * 100;
        const a = ia * spacing * 100 - 50;
        const b = ib * spacing * 100 - 50;

        var rgb = labToRgb(L, a, b);
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
        dummy.position.set(a / 100 + 0.5, b / 100 + 0.5, iL * spacing);
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
  content.add(createAxis(new THREE.Vector3(1.05, 0, 0), 0xff0000)); // a
  content.add(createAxis(new THREE.Vector3(0, 1.05, 0), 0x00ff00)); // b
  content.add(createAxis(new THREE.Vector3(0, 0, 1.05), 0x0000ff)); // L

  const aL = createLabel("a", "#ff0000");
  const bL = createLabel("b", "#00ff00");
  const lL = createLabel("L", "#0000ff");
  aL.position.set(1.1, 0, 0);
  bL.position.set(0, 1.1, 0);
  lL.position.set(0, 0, 1.1);
  content.add(aL, bL, lL);
}
