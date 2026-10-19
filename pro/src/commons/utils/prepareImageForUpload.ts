import imageCompression from 'browser-image-compression'
import imageCompressionWorkerUrl from 'browser-image-compression/dist/browser-image-compression.js?url'

import {
  MAX_THUMBNAIL_WIDTH,
  MIN_IMAGE_DIMENSIONS,
} from '@/components/ImageDragAndDrop/constants'

import { getImageBitmap } from './image'

export const prepareImageForUpload = async (
  file: File,
  {
    minSizes = MIN_IMAGE_DIMENSIONS,
    cropWidth = 1,
  }: {
    minSizes?: { width: number; height: number }
    cropWidth?: number
  } = {}
): Promise<File> => {
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    return file
  }

  try {
    const bitmap = await getImageBitmap(file)
    if (!bitmap) {
      return file
    }

    const { width, height } = bitmap
    const longestSide = Math.max(width, height)
    bitmap.close?.()

    if (cropWidth <= 0) {
      return file
    }

    // Convert each required width/height into a minimum longest-side size.
    // The crop must retain enough pixels for the backend's 750px thumbnail;
    // the other terms preserve the upload's minimum dimensions.
    const targetDimension = Math.ceil(
      Math.max(
        (MAX_THUMBNAIL_WIDTH / (width * cropWidth)) * longestSide,
        (minSizes.width / width) * longestSide,
        (minSizes.height / height) * longestSide
      )
    )

    if (longestSide <= targetDimension) {
      return file
    }

    const compressed = await imageCompression(file, {
      maxWidthOrHeight: targetDimension,
      initialQuality: 0.85,
      alwaysKeepResolution: true,
      fileType: file.type,
      useWebWorker: true,
      libURL: new URL(imageCompressionWorkerUrl, window.location.href).href,
    })

    if (compressed.size >= file.size) {
      return file
    }

    const compressedBitmap = await getImageBitmap(compressed)
    if (!compressedBitmap) {
      return file
    }

    // Keep the original if compression would increase its size or break minimum dimensions.
    const respectsMinimumDimensions =
      compressedBitmap.width >= minSizes.width &&
      compressedBitmap.height >= minSizes.height
    compressedBitmap.close?.()

    return respectsMinimumDimensions
      ? new File([compressed], file.name, {
          type: compressed.type,
          lastModified: file.lastModified,
        })
      : file
  } catch {
    return file
  }
}
