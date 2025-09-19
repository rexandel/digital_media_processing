import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createAxis, createLabel, linearToSrgb} from "../utils.js";

export default function buildRGBModel(
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

  let i = 0;
  const dummy = new THREE.Object3D();
  for (let x = 0; x < sampleCount; x++) {
    for (let y = 0; y < sampleCount; y++) {
      for (let z = 0; z < sampleCount; z++) {
        dummy.position.set(x * spacing, y * spacing, z * spacing);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        var rgb = { r: x * spacing, g: y * spacing, b: z * spacing };
        rgb = linearToSrgb(rgb);
        mesh.instanceColor.setXYZ(i, rgb.r, rgb.g, rgb.b);
        i++;
      }
    }
  }
  content.add(mesh);

  content.add(createAxis(new THREE.Vector3(1.05, 0, 0), 0xff0000));
  content.add(createAxis(new THREE.Vector3(0, 1.05, 0), 0x00ff00));
  content.add(createAxis(new THREE.Vector3(0, 0, 1.05), 0x0000ff));

  const r = createLabel("R", "#ff0000");
  const g = createLabel("G", "#00ff00");
  const b = createLabel("B", "#0000ff");
  r.position.set(1.1, 0, 0);
  g.position.set(0, 1.1, 0);
  b.position.set(0, 0, 1.1);
  content.add(r, g, b);
}
