export const getKey = (text: string): string => {
  return text.toLowerCase().replace(/\s/g, '-')
}

export const sortByLabel = <T extends { [key: string]: string }>(
  list: T[]
): T[] =>
  list.sort((a, b) => {
    if (!a.label || !b.label) {
      return 0
    }
    return a.label.localeCompare(b.label, 'fr')
  })
