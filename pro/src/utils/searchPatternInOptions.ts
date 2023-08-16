import { SelectOption } from 'custom_types/form'

const normalizeStr = (str: string): string => {
  return str
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

const isAMatch = (pattern: string, option: SelectOption): boolean => {
  return normalizeStr(pattern)
    .split(' ')
    .every(word => normalizeStr(option.label).includes(word))
}

export const searchPatternInOptions = (
  options: SelectOption[],
  pattern: string
): SelectOption[] => {
  if (!pattern?.trim()) {
    return options
  }

  //  Filter options containing all of the pattern words
  const matchingOptions = options.filter(option => isAMatch(pattern, option))

  return matchingOptions
}
