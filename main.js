import './style.css'
import { Niivue, NVImage, SHOW_RENDER } from '@niivue/niivue'

async function main() {
  const nv = new Niivue({ show3Dcrosshair: true, backColor: [1, 1, 1, 1] })
  await nv.attachTo("gl")
  // State variables
  let brainImg, scalpImg, lesionImg;
  // 1. Unified function to refresh the viewer
  function updateDisplay() {
    const mode = renderMode.selectedIndex;
    while (nv.volumes.length > 0) nv.removeVolume(nv.volumes[0]);
    nv.addVolume(mode > 1 ? brainImg : scalpImg);
    nv.addVolume(lesionImg);
    nv.volumes[1].opacity = (mode % 2 !== 0) ? 1 : 0;
    nv.updateGLVolume();
  }
  // 2. Unified helper for clicking a button to load a file
  function setupFilePicker(btn, onLoaded, colormap = "gray") {
    const input = document.createElement('input');
    input.type = 'file';
    input.style.display = 'none';
    document.body.appendChild(input);
    btn.onclick = () => input.click();
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const img = await NVImage.loadFromFile({ file, colormap });
      onLoaded(img);
      updateDisplay();
    };
  }
  // 3. Assign button behaviors
  setupFilePicker(openBrainBtn, (img) => brainImg = img);
  setupFilePicker(openScalpBtn, (img) => scalpImg = img);
  setupFilePicker(openLesionBtn, (img) => lesionImg = img, "green2cyan");
  // 4. Initial loading
  renderMode.onchange = updateDisplay;
  [scalpImg, brainImg, lesionImg] = await Promise.all([
    NVImage.loadFromUrl({ url: './T1_116.nii.gz' }),
    NVImage.loadFromUrl({ url: './bT1_116.nii.gz' }),
    NVImage.loadFromUrl({ url: './LESION_116.nii.gz', colormap: "green2cyan" })
  ]);
  nv.setSliceType(nv.sliceTypeRender);
  nv.opts.multiplanarShowRender = SHOW_RENDER.ALWAYS;
  nv.opts.meshXRay = 0.05;
  updateDisplay();
  await nv.loadMeshes([{ url: './standard_1005.jcon' }]);
  nv.setMeshShader(0, "Rim");
}

main();