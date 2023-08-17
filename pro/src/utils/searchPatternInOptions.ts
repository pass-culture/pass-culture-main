import { SelectOption } from 'custom_types/form'

const normalizeStr = (str: string): string => {
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
  options: SelectOption[],
  pattern: string,
  maxDisplayedCount?: number
): SelectOption[] => {
  //  Filter options containing all of the pattern words
  const matchingOptions = options.filter(option => {
    const normalizedOptionLabel = normalizeStr(option.label)
    return normalizeStr(pattern || '')
      .split(' ')
      .every(word => normalizedOptionLabel.includes(word))
  })

  return matchingOptions.slice(0, maxDisplayedCount ?? options.length)
}
