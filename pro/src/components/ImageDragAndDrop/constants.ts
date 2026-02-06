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
