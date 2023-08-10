import { SelectOption } from 'custom_types/form'

const normalizeStr = (str: string): string => {
  return str
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

const getNormalizedMatches = (
  pattern: string,
  option: SelectOption
): string[] => {
  return normalizeStr(option.label)
    .split(' ')
    .filter(word =>
      normalizeStr(pattern)
        .split(' ')
        .some(patternWord => word.includes(patternWord))
    )
}

export const searchPatternInOptions = (
  options: SelectOption[],
  pattern: string
): SelectOption[] => {
  if (!pattern?.trim()) {
    return options
  }

  //  Filter options containing at least one word matching one word from the pattern
  const matchingOptions = options.filter(
    option => getNormalizedMatches(pattern, option).length > 0
  )

  if (normalizeStr(pattern).split(' ').length > 1) {
    //  Sort result by number of label words that have matched some of the pattern words
    matchingOptions.sort((opt1, opt2) =>
      getNormalizedMatches(pattern, opt1).length >
      getNormalizedMatches(pattern, opt2).length
        ? -1
        : 1
    )
  }

  return matchingOptions
}
