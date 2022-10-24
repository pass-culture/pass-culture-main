import { useEffect, useState } from 'react'

/* istanbul ignore next: DEBT, TO FIX */
export const getImageBitmap = async (
  file: File
): Promise<ImageBitmap | null> => {
  // Polyfill for Safari and IE not supporting createImageBitmap
  if (!('createImageBitmap' in window)) {
    window.createImageBitmap = async (
      blob: ImageBitmapSource
    ): Promise<ImageBitmap> =>
      new Promise(resolve => {
        const img = document.createElement('img')
        img.addEventListener('load', function () {
          resolve(this as any)
        })
        img.src = URL.createObjectURL(blob as Blob)
      })
  }
  return await createImageBitmap(file).catch(() => null)
}

/* istanbul ignore next: DEBT, TO FIX */
export const useGetImageBitmap = (file: File) => {
  const [width, setWidth] = useState<number>(0)
  const [height, setHeight] = useState<number>(0)

  useEffect(() => {
    getImageBitmap(file).then(data => {
      if (data) {
        setWidth(data.width)
        setHeight(data.height)
      }
    })
  }, [])

  return { width, height }
}
