import { IMAGE_TYPE, MAX_IMAGE_SIZE, MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH } from './_constants'

const isNotAnImage = async file => !IMAGE_TYPE.includes(file.type)
const isTooBig = async file => file.size > MAX_IMAGE_SIZE
const isOfPoorQuality = async file => {
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
  const { height, width } = await createImageBitmap(file)
  return height < MIN_IMAGE_HEIGHT || width < MIN_IMAGE_WIDTH
}

export const constraints = [
  {
    id: 'format',
    description: 'Formats supportés : JPG, PNG',
    validator: isNotAnImage,
  },
  {
    id: 'size',
    description: 'Le poids du fichier ne doit pas dépasser 10 Mo',
    validator: isTooBig,
  },
  {
    id: 'dimensions',
    description: 'La taille de l’image doit être supérieure à 400 x 400px',
    validator: isOfPoorQuality,
  },
]
