export const getDataURLFromImageURL = async (
  imageURL: string
): Promise<File> => {
  const response = await fetch(imageURL)
  const blob = await response.blob()
  return new File([blob], 'image.jpg', { type: blob.type })
}
