import { getConditionsText } from '@/design-system/UploadZone/utils'

import {
  ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
  MAX_FILE_SIZE,
  UPLOAD_IMAGE_MAX_RESOLUTION,
} from './constants'
import { getImageDimensions } from './getImageDimensions'
import { getImageFormat } from './getImageFormat'

type ImageMinSizes = { width: number; height: number }

const IMAGE_FORMAT_ERROR = 'Le format de l’image n’est pas valide'
const IMAGE_RESOLUTION_ERROR =
  "Image trop volumineuse. La résolution maximale acceptée est d'environ 80 millions de pixels (9000 x 9000 pixels)"

/**
 * Help text of an image `UploadZone`, listing the conditions checked by the zone
 * (format, weight) and by `validateImage` (resolution, minimum dimensions).
 */
export const getImageConditionsText = (minSizes?: ImageMinSizes): string => {
  const conditions = [
    getConditionsText(ALLOWED_IMAGE_TYPES_TO_EXTENSIONS, MAX_FILE_SIZE),
    'Résolution maximale : 80 mégapixels.',
  ]
  if (minSizes) {
    conditions.push(
      `Largeur minimale : ${minSizes.width} px.`,
      `Hauteur minimale : ${minSizes.height} px.`
    )
  }
  return conditions.join(' ')
}

/**
 * `UploadZone` only checks the declared type and the weight of the file:
 * the actual content format, the resolution and the minimum dimensions are checked here.
 * The returned image carries its dimensions, used by the image edition modal.
 */
export const validateImage = async (
  file: File,
  minSizes?: ImageMinSizes
): Promise<
  { image: File; error?: never } | { image?: never; error: string }
> => {
  try {
    const content = await file.arrayBuffer()
    const { width, height } = await getImageDimensions(file)

    if (getImageFormat(content) === null) {
      return { error: IMAGE_FORMAT_ERROR }
    }
    if (width * height > UPLOAD_IMAGE_MAX_RESOLUTION) {
      return { error: IMAGE_RESOLUTION_ERROR }
    }
    if (minSizes && (width < minSizes.width || height < minSizes.height)) {
      return {
        error: `L’image doit faire au moins ${minSizes.width} pixels de large et ${minSizes.height} pixels de haut`,
      }
    }

    const image = new File([content], file.name, { type: file.type })
    return { image: Object.assign(image, { width, height }) }
  } catch {
    return { error: IMAGE_FORMAT_ERROR }
  }
}
