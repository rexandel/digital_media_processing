import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

// OKLab → RGB
function oklabToRgb(L, a, b) {
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.291485548 * b;

  const l = l_ ** 3,
    m = m_ ** 3,
    s = s_ ** 3;

  let r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
  let g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
  let b_ = -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s;
  return { r, g, b: b_ };
}

export default function buildOKLabModel(
  content,
  geo,
  mat,
  sampleCount,
  spacing
) {
  const matrices = [],
    colors = [];
  const dummy = new THREE.Object3D();

  for (let iL = 0; iL < sampleCount; iL++) {
    for (let ia = 0; ia < sampleCount; ia++) {
      for (let ib = 0; ib < sampleCount; ib++) {
        const L = iL * spacing; // 0..1
        const a = ia * spacing - 0.5;
        const b = ib * spacing - 0.5;

        var rgb = oklabToRgb(L, a, b);
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
        dummy.position.set(a + 0.5, b + 0.5, L);
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
