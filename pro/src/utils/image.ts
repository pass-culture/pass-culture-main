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
