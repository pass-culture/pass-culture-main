import { IMAGE_RESIZING_URL, IS_DEV } from '@/commons/utils/config'

export const resizeImageURL = ({
  imageURL,
  width,
}: {
  imageURL: string
  width: number
}): string => {
  if (IS_DEV || !IMAGE_RESIZING_URL || !imageURL) {
    return imageURL
  }

  const pixelRatio = window.devicePixelRatio
  const widthWithRatio = width * pixelRatio

  return `${IMAGE_RESIZING_URL}?size=${widthWithRatio}&filename=${imageURL}`
}
