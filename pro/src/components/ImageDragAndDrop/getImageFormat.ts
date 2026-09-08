import { filetypemime } from 'magic-bytes.js'

import { ALLOWED_IMAGE_TYPES_TO_EXTENSIONS } from './constants'

const SUPPORTED_MIME_TYPES = new Set(
  Object.keys(ALLOWED_IMAGE_TYPES_TO_EXTENSIONS)
)

export const getImageFormat = (content: ArrayBuffer): string | null => {
  const detectedMimeTypes = filetypemime(new Uint8Array(content))

  return (
    detectedMimeTypes.find((mimeType) => SUPPORTED_MIME_TYPES.has(mimeType)) ??
    null
  )
}
