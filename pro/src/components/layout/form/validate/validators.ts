import { removeWhitespaces } from 'utils/string'

export const parsePostalCode = (value: string | undefined): string | void => {
  if (!value) return value
  removeWhitespaces(value)
    .replace(/[^[0-9]/g, '')
    .substring(0, 5)
}

export const validatePostalCode = (value: string): string | void => {
  const normalizedValue = parsePostalCode(value)
  normalizedValue !== value
  return value && value.length !== 5 ? 'Code postal invalide' : undefined
}
