import type { SelectOption } from '@/commons/custom_types/form'

import { normalizeStrForSearch } from './normalizeStrForSearch'

type SelectOptionNormalized = SelectOption & { normalizedLabel?: string }

export const searchPatternInOptions = (
  options: SelectOptionNormalized[],
  pattern: string,
  maxDisplayedCount?: number
): SelectOptionNormalized[] => {
  const matchingOptions: SelectOptionNormalized[] = []

  for (let i = 0; i < options.length; i++) {
    //  Only search for matches while there are less matches found than max expected results
    if (maxDisplayedCount && matchingOptions.length >= maxDisplayedCount) {
      break
    }

    const normalizedOptionLabel =
      options[i].normalizedLabel ?? normalizeStrForSearch(options[i].label)

    //  Look for options containing all of the pattern words
    const isLabelMatchingPattern = normalizeStrForSearch(pattern || '')
      .split(' ')
      .every((word) => normalizedOptionLabel.includes(word))

    if (isLabelMatchingPattern) {
      matchingOptions.push(options[i])
    }
  }

  return matchingOptions
}
