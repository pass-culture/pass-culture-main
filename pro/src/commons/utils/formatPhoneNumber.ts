import parsePhoneNumberFromString, {
  type NumberFormat,
} from 'libphonenumber-js/max'

export const formatPhoneNumber = (
  value: string | null | undefined,
  format: NumberFormat = 'INTERNATIONAL'
): string => {
  if (!value) {
    return ''
  }

  try {
    const parsedPhone = parsePhoneNumberFromString(value, 'FR')
    return parsedPhone?.format(format) ?? value
  } catch {
    return value
  }
}
