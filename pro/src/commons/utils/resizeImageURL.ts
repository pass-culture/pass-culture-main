import { IMAGE_RESIZING_URL, IS_DEV } from '@/commons/utils/config'

export const resizeImageURL = ({
  imageURL,
  width,
  requestImgproxyFormat,
}: {
  imageURL: string
  width: number
  requestImgproxyFormat: boolean
}): string => {
  if (IS_DEV || !IMAGE_RESIZING_URL || !imageURL) {
    return imageURL
  }
  const pixelRatio = window.devicePixelRatio
  const widthWithRatio = width * pixelRatio
  if (requestImgproxyFormat) {
    return `${IMAGE_RESIZING_URL}/insecure/rs:fit:${widthWithRatio}:${widthWithRatio}/plain/gs://${imageURL}`
  } else {
    return `${IMAGE_RESIZING_URL}?size=${widthWithRatio}&filename=${imageURL}`
  }
}
