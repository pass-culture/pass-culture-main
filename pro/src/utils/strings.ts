export const getKey = (text: string): string => {
  return text.toLowerCase().replace(/\s/g, '-')
}

export const sortByDisplayName = <T extends { [key: string]: string | number }>(
  list: T[]
): T[] =>
  list.sort((a, b) =>
    a.displayName.toString().localeCompare(b.displayName.toString(), 'fr')
  )

export const sortByLabel = <T extends { [key: string]: string }>(
  list: T[]
): T[] => list.sort((a, b) => a.label.localeCompare(b.label, 'fr'))
