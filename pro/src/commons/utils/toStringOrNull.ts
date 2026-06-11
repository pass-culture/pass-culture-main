export const toStringOrNull = (
  text: string | null | undefined
): string | null => {
  if (!text) {
    return null
  }

  const cleanedText = text.trim()

  return cleanedText || null
}
