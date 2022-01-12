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
const isOfPoorQuality = async file => {
  const imageBitmap = await getImageBitmap(file)
  return (
    imageBitmap !== null && (imageBitmap.height < MIN_IMAGE_HEIGHT ||
    imageBitmap.width < MIN_IMAGE_WIDTH)
  )
}

export const constraints = [
  {
    id: 'format',
    description: 'Formats supportés : JPG, PNG',
    asyncValidator: isNotAnImage,
  },
  {
    id: 'size',
    description: 'Le poids du fichier ne doit pas dépasser 10 Mo',
    validator: isTooBig,
  },
  {
    id: 'dimensions',
    description:
      'La taille de l’image doit être au format 6/9, avec une largeur minimale de 400px',
    asyncValidator: isOfPoorQuality,
  },
]
