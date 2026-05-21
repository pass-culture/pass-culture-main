export const removeWhitespaces = (str: string) =>
  str ? str.replace(/\s/g, '') : str

export const truncateAtWord = (
  text: string,
  maxLength: number,
  ending: string = '...'
): string => {
  if (text.trim().length <= maxLength) {
    return text
  }
  let truncated = text.slice(0, maxLength)
  const nextChar = text.charAt(maxLength)
  if (nextChar && nextChar !== ' ') {
    const lastSpace = truncated.lastIndexOf(' ')
    if (lastSpace > 0) {
      truncated = truncated.slice(0, lastSpace)
    }
  }
  return truncated + ending
}
