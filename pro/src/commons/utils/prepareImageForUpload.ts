import pica from 'pica'

import {
  MAX_THUMBNAIL_WIDTH,
  MIN_IMAGE_DIMENSIONS,
} from '@/components/ImageDragAndDrop/constants'

import { getImageBitmap } from './image'

const imageResizer = pica()

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

  let bitmap: ImageBitmap | null = null
  try {
    bitmap = await getImageBitmap(file)
    if (!bitmap) {
      return file
    }

    const { width, height } = bitmap
    const longestSide = Math.max(width, height)

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
    const respectsMinimumDimensions =
      compressedBitmap.width >= minSizes.width &&
      compressedBitmap.height >= minSizes.height
    compressedBitmap.close?.()

    return respectsMinimumDimensions ? compressedFile : file
  } catch {
    return file
  } finally {
    bitmap?.close?.()
  }
}
