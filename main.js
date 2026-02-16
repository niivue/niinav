import './style.css'
import { Niivue, SLICE_TYPE, SHOW_RENDER, MULTIPLANAR_TYPE } from '@niivue/niivue'
import { Niimath } from '@niivue/niimath'
import { mat3, vec3 } from 'gl-matrix'

async function main() {
  async function addVolumeFromFiles(f) {
    console.log('attempting to open ', f[0].name)
    console.log('details', f[0])
    while (nv.volumes.length > 1) {
      nv.removeVolume(nv.volumes[1])
    }
    await nv.loadFromFile(f[0])
    nv.setColormap(nv.volumes[1].id, 'green2cyan');
  }
  openBtn.onclick = function () {
    let input = document.createElement('input')
    input.style.display = 'none'
    input.type = 'file'
    document.body.appendChild(input)
    input.onchange = function (event) {
      addVolumeFromFiles(event.target.files)
    }
    input.click()
  }
  aboutBtn.onclick = function () {
    window.alert(
      "NiiNav shows scalp locations."
    )
  }
  shaderSelect.onchange = function () {
    nv.setMeshShader(1, shaderSelect.value)
  }
  const meshList = [{ url: './standard_1005.jcon' }, { url: './scalp.mz3' }]
  async function handleImageLoaded(data) {
    return
    if (nv.volumes.length < 2) {
      return
    }
    await nv.loadMeshes(meshList)
    nv.setMeshShader(0, "Rim")
    nv.setMeshShader(1, "Silhouette")
    //nv.setMeshShader(1, "Outline")
  }
  var nv = new Niivue({
    show3Dcrosshair: true,
    backColor: [1, 1, 1, 1],
    onImageLoaded: handleImageLoaded,
  })
  await nv.attachTo("gl")
  let shaders = nv.meshShaderNames()
  console.log(`..`, shaders)
  for (const shader of nv.meshShaderNames()) {
    const option = document.createElement('option')
    option.value = shader
    option.textContent = shader.charAt(0).toUpperCase() + shader.slice(1)
    shaderSelect.appendChild(option)
  }

  nv.setSliceType(nv.sliceTypeRender)
  nv.opts.multiplanarShowRender = SHOW_RENDER.ALWAYS
  nv.opts.meshXRay = 0.2
  const volumeList = [{ url: './mni152.nii.gz' }, { url: './lesion.nii.gz', colormap: "green2cyan"}]
  await nv.loadVolumes(volumeList)
    await nv.loadMeshes(meshList)
    nv.setMeshShader(0, "Rim")
    nv.setMeshShader(1, "Silhouette")

}

main()
