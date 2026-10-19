const ALLOWED_IMAGE_TYPES = [
  {
    mime: 'image/jpeg',
    extensions: ['.jpeg', '.jpg'],
  },
  {
    mime: 'image/png',
    extensions: ['.png'],
  },
  {
    mime: 'image/mpo',
    extensions: ['.mpo'],
  },
  {
    mime: 'image/webp',
    extensions: ['.webp'],
  },
]

export const ALLOWED_IMAGE_TYPES_TO_EXTENSIONS = Object.fromEntries(
  ALLOWED_IMAGE_TYPES.map(({ mime, extensions }) => [mime, extensions])
)

export const UPLOAD_IMAGE_MAX_RESOLUTION = 80_000_000

export const MAX_FILE_SIZE = 10_000_000

export const MAX_THUMBNAIL_WIDTH = 750

export const MIN_IMAGE_DIMENSIONS = { width: 400, height: 400 }

export const MIN_COLLECTIVE_IMAGE_DIMENSIONS = { width: 400, height: 600 }
