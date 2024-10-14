export const getKey = (text: string): string => {
  return text.toLowerCase().replace(/\s/g, '-')
}

export const sortByLabel = <T extends { [key: string]: string }>(
  list: T[]
): T[] => list.sort((a, b) => a.label.localeCompare(b.label, 'fr'))
