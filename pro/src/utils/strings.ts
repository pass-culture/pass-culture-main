export const getKey = (text: string): string => {
  return text.toLowerCase().replace(/\s/g, '-')
}
