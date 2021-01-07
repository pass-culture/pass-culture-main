import { IMAGE_TYPE, MAX_IMAGE_SIZE, MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH } from './_constants'

const isNotAnImage = async file => !IMAGE_TYPE.includes(file.type)
const isTooBig = async file => file.size > MAX_IMAGE_SIZE
const isOfPoorQuality = async file => {
  const { height, width } = await createImageBitmap(file)
  return Promise.resolve(height <= MIN_IMAGE_HEIGHT || width <= MIN_IMAGE_WIDTH)
}

export const constraints = [
  {
    id: 'format',
    sentence: 'Formats supportés : JPG, PNG',
    validator: isNotAnImage,
  },
  {
    id: 'size',
    sentence: 'Le poids du fichier ne doit pas dépasser 10 Mo',
    validator: isTooBig,
  },
  {
    id: 'dimensions',
    sentence: 'La taille de l’image doit être supérieure à 400 x 400px',
    validator: isOfPoorQuality,
  },
]
