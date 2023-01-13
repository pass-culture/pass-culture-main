// FIXME: find a way to test FileReader
export const imageFileToDataUrl = (
  image: File,
  onLoad: (imageUrl: string) => void
) => {
  const reader = new FileReader()
  reader.addEventListener(
    'load',
    () => {
      onLoad(reader.result as string)
      return Promise.resolve()
    },
    false
  )
  reader.readAsDataURL(image)
}
