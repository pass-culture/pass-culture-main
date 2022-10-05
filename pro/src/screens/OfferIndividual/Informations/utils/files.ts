// FIXME: find a way to test FileReader
/* istanbul ignore next: DEBT, TO FIX */
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
