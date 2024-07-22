import { SelectOption } from 'custom_types/form'

export type SelectOptionNormalized = SelectOption & { normalizedLabel?: string }

export const normalizeStrForAdressSearch = (str: string): string => {
  return normalizeStrForSearch(str).replace(/[^\w ]/, '')
}

export const normalizeStrForSearch = (str: string): string => {
  return (
    str
      .trim()
      .toLowerCase()
      //  normalizing to NFD Unicode normal form decomposes combined graphemes into the combination of simple ones. The è becomes e +  ̀
      .normalize('NFD')
      //  remove accents
      .replace(/[\u0300-\u036f]/g, '')
  )
}

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
      options[i]!.normalizedLabel ?? normalizeStrForSearch(options[i]!.label)

    //  Look for options containing all of the pattern words
    const isLabelMatchingPattern = normalizeStrForSearch(pattern || '')
      .split(' ')
      .every((word) => normalizedOptionLabel.includes(word))

    if (isLabelMatchingPattern) {
      matchingOptions.push(options[i]!)
    }
  }

  return matchingOptions
}
