export const sortByLabel = <T extends { [key: string]: string }>(
  list: T[]
): T[] => {
  // we keep sort over toSorted for compatibilities issues
  list.sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  return list
}
