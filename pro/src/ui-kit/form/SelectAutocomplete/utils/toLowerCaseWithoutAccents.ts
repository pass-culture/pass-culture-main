export const toLowerCaseWithoutAccents = (value?: string): string => {
  if (!value) return ''

  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}
