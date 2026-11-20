import pica from 'pica'

import {
  MAX_THUMBNAIL_WIDTH,
  MIN_IMAGE_DIMENSIONS,
} from '@/commons/utils/imageUpload/constants'

import { getImageBitmap } from './image'

const imageResizer = pica()

export const prepareImageForUpload = async (
  file: File,
  {
    minSizes,
    cropWidth = 1,
  }: {
    minSizes?: { width: number; height: number }
    cropWidth?: number
  } = {}
): Promise<File | undefined> => {
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    return file
  }

  let bitmap: ImageBitmap | null = null
  try {
    bitmap = await getImageBitmap(file)
    if (!bitmap) {
      return file
    }

    const { width, height } = bitmap

    if (minSizes && (width < minSizes.width || height < minSizes.height)) {
      return
    }
    const longestSide = Math.max(width, height)

    if (cropWidth <= 0) {
      return file
    }

    // Convert each required width/height into a minimum longest-side size.
    // The crop must retain enough pixels for the backend's 750px thumbnail;
    // the other terms preserve the upload's minimum dimensions.
    const thumbMinSizes = minSizes ?? MIN_IMAGE_DIMENSIONS
    const targetDimension = Math.ceil(
      Math.max(
        (MAX_THUMBNAIL_WIDTH / (width * cropWidth)) * longestSide,
        (thumbMinSizes.width / width) * longestSide,
        (thumbMinSizes.height / height) * longestSide
      )
    )

    if (longestSide <= targetDimension) {
      return file
    }

    const scale = targetDimension / longestSide
    const canvas = document.createElement('canvas')
    canvas.width = Math.ceil(width * scale)
    canvas.height = Math.ceil(height * scale)

    await imageResizer.resize(bitmap, canvas)
    const compressed = await imageResizer.toBlob(canvas, file.type, 0.85)

    if (compressed.size >= file.size || compressed.type !== file.type) {
      return file
    }

    const compressedFile = new File([compressed], file.name, {
      type: compressed.type,
      lastModified: file.lastModified,
    })
    const compressedBitmap = await getImageBitmap(compressedFile)
    if (!compressedBitmap) {
      return file
    }

    // Keep the original if compression would increase its size or break minimum dimensions.
    const respectsMinimumDimensions = minSizes
      ? compressedBitmap.width >= minSizes.width &&
        compressedBitmap.height >= minSizes.height
      : false
    compressedBitmap.close?.()

    return respectsMinimumDimensions ? compressedFile : file
  } catch {
    return file
  } finally {
    bitmap?.close?.()
  }
}
