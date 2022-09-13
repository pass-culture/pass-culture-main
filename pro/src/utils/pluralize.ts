const pluralizeWord = (
  string: string,
  number: number,
  pluralizeWith = 's'
): string => {
  let plural
  let singular
  const lastLetter = string.slice(-1)[0]
  if (lastLetter === 's' || lastLetter === 'x') {
    singular = string.slice(0, -1)
    plural = string
  } else {
    singular = string
    plural = `${string}${pluralizeWith}`
  }
  return number > 1 ? plural : singular
}

export const pluralizeString = (
  string: string,
  number: number,
  pluralizeWith?: string
): string => {
  return string
    .split(' ')
    .map(w => pluralizeWord(w, number, pluralizeWith))
    .join(' ')
}

export const pluralize = (
  number: number,
  string: string,
  pluralizeWith?: string
): string => {
  return `${number} ${pluralizeString(string, number, pluralizeWith)}`
}
