import {
  IMAGE_TYPE,
  MAX_IMAGE_SIZE,
  MIN_IMAGE_HEIGHT,
  MIN_IMAGE_WIDTH,
} from './_constants'

const getImageBitmap = async file => {
  // Polyfill for Safari and IE not supporting createImageBitmap
  if (!('createImageBitmap' in window)) {
    window.createImageBitmap = async blob =>
      new Promise(resolve => {
        const img = document.createElement('img')
        img.addEventListener('load', function () {
          resolve(this)
        })
        img.src = URL.createObjectURL(blob)
      })
  }
  return await createImageBitmap(file).catch(() => null)
}
const isNotAnImage = async file =>
  !IMAGE_TYPE.includes(file.type) || (await getImageBitmap(file)) === null
const isTooBig = file => file.size > MAX_IMAGE_SIZE
const isOfBadProportions = () => false
const isOfPoorQuality = async file => {
  const imageBitmap = await getImageBitmap(file)
  return (
    imageBitmap !== null &&
    (imageBitmap.height < MIN_IMAGE_HEIGHT ||
      imageBitmap.width < MIN_IMAGE_WIDTH)
  )
}

export const constraints = [
  {
    id: 'format',
    description: 'Formats de fichier supportés : JPG, PNG',
    asyncValidator: isNotAnImage,
  },
  {
    id: 'size',
    description: 'Poids maximal du fichier : 10 Mo',
    validator: isTooBig,
  },
  {
    id: 'proportions',
    description: 'Proportions de l’image : 2/3 (portrait)',
    validator: isOfBadProportions,
  },
  {
    id: 'dimensions',
    description: 'Largeur minimale de l’image : 400 px',
    asyncValidator: isOfPoorQuality,
  },
]
