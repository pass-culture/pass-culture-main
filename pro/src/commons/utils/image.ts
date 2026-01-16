export const getImageBitmap = async (
  file: File
): Promise<ImageBitmap | null> => {
  // Polyfill for Safari and IE not supporting createImageBitmap
  // https://gist.github.com/nektro/84654b5183ddd1ccb7489607239c982d
  if (!window.createImageBitmap) {
    window.createImageBitmap = (
      blob: ImageBitmapSource
    ): Promise<ImageBitmap> =>
      new Promise((resolve) => {
        const img = document.createElement('img')
        img.addEventListener('load', function () {
          resolve(this as unknown as ImageBitmap)
        })
        img.src = URL.createObjectURL(blob as Blob)
      })
  }

  return await createImageBitmap(file).catch(() => null)
}
