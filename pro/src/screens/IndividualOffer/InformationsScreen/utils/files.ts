export const imageFileToDataUrl = (image: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.addEventListener(
      'load',
      () => {
        resolve(reader.result as string)
      },
      false
    )
    reader.addEventListener(
      'error',
      () => reject(new Error('Unable to read file', { cause: reader.error })),
      false
    )
    reader.readAsDataURL(image)
  })
}
