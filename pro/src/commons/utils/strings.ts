export const sortByLabel = <T extends { [key: string]: string }>(
  list: T[]
  // expect sonar cloud error, we keep sort over toSorted for compatibilities issues
): T[] => list.sort((a, b) => a.label.localeCompare(b.label, 'fr'))
