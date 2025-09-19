import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.166.0/build/three.module.js";
import {createPivotGroup} from "./utils.js";

import buildRGBModel from "./models/rgb.js";
import buildHSVModel from "./models/hsv.js";
import buildHSLModel from "./models/hsl.js";
import buildYUVModel from "./models/yuv.js";
import buildXYZModel from "./models/xyz.js";
import buildLabModel from "./models/lab.js";
import buildOKLabModel from "./models/oklab.js";
import buildCMYModel from "./models/cmy.js";

export default function setupScene(renderer, scene, modelName, shared) {
  let pivot = null;

  const loadModel = (kind) => {
    const prevRot = pivot ? pivot.rotation.clone() : null;
    if (pivot) scene.remove(pivot);

    const { pivot: p, contentGroup } = createPivotGroup();
    pivot = p;
    scene.add(pivot);

    if (prevRot) pivot.rotation.copy(prevRot);

    switch (kind) {
      case "rgb":
        buildRGBModel(contentGroup, ...shared);
        break;
      case "hsv":
        buildHSVModel(contentGroup, ...shared);
        break;
      case "hsl":
        buildHSLModel(contentGroup, ...shared);
        break;
      case "yuv":
        buildYUVModel(contentGroup, ...shared);
        break;
      case "xyz":
        buildXYZModel(contentGroup, ...shared);
        break;
      case "lab":
        buildLabModel(contentGroup, ...shared);
        break;
      case "oklab":
        buildOKLabModel(contentGroup, ...shared);
        break;
      case "cmy":
        buildCMYModel(contentGroup, ...shared);
        break;
    }
  };

  // initial
  loadModel(modelName);

  // rotation
  let isDragging = false;
  let prev = { x: 0, y: 0 };
  renderer.domElement.addEventListener("mousedown", (e) => {
    isDragging = true;
    prev = { x: e.clientX, y: e.clientY };
  });
  window.addEventListener("mouseup", () => (isDragging = false));
  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const dx = e.clientX - prev.x;
    const dy = e.clientY - prev.y;
    if (pivot) {
      pivot.rotation.y += dx * 0.01;
      pivot.rotation.x += dy * 0.01;
    }
    prev = { x: e.clientX, y: e.clientY };
  });

  // expose for dropdown use
  return loadModel;
}
