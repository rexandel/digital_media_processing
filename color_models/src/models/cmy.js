import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

export default function buildCMYModel(content, geo, mat, sampleCount, spacing) {
  const count = sampleCount * sampleCount * sampleCount;
  const mesh = new THREE.InstancedMesh(geo, mat, count);
  mesh.instanceColor = new THREE.InstancedBufferAttribute(
    new Float32Array(count * 3),
    3
  );

  const dummy = new THREE.Object3D();
  let i = 0;
  for (let c = 0; c < sampleCount; c++) {
    for (let m = 0; m < sampleCount; m++) {
      for (let y = 0; y < sampleCount; y++) {
        const C = c * spacing,
          M = m * spacing,
          Y = y * spacing;
        // CMY->RGB
        var rgb = {
          r: 1 - C,
          g: 1 - M,
          b: 1 - Y,
        };
        rgb = linearToSrgb(rgb);
        dummy.position.set(C, M, Y);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        mesh.instanceColor.setXYZ(i, rgb.r, rgb.g, rgb.b);
        i++;
      }
    }
  }
  content.add(mesh);

  // axes
  content.add(createAxis(new THREE.Vector3(1.05, 0, 0), 0x00ffff)); // C
  content.add(createAxis(new THREE.Vector3(0, 1.05, 0), 0xff00ff)); // M
  content.add(createAxis(new THREE.Vector3(0, 0, 1.05), 0xffff00)); // Y

  const cL = createLabel("C", "#00ffff");
  const mL = createLabel("M", "#ff00ff");
  const yL = createLabel("Y", "#ffff00");
  cL.position.set(1.1, 0, 0);
  mL.position.set(0, 1.1, 0);
  yL.position.set(0, 0, 1.1);
  content.add(cL, mL, yL);
}
